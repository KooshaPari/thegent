"""Work chunking and parallelization for resource-aware task distribution.

Breaks large tasks into parallelizable chunks with resource-aware sizing.
"""

import logging
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuration for work chunking."""
    
    min_chunk_size: int = 1
    max_chunk_size: int = 100
    target_parallelism: int = 10
    resource_per_chunk_mb: float = 128.0
    resource_per_chunk_fd: int = 10
    
    # Dynamic sizing
    adaptive: bool = True
    min_parallelism: int = 2
    max_parallelism: int = 50


def compute_optimal_chunk_size(
    total_items: int,
    available_resources: dict[str, Any],
    config: ChunkConfig | None = None,
) -> tuple[int, int]:
    """Compute optimal chunk size and parallelism.
    
    Returns (chunk_size, num_chunks).
    """
    cfg = config or ChunkConfig()
    
    if not cfg.adaptive:
        chunk_size = max(cfg.min_chunk_size, min(cfg.max_chunk_size, total_items // cfg.target_parallelism))
        num_chunks = (total_items + chunk_size - 1) // chunk_size
        return chunk_size, num_chunks
    
    # Resource-aware chunking
    available_memory_mb = available_resources.get("mem_available_mb", 1024.0)
    available_fd = available_resources.get("fd_available", 100)
    
    # Calculate max parallelism based on resources
    max_by_memory = int(available_memory_mb / cfg.resource_per_chunk_mb)
    max_by_fd = int(available_fd / cfg.resource_per_chunk_fd)
    
    max_parallelism = min(max_by_memory, max_by_fd, cfg.max_parallelism)
    max_parallelism = max(cfg.min_parallelism, max_parallelism)
    
    # Compute chunk size
    chunk_size = max(cfg.min_chunk_size, (total_items + max_parallelism - 1) // max_parallelism)
    chunk_size = min(chunk_size, cfg.max_chunk_size)
    
    num_chunks = (total_items + chunk_size - 1) // chunk_size
    
    return chunk_size, num_chunks


def chunk_work_items(
    items: list[Any],
    chunk_size: int,
) -> list[list[Any]]:
    """Split work items into chunks."""
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i : i + chunk_size])
    return chunks
