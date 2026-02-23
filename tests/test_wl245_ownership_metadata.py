"""Tests for ownership metadata propagation.

# @trace WL-245
"""

from __future__ import annotations

import pytest

from thegent.integrations.ownership_metadata import (
    OwnershipMetadataPropagator,
    OwnershipRecord,
)


@pytest.mark.requirement("WL-245")
class TestOwnershipRecord:
    """Test OwnershipRecord dataclass."""

    def test_ownership_record_creation_with_team(self) -> None:
        """Test creating an OwnershipRecord with team."""
        record = OwnershipRecord(item_id="item1", owner="alice", team="backend")
        assert record.item_id == "item1"
        assert record.owner == "alice"
        assert record.team == "backend"

    def test_ownership_record_creation_without_team(self) -> None:
        """Test creating an OwnershipRecord without team."""
        record = OwnershipRecord(item_id="item2", owner="bob")
        assert record.item_id == "item2"
        assert record.owner == "bob"
        assert record.team == ""

    def test_ownership_record_fields(self) -> None:
        """Test OwnershipRecord has expected fields."""
        record = OwnershipRecord(item_id="item3", owner="charlie", team="frontend")
        assert hasattr(record, "item_id")
        assert hasattr(record, "owner")
        assert hasattr(record, "team")


@pytest.mark.requirement("WL-245")
class TestOwnershipMetadataPropagator:
    """Test OwnershipMetadataPropagator."""

    def test_assign_with_team(self) -> None:
        """Test assigning ownership with team."""
        propagator = OwnershipMetadataPropagator()
        record = propagator.assign("item1", "alice", "backend")
        assert record.item_id == "item1"
        assert record.owner == "alice"
        assert record.team == "backend"

    def test_assign_without_team(self) -> None:
        """Test assigning ownership without team."""
        propagator = OwnershipMetadataPropagator()
        record = propagator.assign("item2", "bob")
        assert record.item_id == "item2"
        assert record.owner == "bob"
        assert record.team == ""

    def test_assign_overwrites(self) -> None:
        """Test that assigning overwrites previous ownership."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("item1", "alice", "backend")
        record = propagator.assign("item1", "bob", "frontend")
        assert record.owner == "bob"
        assert record.team == "frontend"

    def test_propagate_single_target(self) -> None:
        """Test propagating to a single target."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("source", "alice", "backend")
        results = propagator.propagate("source", ["target1"])
        assert len(results) == 1
        assert results[0].item_id == "target1"
        assert results[0].owner == "alice"
        assert results[0].team == "backend"

    def test_propagate_multiple_targets(self) -> None:
        """Test propagating to multiple targets."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("source", "charlie", "infra")
        results = propagator.propagate("source", ["target1", "target2", "target3"])
        assert len(results) == 3
        for result in results:
            assert result.owner == "charlie"
            assert result.team == "infra"

    def test_propagate_source_not_found(self) -> None:
        """Test propagating from non-existent source raises KeyError."""
        propagator = OwnershipMetadataPropagator()
        with pytest.raises(KeyError):
            propagator.propagate("nonexistent", ["target1"])

    def test_propagate_empty_targets(self) -> None:
        """Test propagating to empty target list."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("source", "alice", "backend")
        results = propagator.propagate("source", [])
        assert results == []

    def test_get_existing(self) -> None:
        """Test getting an existing ownership record."""
        propagator = OwnershipMetadataPropagator()
        assigned = propagator.assign("item1", "alice", "backend")
        retrieved = propagator.get("item1")
        assert retrieved == assigned
        assert retrieved.owner == "alice"

    def test_get_nonexistent(self) -> None:
        """Test getting a non-existent record raises KeyError."""
        propagator = OwnershipMetadataPropagator()
        with pytest.raises(KeyError):
            propagator.get("nonexistent")

    def test_by_owner_single(self) -> None:
        """Test getting items by owner with single item."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("item1", "alice", "backend")
        results = propagator.by_owner("alice")
        assert len(results) == 1
        assert results[0].item_id == "item1"

    def test_by_owner_multiple(self) -> None:
        """Test getting items by owner with multiple items."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("item1", "alice", "backend")
        propagator.assign("item2", "alice", "frontend")
        propagator.assign("item3", "bob", "backend")
        results = propagator.by_owner("alice")
        assert len(results) == 2
        assert all(r.owner == "alice" for r in results)

    def test_by_owner_not_found(self) -> None:
        """Test getting items by non-existent owner returns empty list."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("item1", "alice", "backend")
        results = propagator.by_owner("nonexistent")
        assert results == []

    def test_by_owner_multiple_owners(self) -> None:
        """Test by_owner filters correctly among multiple owners."""
        propagator = OwnershipMetadataPropagator()
        propagator.assign("item1", "alice", "backend")
        propagator.assign("item2", "bob", "frontend")
        propagator.assign("item3", "alice", "infra")
        propagator.assign("item4", "charlie", "backend")
        alice_items = propagator.by_owner("alice")
        assert len(alice_items) == 2
        assert all(r.owner == "alice" for r in alice_items)
