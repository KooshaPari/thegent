"""Tests for WL-253: Snapshot Compaction.

Verifies snapshot registration, compaction tracking, and savings calculation.

# @trace WL-253
"""

from __future__ import annotations

import pytest

from thegent.integrations.snapshot_compaction import (
    SnapshotCompactor,
    SnapshotEntry,
)


@pytest.mark.requirement("WL-253")
class TestSnapshotCompaction:
    """WL-253: Snapshot compaction."""

    def test_snapshot_entry_creation(self):
        """SnapshotEntry instantiation succeeds with valid inputs."""
        entry = SnapshotEntry(snapshot_id="snap-1", size_bytes=1000)
        assert entry.snapshot_id == "snap-1"
        assert entry.size_bytes == 1000
        assert not entry.compacted

    def test_snapshot_entry_with_compacted_flag(self):
        """SnapshotEntry can be created with compacted flag."""
        entry = SnapshotEntry(snapshot_id="snap-1", size_bytes=600, compacted=True)
        assert entry.snapshot_id == "snap-1"
        assert entry.size_bytes == 600
        assert entry.compacted

    def test_snapshot_entry_validation_empty_id(self):
        """SnapshotEntry rejects empty snapshot_id."""
        with pytest.raises(ValueError, match="snapshot_id cannot be empty"):
            SnapshotEntry(snapshot_id="", size_bytes=1000)

    def test_snapshot_entry_validation_negative_size(self):
        """SnapshotEntry rejects negative size_bytes."""
        with pytest.raises(ValueError, match="size_bytes must be >= 0"):
            SnapshotEntry(snapshot_id="snap-1", size_bytes=-1)

    def test_compactor_register(self):
        """register() adds a snapshot to the store."""
        compactor = SnapshotCompactor()
        entry = compactor.register("snap-1", 1000)

        assert entry.snapshot_id == "snap-1"
        assert entry.size_bytes == 1000
        assert not entry.compacted

    def test_compactor_register_multiple(self):
        """Multiple snapshots can be registered."""
        compactor = SnapshotCompactor()
        entry1 = compactor.register("snap-1", 1000)
        entry2 = compactor.register("snap-2", 2000)
        entry3 = compactor.register("snap-3", 500)

        assert entry1.snapshot_id == "snap-1"
        assert entry2.snapshot_id == "snap-2"
        assert entry3.snapshot_id == "snap-3"

    def test_compactor_register_overwrites(self):
        """Registering same ID overwrites previous entry."""
        compactor = SnapshotCompactor()
        entry1 = compactor.register("snap-1", 1000)
        entry2 = compactor.register("snap-1", 1500)

        assert entry1.snapshot_id == "snap-1"
        assert entry2.size_bytes == 1500

    def test_compactor_compact(self):
        """compact() marks snapshot as compacted and updates size."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        entry = compactor.compact("snap-1", 600)

        assert entry.snapshot_id == "snap-1"
        assert entry.size_bytes == 600
        assert entry.compacted

    def test_compactor_compact_not_registered(self):
        """compact() raises KeyError for unregistered snapshot."""
        compactor = SnapshotCompactor()
        with pytest.raises(KeyError, match="Snapshot 'snap-1' not registered"):
            compactor.compact("snap-1", 600)

    def test_compactor_compact_invalid_size(self):
        """compact() rejects negative compacted_size."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        with pytest.raises(ValueError, match="compacted_size must be >= 0"):
            compactor.compact("snap-1", -1)

    def test_compactor_savings_single_snapshot(self):
        """savings_bytes() calculates savings for single snapshot."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.compact("snap-1", 600)

        savings = compactor.savings_bytes()
        assert savings == 400

    def test_compactor_savings_multiple_snapshots(self):
        """savings_bytes() sums savings across all compacted snapshots."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.compact("snap-1", 600)
        compactor.compact("snap-2", 1500)

        savings = compactor.savings_bytes()
        assert savings == 900  # (1000-600) + (2000-1500)

    def test_compactor_savings_uncompacted_not_included(self):
        """savings_bytes() does not include uncompacted snapshots."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.compact("snap-1", 600)
        # snap-2 is not compacted

        savings = compactor.savings_bytes()
        assert savings == 400  # Only snap-1's savings

    def test_compactor_savings_no_compactions(self):
        """savings_bytes() returns 0 with no compactions."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)

        savings = compactor.savings_bytes()
        assert savings == 0

    def test_compactor_savings_empty_store(self):
        """savings_bytes() returns 0 for empty store."""
        compactor = SnapshotCompactor()
        savings = compactor.savings_bytes()
        assert savings == 0

    def test_compactor_uncompacted_empty(self):
        """uncompacted() returns empty list for all-compacted store."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.compact("snap-1", 600)
        compactor.compact("snap-2", 1500)

        uncompacted = compactor.uncompacted()
        assert len(uncompacted) == 0

    def test_compactor_uncompacted_all_uncompacted(self):
        """uncompacted() returns all snapshots when none are compacted."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.register("snap-3", 500)

        uncompacted = compactor.uncompacted()
        assert len(uncompacted) == 3
        snapshot_ids = {e.snapshot_id for e in uncompacted}
        assert snapshot_ids == {"snap-1", "snap-2", "snap-3"}

    def test_compactor_uncompacted_partial(self):
        """uncompacted() returns only non-compacted snapshots."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.register("snap-3", 500)
        compactor.compact("snap-1", 600)

        uncompacted = compactor.uncompacted()
        assert len(uncompacted) == 2
        snapshot_ids = {e.snapshot_id for e in uncompacted}
        assert snapshot_ids == {"snap-2", "snap-3"}

    def test_compactor_uncompacted_order(self):
        """uncompacted() preserves insertion order."""
        compactor = SnapshotCompactor()
        compactor.register("snap-3", 500)
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.compact("snap-1", 600)

        uncompacted = compactor.uncompacted()
        snapshot_ids = [e.snapshot_id for e in uncompacted]
        assert snapshot_ids == ["snap-3", "snap-2"]

    def test_compactor_full_workflow(self):
        """Full workflow: register, compact, query savings and uncompacted."""
        compactor = SnapshotCompactor()

        # Register three snapshots
        compactor.register("snap-1", 1000)
        compactor.register("snap-2", 2000)
        compactor.register("snap-3", 500)

        # Compact two of them
        compactor.compact("snap-1", 600)
        compactor.compact("snap-3", 250)

        # Check savings
        assert compactor.savings_bytes() == 650  # (1000-600) + (500-250)

        # Check uncompacted
        uncompacted = compactor.uncompacted()
        assert len(uncompacted) == 1
        assert uncompacted[0].snapshot_id == "snap-2"

    def test_compactor_zero_size_snapshots(self):
        """register() and compact() handle zero-size snapshots."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 0)
        entry = compactor.compact("snap-1", 0)

        assert entry.size_bytes == 0
        assert entry.compacted
        assert compactor.savings_bytes() == 0

    def test_compactor_compact_increases_size(self):
        """compact() can increase size (e.g., adding overhead)."""
        compactor = SnapshotCompactor()
        compactor.register("snap-1", 1000)
        compactor.compact("snap-1", 1100)  # Larger after compaction

        # Savings can be negative (not counted)
        savings = compactor.savings_bytes()
        assert savings == 0  # max(negative_savings, 0)
