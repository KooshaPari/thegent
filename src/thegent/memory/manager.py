"""Memory manager integrating all cache layers."""

import logging
from typing import Any

from .cache import LayeredCache

logger = logging.getLogger(__name__)


class MemoryManager:
    """Unified memory manager with L1-L2 layering.

    Handles knowledge storage and retrieval with automatic
    fallback between cache layers.
    """

    def __init__(self, l1_size: int = 1000, l2_dir: str = ".cache/l2") -> None:
        """Initialize memory manager.

        Args:
            l1_size: Max entries in L1 cache
            l2_dir: Directory for L2 persistent cache
        """
        self.cache = LayeredCache(l1_size=l1_size, l2_dir=l2_dir)

    async def get_knowledge(self, query: str) -> Any | None:
        """Get knowledge from cache layers.

        Implements L1 → L2 fallback:
        1. Check L1 (in-process LRU)
        2. Check L2 (file-based persistent)

        Args:
            query: Query string/key

        Returns:
            Cached knowledge or None
        """
        # For now, use query as cache key
        # In production, would query L3 (Supermemory) if not in L1/L2
        result = self.cache.get(query)
        if result is not None:
            logger.debug(f"Knowledge cache hit: {query}")
            return result

        logger.debug(f"Knowledge cache miss: {query}")
        return None

    async def store_knowledge(self, query: str, knowledge: Any) -> str:
        """Store knowledge in cache layers.

        Stores in both L1 and L2 for redundancy.

        Args:
            query: Query/key
            knowledge: Knowledge data to store

        Returns:
            Storage ID (for now, the query key)
        """
        self.cache.set(query, knowledge)
        logger.debug(f"Knowledge stored: {query}")
        return query

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict with L1 and L2 statistics
        """
        return self.cache.stats()

    def clear(self) -> None:
        """Clear all cache layers."""
        self.cache.clear()
        logger.info("Memory cache cleared")
