"""L1 and L2 cache infrastructure for multi-layer memory architecture.

L1: In-process cachetools TTLCache (fastest, automatic TTL management)
L2: Diskcache (persistent, process-safe, SQLite-backed)
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Optional

from cachetools import TTLCache

try:
    import diskcache

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

_log = logging.getLogger(__name__)


class L1Cache:
    """In-process cachetools TTLCache with metrics.

    Library-first (LIBRARY_FIRST_POLICY.md): Using cachetools for L1.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600) -> None:
        """Initialize L1 cache."""
        self._cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if key in self._cache:
            self.hit_count += 1
            return self._cache[key]
        self.miss_count += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value

    def clear(self) -> None:
        """Clear all entries."""
        self._cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self._cache.maxsize,
        }


class L2Cache:
    """Persistent diskcache-backed L2 cache.

    Library-first (LIBRARY_FIRST_POLICY.md): Using diskcache for persistent storage.
    """

    def __init__(self, cache_dir: str | Path = ".cache/l2", ttl_seconds: float = 86400) -> None:
        """Initialize L2 cache."""
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.hit_count = 0
        self.miss_count = 0

        self._cache: diskcache.Cache | None = None
        if DISKCACHE_AVAILABLE:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = diskcache.Cache(str(self.cache_dir))
        else:
            _log.warning("diskcache not installed; L2 cache disabled.")

    def get(self, key: str) -> Any | None:
        """Get value from L2 cache."""
        if self._cache is None:
            return None

        try:
            val = self._cache.get(key)
            if val is not None:
                self.hit_count += 1
                return val
        except Exception as e:
            _log.warning("L2 cache read error for %s: %s", key, e)

        self.miss_count += 1
        return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in L2 cache."""
        if self._cache is None:
            return

        try:
            self._cache.set(key, value, expire=ttl or self.ttl_seconds)
        except Exception as e:
            _log.warning("L2 cache write error for %s: %s", key, e)

    def clear(self) -> None:
        """Clear all cache entries."""
        if self._cache is not None:
            self._cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        size = len(self._cache) if self._cache is not None else 0
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "size": size,
        }

    def close(self) -> None:
        """Release diskcache resources."""
        if self._cache is not None:
            self._cache.close()


class LayeredCache:
    """Layered cache with L1 (in-process) → L2 (persistent) fallback."""

    def __init__(self, l1_size: int = 1000, l2_dir: str | Path = ".cache/l2") -> None:
        """Initialize layered cache."""
        self.l1 = L1Cache(max_size=l1_size)
        self.l2 = L2Cache(cache_dir=l2_dir)

    def get(self, key: str) -> Any | None:
        """Get from L1, fallback to L2."""
        val = self.l1.get(key)
        if val is not None:
            return val

        val = self.l2.get(key)
        if val is not None:
            self.l1.set(key, val)
            return val

        return None

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Store in both L1 and L2."""
        self.l1.set(key, value)
        self.l2.set(key, value, ttl=ttl)

    def clear(self) -> None:
        """Clear both layers."""
        self.l1.clear()
        self.l2.clear()

    def stats(self) -> dict[str, Any]:
        """Get stats from both layers."""
        return {
            "l1": self.l1.stats(),
            "l2": self.l2.stats(),
        }

    def close(self) -> None:
        """Release resources."""
        self.l2.close()
