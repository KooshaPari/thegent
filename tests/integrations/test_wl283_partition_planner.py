"""Tests for thegent.integrations.partition_planner — Large-range partition planner.

@trace WL-283
"""

from __future__ import annotations

import pytest

from thegent.integrations.partition_planner import Partition, PartitionPlanner


class TestPartition:
    """Test Partition dataclass."""

    @pytest.mark.requirement("WL-283")
    def test_partition_creation(self) -> None:
        """Can create a Partition with required fields."""
        partition = Partition(
            partition_id=0,
            start=0,
            end=100,
            size=100,
        )

        assert partition.partition_id == 0
        assert partition.start == 0
        assert partition.end == 100
        assert partition.size == 100


class TestPartitionPlannerPlan:
    """Test PartitionPlanner.plan operations. @trace WL-283"""

    @pytest.mark.requirement("WL-283")
    def test_plan_empty_range(self) -> None:
        """plan returns empty list for zero items."""
        partitions = PartitionPlanner.plan(0, 10)
        assert partitions == []

    @pytest.mark.requirement("WL-283")
    def test_plan_single_item(self) -> None:
        """plan creates single partition for single item."""
        partitions = PartitionPlanner.plan(1, 10)

        assert len(partitions) == 1
        assert partitions[0].partition_id == 0
        assert partitions[0].start == 0
        assert partitions[0].end == 1
        assert partitions[0].size == 1

    @pytest.mark.requirement("WL-283")
    def test_plan_exact_fit(self) -> None:
        """plan creates one partition when items fit exactly."""
        partitions = PartitionPlanner.plan(100, 100)

        assert len(partitions) == 1
        assert partitions[0].partition_id == 0
        assert partitions[0].start == 0
        assert partitions[0].end == 100
        assert partitions[0].size == 100

    @pytest.mark.requirement("WL-283")
    def test_plan_multiple_partitions(self) -> None:
        """plan creates multiple partitions when needed."""
        partitions = PartitionPlanner.plan(250, 100)

        assert len(partitions) == 3
        assert partitions[0].start == 0
        assert partitions[0].end == 100
        assert partitions[1].start == 100
        assert partitions[1].end == 200
        assert partitions[2].start == 200
        assert partitions[2].end == 250

    @pytest.mark.requirement("WL-283")
    def test_plan_partition_ids_sequential(self) -> None:
        """plan assigns sequential partition IDs starting at 0."""
        partitions = PartitionPlanner.plan(250, 100)

        for i, partition in enumerate(partitions):
            assert partition.partition_id == i

    @pytest.mark.requirement("WL-283")
    def test_plan_coverage_complete(self) -> None:
        """plan covers all items in the range."""
        partitions = PartitionPlanner.plan(1000, 300)

        # Check all items are covered
        assert partitions[0].start == 0
        assert partitions[-1].end == 1000

        # Check no gaps
        for i in range(len(partitions) - 1):
            assert partitions[i].end == partitions[i + 1].start

    @pytest.mark.requirement("WL-283")
    def test_plan_size_field(self) -> None:
        """plan sets correct size field for each partition."""
        partitions = PartitionPlanner.plan(250, 100)

        assert partitions[0].size == 100
        assert partitions[1].size == 100
        assert partitions[2].size == 50

    @pytest.mark.requirement("WL-283")
    def test_plan_respects_max_size(self) -> None:
        """plan never creates partition larger than max_partition_size."""
        partitions = PartitionPlanner.plan(500, 75)

        for partition in partitions:
            assert partition.size <= 75

    @pytest.mark.requirement("WL-283")
    def test_plan_invalid_total_items_negative(self) -> None:
        """plan raises ValueError for negative total_items."""
        with pytest.raises(ValueError, match="total_items must be >= 0"):
            PartitionPlanner.plan(-1, 10)

    @pytest.mark.requirement("WL-283")
    def test_plan_invalid_max_size_zero(self) -> None:
        """plan raises ValueError for max_partition_size < 1."""
        with pytest.raises(ValueError, match="max_partition_size must be >= 1"):
            PartitionPlanner.plan(100, 0)

    @pytest.mark.requirement("WL-283")
    def test_plan_invalid_max_size_negative(self) -> None:
        """plan raises ValueError for negative max_partition_size."""
        with pytest.raises(ValueError, match="max_partition_size must be >= 1"):
            PartitionPlanner.plan(100, -5)

    @pytest.mark.requirement("WL-283")
    def test_plan_small_max_size(self) -> None:
        """plan works with max_partition_size of 1."""
        partitions = PartitionPlanner.plan(5, 1)

        assert len(partitions) == 5
        for partition in partitions:
            assert partition.size == 1

    @pytest.mark.requirement("WL-283")
    def test_plan_large_range(self) -> None:
        """plan handles very large ranges."""
        partitions = PartitionPlanner.plan(1_000_000, 10_000)

        assert len(partitions) == 100
        assert partitions[-1].end == 1_000_000

    @pytest.mark.requirement("WL-283")
    def test_plan_uneven_distribution(self) -> None:
        """plan handles uneven distribution correctly."""
        partitions = PartitionPlanner.plan(10, 3)

        assert len(partitions) == 4
        assert partitions[0].size == 3
        assert partitions[1].size == 3
        assert partitions[2].size == 3
        assert partitions[3].size == 1


