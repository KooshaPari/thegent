"""
L2 Disk Cache

SQLite-backed disk cache for persistent storage.
"""

from typing import Optional, Any
import json
import time
import hashlib

try:
    import diskcache
    HAS_DISKCACHE = True
except ImportError:
    HAS_DISKCACHE = False


class L2DiskCache:
    """SQLite-backed disk cache."""

    def __init__(self, cache_dir: str = ".cache/l2", ttl: float = 3600.0):
        self.cache_dir = cache_dir
        self.ttl = ttl
        self._cache = None
        self._hits = 0
        self._misses = 0

        if HAS_DISKCACHE:
            self._cache = diskcache.Cache(cache_dir)

    def _hash_key(self, key: str) -> str:
        """Hash key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._cache:
            self._misses += 1
            return None

        hashed = self._hash_key(key)
        value = self._cache.get(hashed)
        if value is not None:
            self._hits += 1
            return json.loads(value)
        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        if not self._cache:
            return

        hashed = self._hash_key(key)
        entry_ttl = ttl if ttl is not None else self.ttl
        self._cache.set(hashed, json.dumps(value), expire=entry_ttl)

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._cache:
            return False

        hashed = self._hash_key(key)
        return self._cache.delete(hashed)

    def clear(self) -> None:
        """Clear all cache entries."""
        if self._cache:
            self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "available": HAS_DISKCACHE,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0
        }
