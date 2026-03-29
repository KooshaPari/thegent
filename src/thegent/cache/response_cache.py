"""LLM Response Cache.

Disk-backed cache for LLM completion responses, keyed by a hash of
(model, messages, temperature).  Wraps the existing TieredCache
(L1 in-memory TTL + L2 diskcache SQLite) so that repeated identical
requests are served from cache without a round-trip to the API.

Traces to: FR-CACHE-002
"""

# wraps: diskcache >=5.6.3  (via TieredCache / L2DiskCache)
# wraps: cachetools >=5.5.2  (via TieredCache / L1MemoryCache)

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from thegent.cache.tiered import TieredCache

_log = logging.getLogger(__name__)

_DEFAULT_CACHE_DIR = str(Path.home() / ".thegent" / "cache" / "responses")
_DEFAULT_L1_TTL: float = 60.0  # seconds
_DEFAULT_L2_TTL: float = 3600.0  # seconds (1 hour)
_DEFAULT_L1_MAX_SIZE: int = 512


class ResponseCache:
    """Tiered cache for LLM completion responses.

    Cache key is a SHA-256 hash of the canonical JSON representation of
    (model, sorted-messages, temperature).  Responses are serialised as
    plain dicts so they survive process restarts.

    Usage::

        cache = ResponseCache()
        key = cache.make_key(model="gpt-4o", messages=[...], temperature=0.0)
        cached = cache.get(key)
        if cached is None:
            response = await call_llm(...)
            cache.set(key, response)

    Bypassing the cache::

        cache = ResponseCache(enabled=False)
        # or pass enabled=False at construction, or pass no_cache=True per-call
        key = cache.make_key(...)
        assert cache.get(key) is None  # always misses
    """

    def __init__(
        self,
        *,
        cache_dir: str = _DEFAULT_CACHE_DIR,
        l1_ttl: float = _DEFAULT_L1_TTL,
        l2_ttl: float = _DEFAULT_L2_TTL,
        l1_max_size: int = _DEFAULT_L1_MAX_SIZE,
        enabled: bool = True,
    ) -> None:
        """Initialise the response cache.

        Args:
            cache_dir:    Directory for the L2 disk cache (created on demand).
            l1_ttl:       TTL for the in-memory L1 tier (seconds).
            l2_ttl:       TTL for the disk-backed L2 tier (seconds).
            l1_max_size:  Maximum number of entries in the L1 tier.
            enabled:      When ``False`` all operations are no-ops (cache
                          bypass mode / ``--no-cache`` flag).
        """
        self.enabled = enabled
        self._tiered: TieredCache | None = None

        if enabled:
            self._tiered = TieredCache(
                l1_ttl=l1_ttl,
                l2_ttl=l2_ttl,
                l1_max_size=l1_max_size,
                l2_cache_dir=cache_dir,
            )

    # ------------------------------------------------------------------
    # Key construction
    # ------------------------------------------------------------------

    @staticmethod
    def make_key(
        *,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 1.0,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Compute a deterministic cache key.

        The key is the hex SHA-256 digest of the canonical JSON
        serialisation of the request tuple so that identical requests
        always map to the same key regardless of dict ordering.

        Args:
            model:       Model identifier string (e.g. ``"claude-opus-4-6"``).
            messages:    List of message dicts (role / content pairs).
            temperature: Sampling temperature used for the request.
            extra:       Optional additional fields to include in the key
                         (e.g. ``max_tokens``, ``system``).

        Returns:
            64-character hexadecimal SHA-256 digest string.
        """
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if extra:
            payload.update(extra)

        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def get(self, key: str) -> dict[str, Any] | None:
        """Return a cached response or ``None`` on miss / bypass.

        Args:
            key: Cache key produced by :meth:`make_key`.

        Returns:
            The cached response dict, or ``None`` if not found or cache
            is disabled.
        """
        if not self.enabled or self._tiered is None:
            return None

        value = self._tiered.get(key)
        if value is not None:
            _log.debug("response cache HIT  key=%s…", key[:16])
        else:
            _log.debug("response cache MISS key=%s…", key[:16])
        return value  # type: ignore[return-value]

    def set(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl: float | None = None,
    ) -> None:
        """Store a response in the cache.

        Args:
            key:   Cache key produced by :meth:`make_key`.
            value: Response dict to cache.
            ttl:   Optional override TTL (seconds).  Applies to both L1
                   and L2 tiers; ``None`` uses the instance defaults.
        """
        if not self.enabled or self._tiered is None:
            return

        self._tiered.set(key, value, l1_ttl=ttl, l2_ttl=ttl)
        _log.debug("response cache SET  key=%s… ttl=%s", key[:16], ttl)

    def invalidate(self, key: str) -> bool:
        """Remove a single entry from all tiers.

        Args:
            key: Cache key to remove.

        Returns:
            ``True`` if the key existed in at least one tier.
        """
        if not self.enabled or self._tiered is None:
            return False

        deleted = self._tiered.delete(key)
        if deleted:
            _log.debug("response cache INVALIDATE key=%s…", key[:16])
        return deleted

    def clear(self) -> None:
        """Purge all entries from all tiers."""
        if not self.enabled or self._tiered is None:
            return

        self._tiered.clear()
        _log.debug("response cache CLEARED")

    def stats(self) -> dict[str, Any]:
        """Return hit/miss statistics from both tiers.

        Returns:
            Dict with keys ``"enabled"``, ``"l1"``, ``"l2"``.
        """
        if not self.enabled or self._tiered is None:
            return {"enabled": False}

        return {"enabled": True, **self._tiered.stats()}


# ---------------------------------------------------------------------------
# Module-level singleton (convenience for import-time use)
# ---------------------------------------------------------------------------

_default_cache: ResponseCache | None = None


def get_default_cache() -> ResponseCache:
    """Return the process-wide default :class:`ResponseCache` instance.

    The instance is created lazily on first access.  Use
    :func:`configure_default_cache` to customise its settings before
    the first call.
    """
    global _default_cache  # noqa: PLW0603
    if _default_cache is None:
        _default_cache = ResponseCache()
    return _default_cache


def configure_default_cache(**kwargs: Any) -> None:
    """Replace the module-level default cache with new settings.

    Args:
        **kwargs: Forwarded verbatim to :class:`ResponseCache.__init__`.
    """
    global _default_cache  # noqa: PLW0603
    _default_cache = ResponseCache(**kwargs)
