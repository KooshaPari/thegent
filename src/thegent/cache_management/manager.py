"""Cache management system."""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    """Cache management."""

    def __init__(self):
        """Initialize cache manager."""
        self.caches: dict[str, dict[str, Any]] = {}

    def create_cache(self, name: str, ttl: int = 3600) -> None:
        """Create a cache.

        Args:
            name: Cache name
            ttl: Time to live in seconds
        """
        self.caches[name] = {
            "data": {},
            "ttl": ttl,
            "created": time.time(),
        }

    def get(self, cache_name: str, key: str) -> Any:
        """Get value from cache.

        Args:
            cache_name: Cache name
            key: Cache key

        Returns:
            Cached value or None
        """
        cache = self.caches.get(cache_name)
        if not cache:
            return None

        entry = cache["data"].get(key)
        if not entry:
            return None

        if time.time() - entry["timestamp"] > cache["ttl"]:
            del cache["data"][key]
            return None

        return entry["value"]

    def set(self, cache_name: str, key: str, value: Any) -> None:
        """Set value in cache.

        Args:
            cache_name: Cache name
            key: Cache key
            value: Value to cache
        """
        cache = self.caches.get(cache_name)
        if not cache:
            self.create_cache(cache_name)
            cache = self.caches[cache_name]

        cache["data"][key] = {
            "value": value,
            "timestamp": time.time(),
        }
