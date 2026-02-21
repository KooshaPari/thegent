"""Multi-tier caching system for optimal performance.

This module provides a high-performance multi-tier caching system:
- L1: cachetools TTLCache (fastest, automatic TTL, smallest)
- L2: cachetools LRUCache (medium-term, configurable size)
- L3: diskcache (persistent, survives restarts)

Performance improvements:
- Multi-tier caching reduces memory pressure
- Persistent caching survives restarts
- Automatic tier promotion/demotion
- Configurable TTL and size limits
- Library-first (LIBRARY_FIRST_POLICY.md): Uses cachetools for all in-memory caching
"""

import contextlib
from pathlib import Path
from typing import Any

# Library-first (LIBRARY_FIRST_POLICY.md): Using cachetools for in-memory caching
from cachetools import LRUCache, TTLCache

try:
    import diskcache

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False


class MultiTierCache:
    """Multi-tier caching system with automatic tier management.

    Tiers:
    1. L1: In-memory dict (fastest, smallest, volatile)
    2. L2: cachetools LRUCache (medium-term, configurable size)
    3. L3: diskcache (persistent, survives restarts)
    """

    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        l3_path: str | None = None,
        default_ttl: float | None = None,
    ) -> None:
        """Initialize multi-tier cache.

        Args:
            l1_size: Maximum items in L1 cache
            l2_size: Maximum items in L2 cache
            l3_path: Path for L3 disk cache (None to disable)
            default_ttl: Default time-to-live in seconds (None = no expiry)
        """
        # L1: cachetools TTLCache (fastest, automatic TTL management)
        self.l1 = TTLCache(maxsize=l1_size, ttl=default_ttl or 60)
        self.l1_size = l1_size

        # L2: cachetools LRUCache (medium-term)
        self.l2 = LRUCache(maxsize=l2_size)
        self.l2_size = l2_size

        # L3: diskcache (persistent)
        if l3_path and DISKCACHE_AVAILABLE:
            self.l3: diskcache.Cache | None = diskcache.Cache(l3_path)
        else:
            self.l3 = None

        self.default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Get value from cache (checks all tiers).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        # Check L1 first (cachetools handles TTL automatically)
        if key in self.l1:
            return self.l1[key]

        # Check L2 (cachetools handles LRU automatically)
        if key in self.l2:
            value = self.l2[key]
            # Promote to L1
            self.l1[key] = value
            return value

        # Check L3 (persistent)
        if self.l3:
            try:
                value = self.l3.get(key)
                if value is not None:
                    # Promote to L2 and L1
                    self.l2[key] = value
                    self.l1[key] = value
                    return value
            except Exception:
                pass

        return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache (stores in all tiers).

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        ttl = ttl or self.default_ttl

        # Store in L1 (cachetools handles eviction and TTL automatically)
        self.l1[key] = value

        # Store in L2 (cachetools handles LRU automatically)
        self.l2[key] = value

        # Store in L3 (persistent)
        if self.l3:
            with contextlib.suppress(Exception):
                self.l3.set(key, value, expire=ttl)

    def delete(self, key: str) -> None:
        """Delete key from all tiers."""
        self.l1.pop(key, None)
        self.l2.pop(key, None)
        if self.l3:
            with contextlib.suppress(Exception):
                self.l3.delete(key)

    def clear(self) -> None:
        """Clear all tiers."""
        self.l1.clear()
        self.l2.clear()
        if self.l3:
            with contextlib.suppress(Exception):
                self.l3.clear()

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "l1_size": len(self.l1),
            "l1_max": self.l1_size,
            "l2_size": len(self.l2),
            "l2_max": self.l2_size,
        }

        if self.l3:
            try:
                # diskcache.Cache.__len__ has type Any|Constant - use object().__len__ bypass
                # or count keys directly
                stats["l3_size"] = sum(1 for _ in self.l3.iterkeys()) if hasattr(self.l3, "iterkeys") else 0
                stats["l3_volume"] = self.l3.volume()
            except Exception:
                stats["l3_size"] = 0
                stats["l3_volume"] = 0
        else:
            stats["l3_size"] = 0
            stats["l3_volume"] = 0

        return stats

    def get_with_fetch(self, key: str, fetch_func: Any, ttl: float | None = None) -> Any:
        """Get value from cache, or fetch and store if missing (with Singleflight TGNT-P9.1)."""
        value = self.get(key)
        if value is not None:
            return value

        from thegent.infra.cache_v2 import Singleflight

        if not hasattr(self, "_singleflight"):
            self._singleflight = Singleflight()

        def _fetch_and_store():
            res = fetch_func()
            if res is not None:
                self.set(key, res, ttl=ttl)
            return res

        return self._singleflight.do(key, _fetch_and_store)

    def enable_invalidation(self, directory: str | Path) -> None:
        """Enable real-time cache invalidation based on file changes (TGNT-P9.2)."""
        from pathlib import Path

        from thegent.infra.cache_v2 import CacheInvalidator

        self.invalidator = CacheInvalidator(self)
        self.invalidator.watch(Path(directory))


# Global cache instance
_global_cache: MultiTierCache | None = None


def get_cache(
    l1_size: int = 100, l2_size: int = 1000, l3_path: str | None = None, default_ttl: float | None = None
) -> MultiTierCache:
    """Get global multi-tier cache instance.

    Args:
        l1_size: Maximum items in L1 cache
        l2_size: Maximum items in L2 cache
        l3_path: Path for L3 disk cache
        default_ttl: Default time-to-live in seconds

    Returns:
        MultiTierCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiTierCache(l1_size=l1_size, l2_size=l2_size, l3_path=l3_path, default_ttl=default_ttl)
    return _global_cache
