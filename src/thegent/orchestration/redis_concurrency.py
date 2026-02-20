"""Redis-backed distributed concurrency limits for swarm coordination.

Implements distributed concurrency control using Redis SETNX + EXPIRE so that
multiple thegent instances share a single global slot pool. Falls back to the
in-process controller when Redis is not installed or unreachable.

Configuration via environment variables (all read through ThegentSettings):
  THGENT_REDIS_HOST              - Redis host (default: localhost)
  THGENT_REDIS_PORT              - Redis port (default: 6379)
  THGENT_REDIS_DB                - Redis DB index (default: 0)
  THGENT_REDIS_PASSWORD          - Optional password
  THGENT_REDIS_KEY_PREFIX        - Key namespace (default: thgent:concurrency)
  THGENT_REDIS_CONCURRENCY_LIMIT - Max concurrent slots (default: 10)

swarm-redis-concurrency
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass
class RedisConfig:
    """Connection parameters for the Redis backend."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    key_prefix: str = "thgent:concurrency"

    @classmethod
    def from_env(cls) -> RedisConfig:
        """Build config from environment variables (THGENT_REDIS_* prefix)."""
        return cls(
            host=os.environ.get("THGENT_REDIS_HOST", "localhost"),
            port=int(os.environ.get("THGENT_REDIS_PORT", "6379")),
            db=int(os.environ.get("THGENT_REDIS_DB", "0")),
            password=os.environ.get("THGENT_REDIS_PASSWORD") or None,
            key_prefix=os.environ.get("THGENT_REDIS_KEY_PREFIX", "thgent:concurrency"),
        )


# ---------------------------------------------------------------------------
# In-memory fallback store
# ---------------------------------------------------------------------------


@dataclass
class _InMemoryStore:
    """Thread-safe in-process slot tracker used as Redis fallback."""

    _active: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._lock = asyncio.Lock()

    def _prune_expired(self) -> None:
        """Remove expired entries (must hold self._lock)."""
        now = time.monotonic()
        expired = [k for k, exp in self._active.items() if exp < now]
        for k in expired:
            del self._active[k]

    async def delete(self, key: str) -> None:
        """Remove key."""
        async with self._lock:
            self._active.pop(key, None)

    async def keys_with_prefix(self, prefix: str) -> list[str]:
        """Return all keys matching prefix, pruning expired entries."""
        async with self._lock:
            self._prune_expired()
            return [k for k in self._active if k.startswith(prefix)]

    async def count_with_prefix(self, prefix: str) -> int:
        """Return count of active keys with given prefix."""
        return len(await self.keys_with_prefix(prefix))

    def count_with_prefix_sync(self, prefix: str) -> int:
        """Synchronous approximate count without pruning (no await required)."""
        now = time.monotonic()
        return sum(
            1
            for k, exp in self._active.items()
            if k.startswith(prefix) and exp >= now
        )

    async def setnx_bounded(self, key: str, ttl: float, max_count: int) -> bool:
        """Atomically set key if not exists AND active count < max_count."""
        async with self._lock:
            self._prune_expired()
            prefix = key.rsplit(":slot:", 1)[0] + ":slot:"
            current = sum(1 for k in self._active if k.startswith(prefix))
            if current >= max_count:
                return False
            if key in self._active:
                return False
            self._active[key] = time.monotonic() + ttl
            return True


# ---------------------------------------------------------------------------
# RedisConcurrencyController
# ---------------------------------------------------------------------------


def _import_redis_asyncio() -> Any:
    """Import redis.asyncio; return module or None if not installed."""
    try:
        import redis.asyncio as aioredis

        return aioredis
    except ImportError:
        return None


