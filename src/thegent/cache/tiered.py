"""
Tiered Cache

Combines multiple cache layers with fallback.
"""

from typing import Optional, Any
from .l1 import L1MemoryCache
from .l2 import L2DiskCache


class TieredCache:
    """Multi-tier cache with L1 and L2 fallbacks."""

    def __init__(
        self,
        l1_ttl: float = 60.0,
        l2_ttl: float = 3600.0,
        l1_max_size: int = 1000,
        l2_cache_dir: str = ".cache/l2"
    ):
        self.l1 = L1MemoryCache(ttl=l1_ttl, max_size=l1_max_size)
        self.l2 = L2DiskCache(cache_dir=l2_cache_dir, ttl=l2_ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get from L1, fallback to L2."""
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            return value

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            # Promote to L1
            self.l1.set(key, value)
            return value

        return None

    def set(
        self,
        key: str,
        value: Any,
        l1_ttl: Optional[float] = None,
        l2_ttl: Optional[float] = None
    ) -> None:
        """Set in both L1 and L2."""
        self.l1.set(key, value, ttl=l1_ttl)
        self.l2.set(key, value, ttl=l2_ttl)

    def delete(self, key: str) -> bool:
        """Delete from all tiers."""
        l1_deleted = self.l1.delete(key)
        l2_deleted = self.l2.delete(key)
        return l1_deleted or l2_deleted

    def clear(self) -> None:
        """Clear all tiers."""
        self.l1.clear()
        self.l2.clear()

    def stats(self) -> dict:
        """Get combined statistics."""
        return {
            "l1": self.l1.stats(),
            "l2": self.l2.stats()
        }

    def get_or_set(
        self,
        key: str,
        factory: callable,
        l1_ttl: Optional[float] = None,
        l2_ttl: Optional[float] = None
    ) -> Any:
        """Get from cache or compute and cache."""
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        self.set(key, value, l1_ttl, l2_ttl)
        return value
