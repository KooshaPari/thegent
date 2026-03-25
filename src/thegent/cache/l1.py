"""
L1 Memory Cache

In-memory TTL cache for fast access.
"""

from dataclasses import dataclass
from typing import Optional, Any
import time


@dataclass
class CacheEntry:
    """Cache entry with TTL."""

    value: Any
    expires_at: float
    created_at: float

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class L1MemoryCache:
    """In-memory TTL cache."""

    def __init__(self, ttl: float = 60.0, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            self._hits += 1
            return entry.value
        self._misses += 1
        if entry:
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache."""
        # Evict if at capacity
        if len(self._cache) >= self.max_size:
            self._evict_expired()
            if len(self._cache) >= self.max_size:
                # Remove oldest
                oldest = min(self._cache.items(), key=lambda x: x[1].created_at)
                del self._cache[oldest[0]]

        now = time.time()
        entry_ttl = ttl if ttl is not None else self.ttl
        self._cache[key] = CacheEntry(value=value, expires_at=now + entry_ttl, created_at=now)

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def _evict_expired(self) -> int:
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, v in self._cache.items() if v.expires_at < now]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
        }