class TestPartitionPlannerPartitionFor:
    """Test PartitionPlanner.partition_for operations. @trace WL-283"""

    @pytest.mark.requirement("WL-283")
    def test_partition_for_first_item(self) -> None:
        """partition_for finds first item in first partition."""
        partitions = PartitionPlanner.plan(100, 50)
        result = PartitionPlanner.partition_for(0, partitions)

        assert result is not None
        assert result.partition_id == 0

    @pytest.mark.requirement("WL-283")
    def test_partition_for_last_item(self) -> None:
        """partition_for finds last item in last partition."""
        partitions = PartitionPlanner.plan(100, 50)
        result = PartitionPlanner.partition_for(99, partitions)

        assert result is not None
        assert result.partition_id == 1

    @pytest.mark.requirement("WL-283")
    def test_partition_for_out_of_range_negative(self) -> None:
        """partition_for returns None for negative index."""
        partitions = PartitionPlanner.plan(100, 50)
        result = PartitionPlanner.partition_for(-1, partitions)

        assert result is None

    @pytest.mark.requirement("WL-283")
    def test_partition_for_out_of_range_too_high(self) -> None:
        """partition_for returns None for index >= total items."""
        partitions = PartitionPlanner.plan(100, 50)
        result = PartitionPlanner.partition_for(100, partitions)

        assert result is None

    @pytest.mark.requirement("WL-283")
    def test_partition_for_multiple_items(self) -> None:
        """partition_for correctly identifies items in each partition."""
        partitions = PartitionPlanner.plan(100, 25)

        # Test items in different partitions
        assert PartitionPlanner.partition_for(0, partitions).partition_id == 0
        assert PartitionPlanner.partition_for(25, partitions).partition_id == 1
        assert PartitionPlanner.partition_for(50, partitions).partition_id == 2
        assert PartitionPlanner.partition_for(75, partitions).partition_id == 3

    @pytest.mark.requirement("WL-283")
    def test_partition_for_empty_partitions(self) -> None:
        """partition_for returns None when partitions list is empty."""
        result = PartitionPlanner.partition_for(0, [])
        assert result is None


class TestPartitionPlannerTotalPartitions:
    """Test PartitionPlanner.total_partitions operations. @trace WL-283"""

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_zero_items(self) -> None:
        """total_partitions returns 0 for zero items."""
        count = PartitionPlanner.total_partitions(0, 10)
        assert count == 0

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_single_item(self) -> None:
        """total_partitions returns 1 for single item."""
        count = PartitionPlanner.total_partitions(1, 10)
        assert count == 1

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_exact_fit(self) -> None:
        """total_partitions returns 1 when items fit exactly."""
        count = PartitionPlanner.total_partitions(100, 100)
        assert count == 1

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_multiple(self) -> None:
        """total_partitions calculates correct count for multiple partitions."""
        count = PartitionPlanner.total_partitions(250, 100)
        assert count == 3

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_uneven(self) -> None:
        """total_partitions rounds up for uneven distribution."""
        count = PartitionPlanner.total_partitions(10, 3)
        assert count == 4

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_matches_plan(self) -> None:
        """total_partitions returns same count as plan."""
        total_items = 1000
        max_size = 300

        planned = PartitionPlanner.plan(total_items, max_size)
        calculated = PartitionPlanner.total_partitions(total_items, max_size)

        assert calculated == len(planned)

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_large_range(self) -> None:
        """total_partitions handles large ranges."""
        count = PartitionPlanner.total_partitions(1_000_000, 10_000)
        assert count == 100

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_invalid_negative_items(self) -> None:
        """total_partitions raises ValueError for negative items."""
        with pytest.raises(ValueError, match="total_items must be >= 0"):
            PartitionPlanner.total_partitions(-1, 10)

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_invalid_zero_max_size(self) -> None:
        """total_partitions raises ValueError for max_size < 1."""
        with pytest.raises(ValueError, match="max_partition_size must be >= 1"):
            PartitionPlanner.total_partitions(100, 0)

    @pytest.mark.requirement("WL-283")
    def test_total_partitions_invalid_negative_max_size(self) -> None:
        """total_partitions raises ValueError for negative max_size."""
        with pytest.raises(ValueError, match="max_partition_size must be >= 1"):
            PartitionPlanner.total_partitions(100, -5)
