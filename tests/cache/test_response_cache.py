"""Tests for thegent.cache.response_cache — ResponseCache.

FR traceability: FR-CACHE-002 (LLM response caching)

Traces to: FR-CACHE-002
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from thegent.cache.response_cache import (
    ResponseCache,
    configure_default_cache,
    get_default_cache,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cache(tmp_path) -> ResponseCache:
    """Return an enabled ResponseCache backed by a temp directory."""
    return ResponseCache(
        cache_dir=str(tmp_path / "resp_cache"),
        l1_ttl=60.0,
        l2_ttl=3600.0,
    )


@pytest.fixture
def disabled_cache(tmp_path) -> ResponseCache:
    """Return a disabled ResponseCache (bypass mode / --no-cache)."""
    return ResponseCache(enabled=False, cache_dir=str(tmp_path / "resp_cache_disabled"))


SAMPLE_MESSAGES: list[dict[str, Any]] = [
    {"role": "user", "content": "What is 2+2?"},
]

SAMPLE_RESPONSE: dict[str, Any] = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "choices": [{"message": {"role": "assistant", "content": "4"}}],
    "model": "gpt-4o",
}


# ---------------------------------------------------------------------------
# FR-CACHE-002 — make_key is deterministic
# ---------------------------------------------------------------------------


class TestMakeKey:
    """FR-CACHE-002: Cache key derivation is stable and deterministic."""

    def test_same_inputs_produce_same_key(self):
        """Identical arguments must produce the same key."""
        k1 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        k2 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        assert k1 == k2

    def test_different_model_produces_different_key(self):
        """Changing the model must change the key."""
        k1 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        k2 = ResponseCache.make_key(
            model="claude-opus-4-6", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        assert k1 != k2

    def test_different_temperature_produces_different_key(self):
        """Changing the temperature must change the key."""
        k1 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        k2 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.7
        )
        assert k1 != k2

    def test_different_messages_produce_different_key(self):
        """Changing the messages must change the key."""
        k1 = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        k2 = ResponseCache.make_key(
            model="gpt-4o",
            messages=[{"role": "user", "content": "What is 3+3?"}],
            temperature=0.0,
        )
        assert k1 != k2

    def test_key_is_64_char_hex(self):
        """Key should be a 64-character hex SHA-256 digest."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_extra_fields_affect_key(self):
        """Extra fields (max_tokens, system) must be incorporated in the key."""
        k_base = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        k_extra = ResponseCache.make_key(
            model="gpt-4o",
            messages=SAMPLE_MESSAGES,
            temperature=0.0,
            extra={"max_tokens": 512},
        )
        assert k_base != k_extra


# ---------------------------------------------------------------------------
# FR-CACHE-002 — get / set / miss / hit lifecycle
# ---------------------------------------------------------------------------


