"""Tests for Redis-backed distributed concurrency limits.

@trace FR-ORC-002 (swarm-redis-concurrency)
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegent.orchestration.redis_concurrency import (
    RedisConcurrencyController,
    RedisConfig,
    _InMemoryStore,
    make_redis_concurrency_controller,
)

# ---------------------------------------------------------------------------
# RedisConfig tests
# ---------------------------------------------------------------------------


class TestRedisConfig:
    """Tests for RedisConfig dataclass."""

    def test_defaults(self) -> None:  # @trace FR-ORC-002
        cfg = RedisConfig()
        assert cfg.host == "localhost"
        assert cfg.port == 6379
        assert cfg.db == 0
        assert cfg.password is None
        assert cfg.key_prefix == "thgent:concurrency"

    def test_from_env_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:  # @trace FR-ORC-002
        monkeypatch.delenv("THGENT_REDIS_HOST", raising=False)
        monkeypatch.delenv("THGENT_REDIS_PORT", raising=False)
        monkeypatch.delenv("THGENT_REDIS_DB", raising=False)
        monkeypatch.delenv("THGENT_REDIS_PASSWORD", raising=False)
        monkeypatch.delenv("THGENT_REDIS_KEY_PREFIX", raising=False)
        cfg = RedisConfig.from_env()
        assert cfg.host == "localhost"
        assert cfg.port == 6379
        assert cfg.db == 0
        assert cfg.password is None
        assert cfg.key_prefix == "thgent:concurrency"

    def test_from_env_custom(self, monkeypatch: pytest.MonkeyPatch) -> None:  # @trace FR-ORC-002
        monkeypatch.setenv("THGENT_REDIS_HOST", "redis.prod.example.com")
        monkeypatch.setenv("THGENT_REDIS_PORT", "6380")
        monkeypatch.setenv("THGENT_REDIS_DB", "2")
        monkeypatch.setenv("THGENT_REDIS_PASSWORD", "secret")
        monkeypatch.setenv("THGENT_REDIS_KEY_PREFIX", "myapp:cc")
        cfg = RedisConfig.from_env()
        assert cfg.host == "redis.prod.example.com"
        assert cfg.port == 6380
        assert cfg.db == 2
        assert cfg.password == "secret"
        assert cfg.key_prefix == "myapp:cc"

    def test_from_env_empty_password_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:  # @trace FR-ORC-002
        monkeypatch.setenv("THGENT_REDIS_PASSWORD", "")
        cfg = RedisConfig.from_env()
        assert cfg.password is None


# ---------------------------------------------------------------------------
# _InMemoryStore tests
# ---------------------------------------------------------------------------


class TestInMemoryStore:
    """Tests for the in-process fallback store."""

    @pytest.fixture
    def store(self) -> _InMemoryStore:
        return _InMemoryStore()

    @pytest.mark.asyncio
    async def test_setnx_bounded_acquires_when_under_limit(
        self, store: _InMemoryStore
    ) -> None:  # @trace FR-ORC-002
        ok = await store.setnx_bounded("pfx:slot:run1", ttl=60.0, max_count=3)
        assert ok is True

    @pytest.mark.asyncio
    async def test_setnx_bounded_rejects_duplicate_key(
        self, store: _InMemoryStore
    ) -> None:  # @trace FR-ORC-002
        await store.setnx_bounded("pfx:slot:run1", ttl=60.0, max_count=3)
        ok = await store.setnx_bounded("pfx:slot:run1", ttl=60.0, max_count=3)
        assert ok is False

    @pytest.mark.asyncio
    async def test_setnx_bounded_blocks_at_limit(
        self, store: _InMemoryStore
    ) -> None:  # @trace FR-ORC-002
        for i in range(2):
            await store.setnx_bounded(f"pfx:slot:r{i}", ttl=60.0, max_count=2)
        ok = await store.setnx_bounded("pfx:slot:r99", ttl=60.0, max_count=2)
        assert ok is False

    @pytest.mark.asyncio
    async def test_delete_removes_key(self, store: _InMemoryStore) -> None:  # @trace FR-ORC-002
        await store.setnx_bounded("pfx:slot:run1", ttl=60.0, max_count=5)
        await store.delete("pfx:slot:run1")
        count = await store.count_with_prefix("pfx:slot:")
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_noop_missing_key(self, store: _InMemoryStore) -> None:  # @trace FR-ORC-002
        await store.delete("pfx:slot:nonexistent")  # must not raise

    @pytest.mark.asyncio
    async def test_count_with_prefix(self, store: _InMemoryStore) -> None:  # @trace FR-ORC-002
        await store.setnx_bounded("pfx:slot:r1", ttl=60.0, max_count=10)
        await store.setnx_bounded("pfx:slot:r2", ttl=60.0, max_count=10)
        count = await store.count_with_prefix("pfx:slot:")
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_excludes_expired(self, store: _InMemoryStore) -> None:  # @trace FR-ORC-002
        # Manually insert an already-expired entry
        store._active["pfx:slot:old"] = time.monotonic() - 1.0
        store._active["pfx:slot:fresh"] = time.monotonic() + 60.0
        count = await store.count_with_prefix("pfx:slot:")
        assert count == 1

    def test_count_with_prefix_sync(self, store: _InMemoryStore) -> None:  # @trace FR-ORC-002
        store._active["pfx:slot:r1"] = time.monotonic() + 60.0
        store._active["pfx:slot:r2"] = time.monotonic() - 1.0  # expired
        count = store.count_with_prefix_sync("pfx:slot:")
        assert count == 1


# ---------------------------------------------------------------------------
# RedisConcurrencyController — fallback mode (no redis package)
# ---------------------------------------------------------------------------


class TestFallbackMode:
    """Tests for RedisConcurrencyController when redis is not installed."""

    @pytest.fixture
    def ctrl(self, monkeypatch: pytest.MonkeyPatch) -> RedisConcurrencyController:
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=None,
        ):
            return RedisConcurrencyController(
                redis_config=RedisConfig(key_prefix="t:cc"),
                max_concurrent=3,
            )

    def test_is_available_false(self, ctrl: RedisConcurrencyController) -> None:  # @trace FR-ORC-002
        assert ctrl.is_available() is False

    @pytest.mark.asyncio
    async def test_acquire_returns_true_under_limit(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        ok = await ctrl.acquire("run-1", timeout=1.0)
        assert ok is True

    @pytest.mark.asyncio
    async def test_acquire_returns_false_when_at_limit(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        for i in range(3):
            await ctrl.acquire(f"run-{i}", timeout=1.0)
        ok = await ctrl.acquire("run-overflow", timeout=0.1)
        assert ok is False

    @pytest.mark.asyncio
    async def test_release_frees_slot(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        for i in range(3):
            await ctrl.acquire(f"run-{i}", timeout=1.0)
        await ctrl.release("run-0")
        ok = await ctrl.acquire("run-new", timeout=1.0)
        assert ok is True

    @pytest.mark.asyncio
    async def test_release_noop_unknown_run(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.release("nonexistent")  # must not raise

    @pytest.mark.asyncio
    async def test_aget_active_count_correct(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.acquire("run-1", timeout=1.0)
        await ctrl.acquire("run-2", timeout=1.0)
        count = await ctrl.aget_active_count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_alist_active_contains_run_ids(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.acquire("run-alpha", timeout=1.0)
        await ctrl.acquire("run-beta", timeout=1.0)
        active = await ctrl.alist_active()
        assert "run-alpha" in active
        assert "run-beta" in active

    @pytest.mark.asyncio
    async def test_alist_active_empty_initially(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        active = await ctrl.alist_active()
        assert active == []

    @pytest.mark.asyncio
    async def test_acquire_times_out_at_limit(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        for i in range(3):
            await ctrl.acquire(f"run-{i}", timeout=1.0)
        start = time.monotonic()
        ok = await ctrl.acquire("run-late", timeout=0.3)
        elapsed = time.monotonic() - start
        assert ok is False
        assert elapsed < 2.0  # sanity: didn't hang

    def test_get_active_count_sync_outside_loop(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        count = ctrl.get_active_count()
        assert count == 0


# ---------------------------------------------------------------------------
# RedisConcurrencyController — Redis mode with mock
# ---------------------------------------------------------------------------


def _make_mock_redis(existing_keys: list[str] | None = None) -> MagicMock:
    """Create a mock redis.asyncio.Redis instance."""
    r = MagicMock()
    keys_store: list[str] = list(existing_keys or [])

    async def mock_keys(pattern: str) -> list[str]:
        prefix = pattern.rstrip("*")
        return [k for k in keys_store if k.startswith(prefix)]

    async def mock_set(key: str, value: str, *, nx: bool = False, ex: int = 0) -> bool:
        if nx and key in keys_store:
            return False
        keys_store.append(key)
        return True

    async def mock_delete(*keys: str) -> int:
        removed = 0
        for k in keys:
            if k in keys_store:
                keys_store.remove(k)
                removed += 1
        return removed

    r.keys = mock_keys
    r.set = mock_set
    r.delete = mock_delete
    return r


class TestRedisMockMode:
    """Tests for RedisConcurrencyController backed by a mock redis client."""

    @pytest.fixture
    def redis_mock(self) -> MagicMock:
        return _make_mock_redis()

    @pytest.fixture
    def ctrl(self, redis_mock: MagicMock) -> RedisConcurrencyController:
        aioredis_mod = MagicMock()
        aioredis_mod.Redis.return_value = redis_mock
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=aioredis_mod,
        ):
            c = RedisConcurrencyController(
                redis_config=RedisConfig(key_prefix="t:cc"),
                max_concurrent=3,
            )
        # Override the internal redis reference with the mock directly
        c._redis = redis_mock
        c._redis_available = True
        c._fallback = None
        return c

    def test_is_available_true(self, ctrl: RedisConcurrencyController) -> None:  # @trace FR-ORC-002
        assert ctrl.is_available() is True

    @pytest.mark.asyncio
    async def test_acquire_redis_under_limit(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        ok = await ctrl.acquire("run-r1", timeout=1.0)
        assert ok is True

    @pytest.mark.asyncio
    async def test_acquire_redis_at_limit_returns_false(
        self, ctrl: RedisConcurrencyController, redis_mock: MagicMock
    ) -> None:  # @trace FR-ORC-002
        # Pre-populate 3 existing keys so limit is reached
        ctrl._redis = _make_mock_redis(["t:cc:slot:a", "t:cc:slot:b", "t:cc:slot:c"])
        ok = await ctrl.acquire("run-overflow", timeout=0.1)
        assert ok is False

    @pytest.mark.asyncio
    async def test_aget_active_count_redis(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.acquire("run-1", timeout=1.0)
        await ctrl.acquire("run-2", timeout=1.0)
        count = await ctrl.aget_active_count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_release_redis_removes_key(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.acquire("run-1", timeout=1.0)
        await ctrl.release("run-1")
        count = await ctrl.aget_active_count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_alist_active_redis(
        self, ctrl: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl.acquire("run-x", timeout=1.0)
        active = await ctrl.alist_active()
        assert "run-x" in active


# ---------------------------------------------------------------------------
# Fallback on Redis error
# ---------------------------------------------------------------------------


class TestRedisFallbackOnError:
    """Tests that errors in Redis calls trigger fallback to in-memory."""

    @pytest.fixture
    def ctrl_with_broken_redis(self) -> RedisConcurrencyController:
        aioredis_mod = MagicMock()
        bad_redis = MagicMock()
        bad_redis.keys = AsyncMock(side_effect=ConnectionError("redis gone"))
        bad_redis.set = AsyncMock(side_effect=ConnectionError("redis gone"))
        bad_redis.delete = AsyncMock(side_effect=ConnectionError("redis gone"))
        aioredis_mod.Redis.return_value = bad_redis
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=aioredis_mod,
        ):
            c = RedisConcurrencyController(
                redis_config=RedisConfig(key_prefix="t:cc"),
                max_concurrent=3,
            )
        c._redis = bad_redis
        c._redis_available = True
        return c

    @pytest.mark.asyncio
    async def test_acquire_switches_to_fallback_on_error(
        self, ctrl_with_broken_redis: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        ok = await ctrl_with_broken_redis.acquire("run-err", timeout=1.0)
        assert ok is True
        assert ctrl_with_broken_redis.is_available() is False

    @pytest.mark.asyncio
    async def test_is_available_false_after_redis_error(
        self, ctrl_with_broken_redis: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        await ctrl_with_broken_redis.acquire("run-err2", timeout=1.0)
        assert ctrl_with_broken_redis.is_available() is False

    @pytest.mark.asyncio
    async def test_aget_active_count_switches_on_error(
        self, ctrl_with_broken_redis: RedisConcurrencyController
    ) -> None:  # @trace FR-ORC-002
        count = await ctrl_with_broken_redis.aget_active_count()
        assert isinstance(count, int)
        assert ctrl_with_broken_redis.is_available() is False


# ---------------------------------------------------------------------------
# make_redis_concurrency_controller factory
# ---------------------------------------------------------------------------


class TestFactory:
    """Tests for the factory helper."""

    def test_returns_controller_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:  # @trace FR-ORC-002
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=None,
        ):
            ctrl = make_redis_concurrency_controller(max_concurrent=5)
        assert isinstance(ctrl, RedisConcurrencyController)

    def test_max_concurrent_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:  # @trace FR-ORC-002
        monkeypatch.setenv("THGENT_REDIS_CONCURRENCY_LIMIT", "42")
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=None,
        ):
            ctrl = make_redis_concurrency_controller()
        assert ctrl._max_concurrent == 42

    def test_slot_ttl_passed(self, monkeypatch: pytest.MonkeyPatch) -> None:  # @trace FR-ORC-002
        with patch(
            "thegent.orchestration.redis_concurrency._import_redis_asyncio",
            return_value=None,
        ):
            ctrl = make_redis_concurrency_controller(slot_ttl_s=300.0)
        assert ctrl._slot_ttl_s == 300.0
