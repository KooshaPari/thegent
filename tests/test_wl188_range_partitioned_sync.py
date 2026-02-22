"""Tests for WL-188: WL-Range Partitioned Sync.

Verifies that WL IDs are correctly partitioned into ranges.

# @trace WL-188
"""

from __future__ import annotations

import pytest

from thegent.integrations.range_partitioned_sync import RangePartitionedSync, SyncPartition


@pytest.mark.requirement("WL-188")
class TestRangePartitionedSync:
    """WL-188: WL-Range partitioned sync."""

    def test_partition_empty_list(self):
        """partition() with empty list returns empty."""
        sync = RangePartitionedSync()
        result = sync.partition([])
        assert result == []

    def test_partition_single_item(self):
        """partition() with single item creates one partition."""
        sync = RangePartitionedSync()
        result = sync.partition([42])
        assert len(result) == 1
        assert result[0].start == 42
        assert result[0].end == 42
        assert result[0].items == ["42"]

    def test_partition_fits_in_one(self):
        """partition() with items <= partition_size creates one batch."""
        sync = RangePartitionedSync()
        result = sync.partition([1, 2, 3, 4, 5], partition_size=10)
        assert len(result) == 1
        assert result[0].start == 1
        assert result[0].end == 5
        assert result[0].items == ["1", "2", "3", "4", "5"]

    def test_partition_multiple_batches(self):
        """partition() creates multiple partitions."""
        sync = RangePartitionedSync()
        result = sync.partition([10, 20, 30, 40, 50, 60], partition_size=2)
        assert len(result) == 3
        assert result[0].start == 10
        assert result[0].end == 20
        assert result[0].items == ["10", "20"]
        assert result[1].start == 30
        assert result[1].end == 40
        assert result[2].start == 50
        assert result[2].end == 60

    def test_partition_unordered_input(self):
        """partition() sorts IDs before partitioning."""
        sync = RangePartitionedSync()
        result = sync.partition([50, 10, 40, 20, 30], partition_size=2)
        assert len(result) == 3
        assert result[0].start == 10
        assert result[0].items == ["10", "20"]
        assert result[1].start == 30
        assert result[1].items == ["30", "40"]
        assert result[2].start == 50
        assert result[2].items == ["50"]

    def test_partition_invalid_partition_size(self):
        """partition() with partition_size < 1 raises ValueError."""
        sync = RangePartitionedSync()
        with pytest.raises(ValueError, match="partition_size must be >= 1"):
            sync.partition([1, 2, 3], partition_size=0)

    def test_partition_duplicates_in_input(self):
        """partition() handles duplicate IDs."""
        sync = RangePartitionedSync()
        result = sync.partition([1, 2, 2, 3, 3, 3], partition_size=2)
        # After sorting: [1, 2, 2, 3, 3, 3]
        assert len(result) == 3

    def test_items_in_range_empty_list(self):
        """items_in_range() with empty list returns empty."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(10, 20, [])
        assert result == []

    def test_items_in_range_all_match(self):
        """items_in_range() returns all items in range."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(10, 20, [10, 12, 15, 20])
        assert result == [10, 12, 15, 20]

    def test_items_in_range_partial_match(self):
        """items_in_range() returns only items in range."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(10, 20, [5, 10, 15, 20, 25])
        assert result == [10, 15, 20]

    def test_items_in_range_no_match(self):
        """items_in_range() returns empty if no items match."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(100, 200, [1, 2, 3])
        assert result == []

    def test_items_in_range_boundary(self):
        """items_in_range() includes boundaries."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(10, 10, [10])
        assert result == [10]

    def test_items_in_range_unordered_input(self):
        """items_in_range() works with unordered input."""
        sync = RangePartitionedSync()
        result = sync.items_in_range(20, 40, [50, 10, 30, 5, 25])
        assert sorted(result) == [25, 30]

    def test_partition_large_dataset(self):
        """partition() handles larger datasets."""
        sync = RangePartitionedSync()
        ids = list(range(1, 101))  # 1 to 100
        result = sync.partition(ids, partition_size=25)
        assert len(result) == 4
        assert all(len(p.items) == 25 for p in result)
        assert result[0].start == 1
        assert result[-1].end == 100
