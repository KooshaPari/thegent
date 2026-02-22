"""Large-range partition planning for workstream synchronization.

Dynamically plans partitions for distributing large workstreams across
parallel processing workers.

FR traceability: WL-283 (Large-Range Partition Planner)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Partition:
    """Represents a partition of items in a workstream."""

    partition_id: int
    start: int
    end: int
    size: int


class PartitionPlanner:
    """Plans partitions for large workstream ranges."""

    @staticmethod
    def plan(total_items: int, max_partition_size: int) -> list[Partition]:
        """Plan partitions for a range of items.

        Divides [0, total_items) into partitions of at most max_partition_size items.
        Each partition has sequential partition_id starting at 0.

        Args:
            total_items: Total number of items to partition.
            max_partition_size: Maximum size of each partition.

        Returns:
            List of Partition objects covering the full range.

        Raises:
            ValueError: If total_items < 0 or max_partition_size < 1.
        """
        if total_items < 0:
            raise ValueError("total_items must be >= 0")
        if max_partition_size < 1:
            raise ValueError("max_partition_size must be >= 1")

        if total_items == 0:
            return []

        partitions: list[Partition] = []
        partition_id = 0
        current_start = 0

        while current_start < total_items:
            partition_end = min(current_start + max_partition_size, total_items)
            size = partition_end - current_start

            partition = Partition(
                partition_id=partition_id,
                start=current_start,
                end=partition_end,
                size=size,
            )
            partitions.append(partition)

            current_start = partition_end
            partition_id += 1

        logger.debug(
            f"Planned {len(partitions)} partitions for {total_items} items "
            f"with max size {max_partition_size}"
        )

        return partitions

    @staticmethod
    def partition_for(
        item_index: int, partitions: list[Partition]
    ) -> Partition | None:
        """Find which partition an item belongs to.

        Args:
            item_index: Index of the item to locate.
            partitions: List of partitions to search.

        Returns:
            The partition containing the item, or None if out of range.
        """
        for partition in partitions:
            if partition.start <= item_index < partition.end:
                return partition

        return None

    @staticmethod
    def total_partitions(total_items: int, max_partition_size: int) -> int:
        """Calculate the number of partitions needed.

        Returns the count without allocating the actual partitions.

        Args:
            total_items: Total number of items to partition.
            max_partition_size: Maximum size of each partition.

        Returns:
            Number of partitions needed.

        Raises:
            ValueError: If total_items < 0 or max_partition_size < 1.
        """
        if total_items < 0:
            raise ValueError("total_items must be >= 0")
        if max_partition_size < 1:
            raise ValueError("max_partition_size must be >= 1")

        if total_items == 0:
            return 0

        # Calculate how many partitions are needed using ceiling division
        return (total_items + max_partition_size - 1) // max_partition_size
