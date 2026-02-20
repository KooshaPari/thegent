"""Memory management module for thegent.

Provides multi-layer caching infrastructure:
- L1: In-process LRU cache (fast)
- L2: File-based persistent cache
- L3: Supermemory knowledge graph API (SupermemoryClient / MemoryManager)
- L4: Document artifact storage

Also provides idea seed detection and storage:
- Pattern-based seed detection from user prompts and agent outputs
- JSONL-based persistent storage for seeds
"""

from .cache import L1Cache, L2Cache, LayeredCache
from .manager import MemoryManager as LayeredMemoryManager
from .memory_manager import MemoryManager
from .seed_detector import Seed, SeedConfidence, SeedDetector, SeedSource
from .seed_storage import SeedStorage
from .supermemory_client import (
    MemoryEntry,
    SupermemoryAPIError,
    SupermemoryClient,
    SupermemoryConfigError,
)

__all__ = [
    "L1Cache",
    "L2Cache",
    "LayeredCache",
    "LayeredMemoryManager",
    "MemoryEntry",
    "MemoryManager",
    "Seed",
    "SeedConfidence",
    "SeedDetector",
    "SeedSource",
    "SeedStorage",
    "SupermemoryAPIError",
    "SupermemoryClient",
    "SupermemoryConfigError",
]
