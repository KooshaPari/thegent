"""L1 and L2 cache infrastructure for multi-layer memory architecture.

L1: In-process LRU cache with TTL expiration
L2: File-based persistent cache with fallback
"""

import logging
import pickle
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class L1Cache:
    """In-process LRU cache with TTL expiration.

    Attributes:
        max_size: Maximum number of entries to keep
        ttl_seconds: Time-to-live for each entry in seconds
        hit_count: Number of cache hits
        miss_count: Number of cache misses
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600) -> None:
        """Initialize L1 cache.

        Args:
            max_size: Maximum cache size (default 1000)
            ttl_seconds: Time-to-live per entry (default 3600s)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            self.miss_count += 1
            return None

        entry = self._cache[key]
        if time.time() - entry["created_at"] > self.ttl_seconds:
            del self._cache[key]
            self.miss_count += 1
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        self.hit_count += 1
        return entry["value"]

    def set(self, key: str, value: Any) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self._cache:
            del self._cache[key]

        if len(self._cache) >= self.max_size:
            # Remove least recently used (first item)
            self._cache.popitem(last=False)

        self._cache[key] = {
            "value": value,
            "created_at": time.time(),
        }

    def clear(self) -> None:
        """Clear all entries."""
        self._cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with hit_count, miss_count, hit_rate, size
        """
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
        }


class L2Cache:
    """File-based persistent cache.

    Stores cache entries to disk for persistence across process restarts.
    """

    def __init__(self, cache_dir: str = ".cache/l2", ttl_seconds: int = 86400) -> None:
        """Initialize L2 cache.

        Args:
            cache_dir: Directory for cache files (default .cache/l2)
            ttl_seconds: Time-to-live per entry (default 86400s = 1 day)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.hit_count = 0
        self.miss_count = 0

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_key}.cache"

    def get(self, key: str) -> Any | None:
        """Get value from L2 cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            self.miss_count += 1
            return None

        try:
            with open(cache_path, "rb") as f:
                entry = pickle.load(f)

            if time.time() - entry["created_at"] > self.ttl_seconds:
                cache_path.unlink()
                self.miss_count += 1
                return None

            self.hit_count += 1
            return entry["value"]
        except Exception as e:
            logger.warning(f"L2 cache read error for {key}: {e}")
            self.miss_count += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Set value in L2 cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)

        try:
            entry = {
                "value": value,
                "created_at": time.time(),
            }
            with open(cache_path, "wb") as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.warning(f"L2 cache write error for {key}: {e}")

    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {cache_file}: {e}")
        self.hit_count = 0
        self.miss_count = 0

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        size = sum(1 for _ in self.cache_dir.glob("*.cache"))
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "size": size,
        }


class LayeredCache:
    """Layered cache with L1 → L2 fallback.

    Implements fallback logic:
    1. Check L1 (fast, in-process)
    2. Check L2 (slower, file-based)
    3. Return None if not found in either layer
    """

    def __init__(self, l1_size: int = 1000, l2_dir: str = ".cache/l2") -> None:
        """Initialize layered cache.

        Args:
            l1_size: Max size for L1 cache
            l2_dir: Directory for L2 cache
        """
        self.l1 = L1Cache(max_size=l1_size)
        self.l2 = L2Cache(cache_dir=l2_dir)

    def get(self, key: str) -> Any | None:
        """Get from L1, fallback to L2.

        Args:
            key: Cache key

        Returns:
            Value from L1 or L2, or None
        """
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            return value

        # Fall back to L2
        value = self.l2.get(key)
        if value is not None:
            # Populate L1 on L2 hit
            self.l1.set(key, value)
            return value

        return None

    def set(self, key: str, value: Any) -> None:
        """Store in both L1 and L2.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.l1.set(key, value)
        self.l2.set(key, value)

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