class TestGetSetLifecycle:
    """FR-CACHE-002: Basic cache read/write lifecycle."""

    def test_get_returns_none_on_miss(self, cache: ResponseCache):
        """Cache miss must return None."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        assert cache.get(key) is None

    def test_set_then_get_returns_value(self, cache: ResponseCache):
        """Value stored via set must be retrievable with get."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        cache.set(key, SAMPLE_RESPONSE)
        result = cache.get(key)
        assert result == SAMPLE_RESPONSE

    def test_invalidate_removes_entry(self, cache: ResponseCache):
        """Invalidated key must no longer be retrievable."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        cache.set(key, SAMPLE_RESPONSE)
        deleted = cache.invalidate(key)
        assert deleted is True
        assert cache.get(key) is None

    def test_invalidate_returns_false_for_missing_key(self, cache: ResponseCache):
        """Invalidating a non-existent key must return False."""
        assert cache.invalidate("nonexistent" * 4) is False

    def test_clear_removes_all_entries(self, cache: ResponseCache):
        """clear() must purge all stored entries."""
        for i in range(3):
            key = ResponseCache.make_key(
                model="gpt-4o",
                messages=[{"role": "user", "content": str(i)}],
                temperature=0.0,
            )
            cache.set(key, {"answer": i})

        cache.clear()

        for i in range(3):
            key = ResponseCache.make_key(
                model="gpt-4o",
                messages=[{"role": "user", "content": str(i)}],
                temperature=0.0,
            )
            assert cache.get(key) is None


# ---------------------------------------------------------------------------
# FR-CACHE-002 — disabled cache (bypass / --no-cache)
# ---------------------------------------------------------------------------


class TestDisabledCache:
    """FR-CACHE-002: Disabled cache must be a transparent no-op."""

    def test_get_always_returns_none(self, disabled_cache: ResponseCache):
        """Disabled cache get must always return None."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        disabled_cache.set(key, SAMPLE_RESPONSE)  # should silently no-op
        assert disabled_cache.get(key) is None

    def test_set_is_noop(self, disabled_cache: ResponseCache):
        """set() on a disabled cache must not raise."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        disabled_cache.set(key, SAMPLE_RESPONSE)  # must not raise

    def test_invalidate_returns_false(self, disabled_cache: ResponseCache):
        """invalidate() on a disabled cache must return False."""
        key = ResponseCache.make_key(
            model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0
        )
        assert disabled_cache.invalidate(key) is False

    def test_clear_is_noop(self, disabled_cache: ResponseCache):
        """clear() on a disabled cache must not raise."""
        disabled_cache.clear()  # must not raise

    def test_stats_reports_disabled(self, disabled_cache: ResponseCache):
        """Stats for a disabled cache must report enabled=False."""
        stats = disabled_cache.stats()
        assert stats["enabled"] is False


# ---------------------------------------------------------------------------
# FR-CACHE-002 — stats
# ---------------------------------------------------------------------------


class TestStats:
    """FR-CACHE-002: Stats are populated after cache use."""

    def test_stats_has_enabled_key(self, cache: ResponseCache):
        stats = cache.stats()
        assert "enabled" in stats
        assert stats["enabled"] is True


# ---------------------------------------------------------------------------
# FR-CACHE-002 — module-level singleton helpers
# ---------------------------------------------------------------------------


class TestModuleSingleton:
    """FR-CACHE-002: configure_default_cache and get_default_cache work correctly."""

    def test_configure_disables_cache(self, tmp_path):
        """configure_default_cache(enabled=False) must return a disabled cache."""
        configure_default_cache(enabled=False, cache_dir=str(tmp_path / "singleton"))
        default = get_default_cache()
        assert default.enabled is False

    def test_configure_enables_cache(self, tmp_path):
        """configure_default_cache() with defaults must return an enabled cache."""
        configure_default_cache(
            enabled=True, cache_dir=str(tmp_path / "singleton_enabled")
        )
        default = get_default_cache()
        assert default.enabled is True

    def test_get_default_cache_returns_same_instance(self, tmp_path):
        """get_default_cache() must return the same object on repeated calls."""
        configure_default_cache(
            enabled=True, cache_dir=str(tmp_path / "singleton_same")
        )
        a = get_default_cache()
        b = get_default_cache()
        assert a is b


# ---------------------------------------------------------------------------
# FR-CACHE-002 — CliproxyHTTPClient cache integration
# ---------------------------------------------------------------------------


class TestCliproxyHTTPClientCacheIntegration:
    """FR-CACHE-002: CliproxyHTTPClient reads from and writes to ResponseCache."""

    @pytest.mark.asyncio
    async def test_cache_hit_skips_backend(self, tmp_path):
        """When cache has an entry, proxy_request must NOT call the backend."""
        from thegent.adapters.driven.cliproxy_http import CliproxyHTTPClient
        from thegent.cache.response_cache import ResponseCache

        rc = ResponseCache(cache_dir=str(tmp_path / "http_cache"))
        body_payload = {
            "model": "gpt-4o",
            "messages": SAMPLE_MESSAGES,
            "temperature": 0.0,
        }
        import orjson
        body_bytes = orjson.dumps(body_payload)

        key = rc.make_key(
            model="gpt-4o",
            messages=SAMPLE_MESSAGES,
            temperature=0.0,
        )
        rc.set(key, SAMPLE_RESPONSE)

        client = CliproxyHTTPClient(
            backend_url="http://localhost:9999",
            response_cache=rc,
        )

        # No actual HTTP request should be made — patching httpx to confirm.
        with patch("httpx.AsyncClient") as mock_httpx:
            status, resp_body, resp_headers = await client.proxy_request(
                "POST",
                "/v1/chat/completions",
                body=body_bytes,
            )

        mock_httpx.assert_not_called()
        assert status == 200
        assert resp_headers.get("X-Cache") == "HIT"
        assert orjson.loads(resp_body) == SAMPLE_RESPONSE

    @pytest.mark.asyncio
    async def test_cache_miss_calls_backend_and_stores(self, tmp_path):
        """On cache miss proxy_request must call the backend and populate cache."""
        from thegent.adapters.driven.cliproxy_http import CliproxyHTTPClient
        from thegent.cache.response_cache import ResponseCache
        import orjson

        rc = ResponseCache(cache_dir=str(tmp_path / "http_cache_miss"))

        body_payload = {
            "model": "gpt-4o",
            "messages": SAMPLE_MESSAGES,
            "temperature": 0.0,
        }
        body_bytes = orjson.dumps(body_payload)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = orjson.dumps(SAMPLE_RESPONSE)
        mock_resp.headers = {"Content-Type": "application/json"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_resp)

        client = CliproxyHTTPClient(
            backend_url="http://localhost:9999",
            response_cache=rc,
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, _, headers = await client.proxy_request(
                "POST",
                "/v1/chat/completions",
                body=body_bytes,
            )

        assert status == 200
        assert headers.get("X-Cache") == "MISS"

        # Second call must be served from cache.
        with patch("httpx.AsyncClient") as mock_httpx2:
            status2, _resp_body2, headers2 = await client.proxy_request(
                "POST",
                "/v1/chat/completions",
                body=body_bytes,
            )

        mock_httpx2.assert_not_called()
        assert status2 == 200
        assert headers2.get("X-Cache") == "HIT"

    @pytest.mark.asyncio
    async def test_streaming_request_bypasses_cache(self, tmp_path):
    @pytest.mark.asyncio
    async def test_streaming_request_bypasses_cache(self, tmp_path):
        """Streaming requests (stream=True) must never be served from cache.

        Verify via the public proxy_request API: a streaming body must never
        produce an X-Cache: HIT header even when the same key was previously
        stored, because streaming responses are not cache-eligible.
        """
        from thegent.adapters.driven.cliproxy_http import CliproxyHTTPClient
        from thegent.cache.response_cache import ResponseCache
        import orjson

        rc = ResponseCache(cache_dir=str(tmp_path / "stream_cache"))
        body_stream = orjson.dumps(
            {"model": "gpt-4o", "messages": SAMPLE_MESSAGES, "stream": True}
        )

        # Seed the cache with a non-streaming key so the cache has data, then
        # confirm the streaming request bypasses it.
        key = rc.make_key(model="gpt-4o", messages=SAMPLE_MESSAGES, temperature=0.0)
        rc.set(key, SAMPLE_RESPONSE)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = orjson.dumps(SAMPLE_RESPONSE)
        mock_resp.headers = {"Content-Type": "application/json"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_resp)

        client = CliproxyHTTPClient(
            backend_url="http://localhost:9999",
            response_cache=rc,
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            _status, _body, headers = await client.proxy_request(
                "POST",
                "/v1/chat/completions",
                body=body_stream,
            )

        # A streaming request must ALWAYS hit the backend (never return HIT).
        mock_client.request.assert_called_once()
        assert headers.get("X-Cache") != "HIT"

    @pytest.mark.asyncio
    async def test_get_request_bypasses_cache(self, tmp_path):
        """Non-POST requests must never be cached.

        Verify via the public proxy_request API: a GET request must always
        reach the backend and must never return X-Cache: HIT.
        """
        from thegent.adapters.driven.cliproxy_http import CliproxyHTTPClient
        from thegent.cache.response_cache import ResponseCache
        import orjson

        rc = ResponseCache(cache_dir=str(tmp_path / "get_cache"))

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = orjson.dumps({"object": "list", "data": []})
        mock_resp.headers = {"Content-Type": "application/json"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_resp)

        client = CliproxyHTTPClient(
            backend_url="http://localhost:9999",
            response_cache=rc,
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            _status, _body, headers = await client.proxy_request(
                "GET",
                "/v1/chat/completions",
                body=b"",
            )

        mock_client.request.assert_called_once()
        assert headers.get("X-Cache") != "HIT"

    @pytest.mark.asyncio
    async def test_non_completion_path_bypasses_cache(self, tmp_path):
        """Non-completion paths must never be cached.

        Verify via the public proxy_request API: a POST to /v1/models must
        always hit the backend and never return X-Cache: HIT.
        """
        from thegent.adapters.driven.cliproxy_http import CliproxyHTTPClient
        from thegent.cache.response_cache import ResponseCache
        import orjson

        rc = ResponseCache(cache_dir=str(tmp_path / "models_cache"))
        body = orjson.dumps({"model": "gpt-4o"})

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = orjson.dumps({"object": "list", "data": []})
        mock_resp.headers = {"Content-Type": "application/json"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_resp)

        client = CliproxyHTTPClient(
            backend_url="http://localhost:9999",
            response_cache=rc,
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            _status, _body, headers = await client.proxy_request(
                "POST",
                "/v1/models",
                body=body,
            )

        mock_client.request.assert_called_once()
        assert headers.get("X-Cache") != "HIT"