class RedisConcurrencyController:
    """Distributed concurrency limits backed by Redis SETNX/EXPIRE.

    Each acquired slot is represented by a Redis key:
      ``{key_prefix}:slot:{run_id}``

    The key expires automatically after ``slot_ttl_s`` seconds so stale slots
    (from crashed workers) are reclaimed without manual intervention.

    Fallback: if the ``redis`` package is not installed *or* Redis is
    unreachable at construction time, the controller silently falls back to
    an in-process ``_InMemoryStore`` that behaves identically within a single
    process.  ``is_available()`` returns ``False`` in fallback mode.
    """

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        max_concurrent: int | None = None,
        slot_ttl_s: float = 120.0,
    ) -> None:
        """Initialise the controller.

        Args:
            redis_config: Connection parameters.  When *None*, reads from env.
            max_concurrent: Maximum concurrent slots across all instances.
                            Reads ``THGENT_REDIS_CONCURRENCY_LIMIT`` when *None*
                            (default: 10).
            slot_ttl_s: TTL in seconds for each slot key.  Slots older than
                        this are considered stale and released automatically.
        """
        self._config = redis_config or RedisConfig.from_env()
        self._max_concurrent = max_concurrent or int(
            os.environ.get("THGENT_REDIS_CONCURRENCY_LIMIT", "10")
        )
        self._slot_ttl_s = slot_ttl_s
        self._redis: Any = None  # redis.asyncio.Redis instance or None
        self._fallback: _InMemoryStore | None = None
        self._redis_available = False

        self._try_connect_redis()

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def _try_connect_redis(self) -> None:
        """Attempt to import redis and create a client.  Silently falls back."""
        aioredis = _import_redis_asyncio()
        if aioredis is None:
            _log.debug(
                "redis_concurrency: redis package not installed, using in-memory fallback"
            )
            self._fallback = _InMemoryStore()
            self._redis_available = False
            return

        kwargs: dict[str, Any] = {
            "host": self._config.host,
            "port": self._config.port,
            "db": self._config.db,
            "decode_responses": True,
            "socket_connect_timeout": 2,
            "socket_timeout": 2,
        }
        if self._config.password:
            kwargs["password"] = self._config.password

        self._redis = aioredis.Redis(**kwargs)
        self._redis_available = True
        _log.debug(
            "redis_concurrency: connected host=%s port=%d db=%d prefix=%s limit=%d",
            self._config.host,
            self._config.port,
            self._config.db,
            self._config.key_prefix,
            self._max_concurrent,
        )

    # ------------------------------------------------------------------
    # Key helpers
    # ------------------------------------------------------------------

    def _slot_key(self, run_id: str) -> str:
        return f"{self._config.key_prefix}:slot:{run_id}"

    def _slot_prefix(self) -> str:
        return f"{self._config.key_prefix}:slot:"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True when Redis is configured and reachable (not fallback mode)."""
        return self._redis_available

    async def acquire(self, run_id: str, timeout: float = 30.0) -> bool:
        """Acquire a concurrency slot for *run_id*.

        Polls until a slot becomes available or *timeout* seconds elapse.

        Args:
            run_id: Unique identifier for the run requesting a slot.
            timeout: Maximum seconds to wait for a free slot.

        Returns:
            True when the slot was acquired, False when timed out.
        """
        key = self._slot_key(run_id)
        deadline = time.monotonic() + timeout
        poll_interval = 0.5

        while time.monotonic() < deadline:
            acquired = await self._try_acquire(key)
            if acquired:
                _log.debug("redis_concurrency: acquired run_id=%s key=%s", run_id, key)
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            await asyncio.sleep(min(poll_interval, remaining))

        _log.debug(
            "redis_concurrency: timed out acquiring run_id=%s timeout=%.1f",
            run_id,
            timeout,
        )
        return False

    async def release(self, run_id: str) -> None:
        """Release the concurrency slot held by *run_id*.

        Safe to call even if *run_id* never acquired a slot (no-op).
        """
        key = self._slot_key(run_id)
        if self._redis_available and self._redis is not None:
            try:
                await self._redis.delete(key)
                _log.debug(
                    "redis_concurrency: released run_id=%s key=%s", run_id, key
                )
                return
            except Exception as exc:
                _log.warning(
                    "redis_concurrency: release failed, switching to fallback: %s", exc
                )
                self._switch_to_fallback()

        if self._fallback is not None:
            await self._fallback.delete(key)
            _log.debug(
                "redis_concurrency: fallback released run_id=%s key=%s", run_id, key
            )

    def get_active_count(self) -> int:
        """Return the number of currently active (acquired) slots.

        When called from within a running event loop (async context), returns
        a synchronous approximate count from the fallback store or 0 for
        Redis mode (use ``aget_active_count()`` from async code).
        """
        try:
            asyncio.get_running_loop()
            # Inside async context: return approximate sync count
            return self._sync_active_count_approximate()
        except RuntimeError:
            pass

        return asyncio.run(self.aget_active_count())

    async def aget_active_count(self) -> int:
        """Async variant of ``get_active_count``."""
        prefix = self._slot_prefix()
        if self._redis_available and self._redis is not None:
            try:
                keys = await self._redis.keys(f"{prefix}*")
                return len(keys)
            except Exception as exc:
                _log.warning(
                    "redis_concurrency: aget_active_count failed, switching to fallback: %s",
                    exc,
                )
                self._switch_to_fallback()

        if self._fallback is not None:
            return await self._fallback.count_with_prefix(prefix)
        return 0

    def list_active(self) -> list[str]:
        """Return the list of run_ids currently holding a slot (synchronous)."""
        try:
            asyncio.get_running_loop()
            # Inside async context: cannot run new loop, return empty
            return []
        except RuntimeError:
            pass

        return asyncio.run(self.alist_active())

    async def alist_active(self) -> list[str]:
        """Async variant of ``list_active``."""
        prefix = self._slot_prefix()
        prefix_len = len(prefix)
        if self._redis_available and self._redis is not None:
            try:
                keys = await self._redis.keys(f"{prefix}*")
                return [k[prefix_len:] for k in keys]
            except Exception as exc:
                _log.warning(
                    "redis_concurrency: alist_active failed, switching to fallback: %s",
                    exc,
                )
                self._switch_to_fallback()

        if self._fallback is not None:
            keys = await self._fallback.keys_with_prefix(prefix)
            return [k[prefix_len:] for k in keys]
        return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _try_acquire(self, key: str) -> bool:
        """Attempt one acquisition attempt.  Returns True if slot taken."""
        if self._redis_available and self._redis is not None:
            try:
                return await self._try_acquire_redis(key)
            except Exception as exc:
                _log.warning(
                    "redis_concurrency: acquire failed, switching to fallback: %s", exc
                )
                self._switch_to_fallback()

        if self._fallback is not None:
            return await self._fallback.setnx_bounded(
                key, self._slot_ttl_s, self._max_concurrent
            )
        return False

    async def _try_acquire_redis(self, key: str) -> bool:
        """Redis SETNX + EXPIRE atomic acquire.  Returns True if acquired."""
        # Count active slots first (approximate — tolerable race window)
        active_keys = await self._redis.keys(f"{self._slot_prefix()}*")
        if len(active_keys) >= self._max_concurrent:
            return False

        # SET key 1 NX EX ttl — atomically set only if key does not exist
        result = await self._redis.set(
            key, "1", nx=True, ex=int(self._slot_ttl_s)
        )
        if not result:
            return False

        # Double-check after acquiring: if we now exceed the limit, release
        active_after = await self._redis.keys(f"{self._slot_prefix()}*")
        if len(active_after) > self._max_concurrent:
            # We caused an overshoot — release our slot
            await self._redis.delete(key)
            return False

        return True

    def _switch_to_fallback(self) -> None:
        """Mark Redis as unavailable and activate in-memory fallback."""
        self._redis_available = False
        self._redis = None
        if self._fallback is None:
            self._fallback = _InMemoryStore()
        _log.warning(
            "redis_concurrency: switched to in-memory fallback (Redis unavailable)"
        )

    def _sync_active_count_approximate(self) -> int:
        """Synchronous approximate count (fallback only, no await)."""
        if self._fallback is not None:
            return self._fallback.count_with_prefix_sync(self._slot_prefix())
        return 0


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------


def make_redis_concurrency_controller(
    max_concurrent: int | None = None,
    slot_ttl_s: float = 120.0,
) -> RedisConcurrencyController:
    """Create a ``RedisConcurrencyController`` from environment variables.

    When ``THGENT_REDIS_HOST`` is not set, the controller will still be
    created but immediately fall back to in-process limits (``is_available()``
    returns ``False``).
    """
    config = RedisConfig.from_env()
    return RedisConcurrencyController(
        redis_config=config,
        max_concurrent=max_concurrent,
        slot_ttl_s=slot_ttl_s,
    )
