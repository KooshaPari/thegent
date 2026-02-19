"""
Abstract cache provider interface for Supermemory L1/L2 cache layers.

This module defines the CacheProvider ABC that all concrete cache implementations
(Redis, FileCache, Memory) must implement. It supports TTL, eviction policies,
and hierarchical cache management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class CacheItem:
    """Represents a single cache item with metadata."""

    key: str
    """Cache key (unique identifier)."""

    value: Any
    """Cached value (any serializable type)."""

    created_at: datetime
    """Timestamp when item was created."""

    expires_at: datetime | None = None
    """Timestamp when item expires (if set)."""

    hits: int = 0
    """Number of times this item was accessed."""

    def is_expired(self) -> bool:
        """Check if this item has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def ttl_remaining(self) -> int | None:
        """Get remaining TTL in seconds, or None if no expiry."""
        if self.expires_at is None:
            return None
        remaining = (self.expires_at - datetime.now(UTC)).total_seconds()
        return max(0, int(remaining))


class CacheProvider(ABC):
    """
    Abstract base class for cache providers.

    Defines the interface that all cache implementations must follow.
    Implementations should support:
    - Key-value storage with optional TTL
    - Automatic expiration
    - Hit/miss tracking (optional)
    - Flush and eviction operations
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key to retrieve.

        Returns:
            The cached value if found and not expired, None otherwise.
        """

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Store a value in cache.

        Args:
            key: Cache key.
            value: Value to cache (should be serializable).
            ttl: Time-to-live in seconds. None means no expiry.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete.
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.

        Args:
            key: Cache key to check.

        Returns:
            True if key exists and is not expired, False otherwise.
        """

    @abstractmethod
    async def flush(self) -> None:
        """
        Clear all entries from cache.

        This is a destructive operation that removes all cached data.
        """

    @abstractmethod
    async def evict_expired(self) -> int:
        """
        Remove all expired items from cache.

        Returns:
            Number of items evicted.
        """

    async def set_with_ttl_seconds(self, key: str, value: Any, seconds: int) -> None:
        """
        Set a cache entry with TTL in seconds.

        Convenience method. Equivalent to set(key, value, ttl=seconds).

        Args:
            key: Cache key.
            value: Value to cache.
            seconds: TTL in seconds.
        """
        await self.set(key, value, ttl=seconds)

    async def set_with_ttl_delta(self, key: str, value: Any, delta: timedelta) -> None:
        """
        Set a cache entry with TTL as timedelta.

        Args:
            key: Cache key.
            value: Value to cache.
            delta: TTL as timedelta object.
        """
        await self.set(key, value, ttl=int(delta.total_seconds()))
