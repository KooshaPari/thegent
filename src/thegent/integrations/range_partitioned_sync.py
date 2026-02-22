"""WL-Range partitioned sync.

Partitions workload IDs into ranges for efficient batch syncing.

# @trace WL-188
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SyncPartition:
    """Represents a range partition for sync operations."""

    start: int
    end: int
    items: list[str]


class RangePartitionedSync:
    """Partitions WL IDs into ranges for synchronized processing."""

    def partition(self, wl_ids: list[int], partition_size: int = 100) -> list[SyncPartition]:
        """Partition WL IDs into ranges.

        Groups IDs into contiguous ranges based on partition_size. Each partition
        spans from the minimum to maximum ID in a logical group, with items being
        the string representations of those IDs.

        Args:
            wl_ids: List of workload IDs to partition.
            partition_size: Number of IDs per partition.

        Returns:
            List of SyncPartition objects representing the partitioned ranges.

        Raises:
            ValueError: If partition_size < 1.
        """
        if partition_size < 1:
            raise ValueError("partition_size must be >= 1")

        if not wl_ids:
            logger.debug("Partition called with empty wl_ids")
            return []

        # Sort IDs to ensure contiguous ranges
        sorted_ids = sorted(wl_ids)
        partitions: list[SyncPartition] = []

        for i in range(0, len(sorted_ids), partition_size):
            chunk = sorted_ids[i : i + partition_size]
            start = chunk[0]
            end = chunk[-1]
            items = [str(wl_id) for wl_id in chunk]

            partition = SyncPartition(start=start, end=end, items=items)
            partitions.append(partition)
            logger.debug(f"Created partition: start={start}, end={end}, items={len(items)}")

        logger.debug(f"Partitioned {len(sorted_ids)} IDs into {len(partitions)} partitions")
        return partitions

    def items_in_range(self, start: int, end: int, wl_ids: list[int]) -> list[int]:
        """Get all IDs within a given range.

        Args:
            start: Minimum ID (inclusive).
            end: Maximum ID (inclusive).
            wl_ids: List of IDs to filter.

        Returns:
            List of IDs from wl_ids that fall within [start, end].
        """
        result = [wl_id for wl_id in wl_ids if start <= wl_id <= end]
        logger.debug(f"items_in_range({start}, {end}): found {len(result)} items")
        return result
