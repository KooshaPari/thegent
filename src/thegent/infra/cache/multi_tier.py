"""TGNT-P9.4 — three-tier cache primitive.

This module is the canonical home for :class:`MultiTierCache` and the
:func:`get_cache` singleton accessor.

Tier composition:

* **L1** — ``cachetools.TTLCache`` (fastest, automatic TTL, smallest).
* **L2** — ``cachetools.LRUCache`` (medium-term, configurable size).
* **L3** — ``PersistDict`` (persistent, survives restarts, safe
  serialization via LMDB). Optional; when unavailable, ``l3`` is
  ``None`` and ``get`` short-circuits to the l2 path.

The ``get`` method was refactored in the WL706 hardening pass into a
thin orchestrator over three helpers (``_check_l1``,
``_check_l2_promote_to_l1``, ``_check_l3_promote_to_l2_and_l1``) to
collapse the three-tier promotion fan-out into ≤10 LOC and pin the
behaviour with hardening tests.

``get_with_fetch`` adds ``Singleflight`` coalescing on top of the
multi-tier ``get`` / ``set`` pair — duplicate concurrent misses
collapse into a single ``fetch_func`` invocation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from cachetools import LRUCache, TTLCache

from thegent.infra.cache.singleflight import Singleflight

logger = logging.getLogger(__name__)

try:
    from PersistDict import PersistDict

    PERSISTDICT_AVAILABLE = True
except ImportError:
    PERSISTDICT_AVAILABLE = False


_MISS = object()


class MultiTierCache:
    """Multi-tier caching system with automatic tier management.

    Tiers:

    1. L1: cachetools TTLCache (fastest, automatic TTL, smallest).
    2. L2: cachetools LRUCache (medium-term, configurable size).
    3. L3: PersistDict (persistent, survives restarts, safe
       serialization).
    """

    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        l3_path: str | None = None,
        default_ttl: float | None = None,
    ) -> None:
        self.l1: TTLCache = TTLCache(maxsize=l1_size, ttl=default_ttl or 60)
        self.l1_size = l1_size
        self.l2: LRUCache = LRUCache(maxsize=l2_size)
        self.l2_size = l2_size
        # Use PersistDict for L3 (safe serialization via LMDB).
        self._l3_type: str = "none"
        if l3_path and PERSISTDICT_AVAILABLE:
            self.l3: "PersistDict | None" = PersistDict(
                database_path=l3_path,
                expiration_days=int(default_ttl / 86400) if default_ttl else 7,
                background_thread=False,
            )
            self._l3_type = "persistdict"
        else:
            self.l3 = None
        self.default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Look up a key across all three tiers, promoting on miss."""
        value = self._check_l1(key)
        if value is not _MISS:
            return value
        value = self._check_l2_promote_to_l1(key)
        if value is not _MISS:
            return value
        return self._check_l3_promote_to_l2_and_l1(key)

    def _check_l1(self, key: str) -> Any:
        """L1 lookup (no promotion). Returns ``_MISS`` on miss."""
        if key in self.l1:
            return self.l1[key]
        return _MISS

    def _check_l2_promote_to_l1(self, key: str) -> Any:
        """L2 lookup with L2 → L1 promotion. Returns ``_MISS`` on miss."""
        if key in self.l2:
            value = self.l2[key]
            self.l1[key] = value
            return value
        return _MISS

    def _check_l3_promote_to_l2_and_l1(self, key: str) -> Any | None:
        """L3 lookup with L3 → L2 → L1 double-promotion. Returns ``None`` on miss."""
        if self.l3:
            value = self._get_l3(key)
            if value is not None:
                self.l2[key] = value
                self.l1[key] = value
                return value
        return None

    def _get_l3(self, key: str) -> Any | None:
        """Get from L3 cache (PersistDict)."""
        try:
            return self.l3[key]
        except KeyError:
            return None
        except Exception:
            return None

    def _set_l3(self, key: str, value: Any, ttl: float | None) -> None:
        """Set L3 cache (PersistDict)."""
        try:
            self.l3[key] = value
        except Exception:
            pass

    def _delete_l3(self, key: str) -> None:
        """Delete from L3 cache (PersistDict)."""
        try:
            self.l3.pop(key, None)
        except Exception:
            pass

    def _clear_l3(self) -> None:
        """Clear L3 cache (PersistDict)."""
        try:
            self.l3.clear()
        except Exception:
            pass

    def _len_l3(self) -> int:
        """Get L3 cache size (PersistDict)."""
        try:
            l3 = self.l3
            return len(l3) if l3 is not None else 0
        except Exception:
            return 0

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        ttl = ttl or self.default_ttl
        self.l1[key] = value
        self.l2[key] = value
        self._set_l3(key, value, ttl)

    def delete(self, key: str) -> None:
        self.l1.pop(key, None)
        self.l2.pop(key, None)
        self._delete_l3(key)

    def clear(self) -> None:
        self.l1.clear()
        self.l2.clear()
        self._clear_l3()

    def stats(self) -> dict[str, Any]:
        stats: dict[str, Any] = {
            "l1_size": len(self.l1),
            "l1_max": self.l1_size,
            "l2_size": len(self.l2),
            "l2_max": self.l2_size,
        }
        if self.l3:
            try:
                stats["l3_size"] = self._len_l3()
                stats["l3_volume"] = "N/A"  # PersistDict doesn't have volume()
            except Exception:
                stats["l3_size"] = 0
                stats["l3_volume"] = 0
        else:
            stats["l3_size"] = 0
            stats["l3_volume"] = 0
        return stats

    def get_with_fetch(self, key: str, fetch_func: Any, ttl: float | None = None) -> Any:
        """Get value from cache, or fetch and store if missing (Singleflight coalescing)."""
        value = self.get(key)
        if value is not None:
            return value

        if not hasattr(self, "_singleflight"):
            self._singleflight = Singleflight()

        def _fetch_and_store():
            res = fetch_func()
            if res is not None:
                self.set(key, res, ttl=ttl)
            return res

        return self._singleflight.do(key, _fetch_and_store)

    def enable_invalidation(self, directory: str | Path) -> None:
        """Enable real-time cache invalidation based on file changes."""
        from thegent.infra.cache.invalidator import CacheInvalidator

        self.invalidator = CacheInvalidator(self)
        self.invalidator.watch(Path(directory))


_global_cache: MultiTierCache | None = None


def get_cache(
    l1_size: int = 100,
    l2_size: int = 1000,
    l3_path: str | None = None,
    default_ttl: float | None = None,
) -> MultiTierCache:
    """Get global multi-tier cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiTierCache(l1_size=l1_size, l2_size=l2_size, l3_path=l3_path, default_ttl=default_ttl)
    return _global_cache


__all__ = ["MultiTierCache", "PERSISTDICT_AVAILABLE", "get_cache"]
