"""
Multi-Level Cache System

4-tier caching for agent responses and tool outputs:
- L1: TTLCache in-memory (60s TTL)
- L2: diskcache SQLite-backed (1hr TTL)
- L3: Redis distributed (optional)
- L4: Plan template cache (APC pattern)
"""

from .tiered import TieredCache
from .l1 import L1MemoryCache
from .l2 import L2DiskCache
from .response_cache import ResponseCache, get_default_cache, configure_default_cache

__all__ = [
    "TieredCache",
    "L1MemoryCache",
    "L2DiskCache",
    "ResponseCache",
    "get_default_cache",
    "configure_default_cache",
]
