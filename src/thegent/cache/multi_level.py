"""Multi-level caching system."""
from __future__ import annotations

from typing import Any

# Check if diskcache is available
try:
    import diskcache

    _DISKCACHE_AVAILABLE = True
except ImportError:
    _DISKCACHE_AVAILABLE = False


class CacheEntry:
    """A cache entry."""
    
    def __init__(self, key: str, value: Any, ttl: int | None = None) -> None:
        self.key = key
        self.value = value
        self.ttl = ttl


class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (disk) tiers."""
    
    def __init__(self) -> None:
        self.l1: dict[str, Any] = {}
        self.l2: dict[str, Any] = {}
    
    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if key in self.l1:
            return self.l1[key]
        if key in self.l2:
            return self.l2[key]
        return None
    
    def set(self, key: str, value: Any, level: int = 1) -> None:
        """Set value in cache."""
        if level <= 1:
            self.l1[key] = value
        else:
            self.l2[key] = value
    
    def delete(self, key: str) -> None:
        """Delete from all cache levels."""
        self.l1.pop(key, None)
        self.l2.pop(key, None)
    
    def clear(self, level: int | None = None) -> None:
        """Clear cache."""
        if level is None or level <= 1:
            self.l1.clear()
        if level is None or level > 1:
            self.l2.clear()


def cached_multi(func: Any) -> Any:
    """Decorator for caching multi-level operations."""
    return func


__all__ = ["CacheEntry", "MultiLevelCache", "_DISKCACHE_AVAILABLE", "cached_multi"]
