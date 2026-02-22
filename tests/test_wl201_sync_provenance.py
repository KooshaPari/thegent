# @trace WL-201
"""Tests for Sync Provenance Stamps.

Validates provenance metadata attachment, extraction, and handling
for sync operations.
"""

from __future__ import annotations

import pytest

from thegent.integrations.sync_provenance import (
    SyncProvenanceStamp,
    extract_provenance,
    get_current_timestamp,
    has_provenance,
    remove_provenance,
    stamp_sync_record,
)


@pytest.mark.requirement("WL-201")
def test_sync_provenance_stamp_creation():
    """Test creating a provenance stamp."""
    stamp = SyncProvenanceStamp(
        sync_id="sync-123",
        timestamp="2026-02-22T10:30:00Z",
        source="github",
        operator="workstream-autosync",
        cycle_number=42,
    )
    assert stamp.sync_id == "sync-123"
    assert stamp.timestamp == "2026-02-22T10:30:00Z"
    assert stamp.source == "github"
    assert stamp.operator == "workstream-autosync"
    assert stamp.cycle_number == 42


@pytest.mark.requirement("WL-201")
def test_sync_provenance_stamp_to_dict():
    """Test converting a stamp to dictionary."""
    stamp = SyncProvenanceStamp(
        sync_id="sync-123",
        timestamp="2026-02-22T10:30:00Z",
        source="github",
        operator="workstream-autosync",
        cycle_number=42,
    )
    data = stamp.to_dict()

    assert data["sync_id"] == "sync-123"
    assert data["timestamp"] == "2026-02-22T10:30:00Z"
    assert data["source"] == "github"
    assert data["operator"] == "workstream-autosync"
    assert data["cycle_number"] == 42


@pytest.mark.requirement("WL-201")
def test_sync_provenance_stamp_from_dict():
    """Test creating a stamp from dictionary."""
    data = {
        "sync_id": "sync-456",
        "timestamp": "2026-02-22T11:00:00Z",
        "source": "linear",
        "operator": "event-handler",
        "cycle_number": 5,
    }
    stamp = SyncProvenanceStamp.from_dict(data)

    assert stamp.sync_id == "sync-456"
    assert stamp.timestamp == "2026-02-22T11:00:00Z"
    assert stamp.source == "linear"
    assert stamp.operator == "event-handler"
    assert stamp.cycle_number == 5


@pytest.mark.requirement("WL-201")
def test_stamp_sync_record_attaches_provenance():
    """Test that stamping a record attaches provenance metadata."""
    record = {"id": "issue-1", "title": "Fix bug"}
    stamp = SyncProvenanceStamp(
        sync_id="sync-789",
        timestamp="2026-02-22T12:00:00Z",
        source="github",
        operator="sync-agent",
        cycle_number=1,
    )

    stamped = stamp_sync_record(record, stamp)

    # Original record should be unchanged
    assert "__provenance__" not in record
    # Stamped record should have provenance
    assert "__provenance__" in stamped
    assert stamped["id"] == "issue-1"
    assert stamped["title"] == "Fix bug"
    assert stamped["__provenance__"]["sync_id"] == "sync-789"


@pytest.mark.requirement("WL-201")
def test_stamp_sync_record_rejects_non_dict():
    """Test that stamping rejects non-dict records."""
    stamp = SyncProvenanceStamp(
        sync_id="sync-123",
        timestamp="2026-02-22T10:30:00Z",
        source="github",
        operator="agent",
        cycle_number=1,
    )

    with pytest.raises(ValueError, match="must be a dictionary"):
        stamp_sync_record("not a dict", stamp)


@pytest.mark.requirement("WL-201")
def test_extract_provenance_from_stamped_record():
    """Test extracting provenance from a stamped record."""
    record = {"id": "issue-1", "title": "Fix bug"}
    stamp = SyncProvenanceStamp(
        sync_id="sync-789",
        timestamp="2026-02-22T12:00:00Z",
        source="github",
        operator="sync-agent",
        cycle_number=1,
    )

    stamped = stamp_sync_record(record, stamp)
    extracted = extract_provenance(stamped)

    assert extracted is not None
    assert extracted.sync_id == "sync-789"
    assert extracted.source == "github"
    assert extracted.operator == "sync-agent"
    assert extracted.cycle_number == 1


@pytest.mark.requirement("WL-201")
def test_extract_provenance_from_unstamped_record():
    """Test that extracting from unstamped record returns None."""
    record = {"id": "issue-1", "title": "Fix bug"}
    extracted = extract_provenance(record)
    assert extracted is None


@pytest.mark.requirement("WL-201")
def test_extract_provenance_rejects_non_dict():
    """Test that extraction rejects non-dict records."""
    with pytest.raises(ValueError, match="must be a dictionary"):
        extract_provenance("not a dict")


@pytest.mark.requirement("WL-201")
def test_has_provenance_true():
    """Test has_provenance returns True for stamped records."""
    record = {"id": "issue-1"}
    stamp = SyncProvenanceStamp(
        sync_id="sync-1",
        timestamp="2026-02-22T10:00:00Z",
        source="github",
        operator="agent",
        cycle_number=1,
    )
    stamped = stamp_sync_record(record, stamp)
    assert has_provenance(stamped) is True


@pytest.mark.requirement("WL-201")
def test_has_provenance_false():
    """Test has_provenance returns False for unstamped records."""
    record = {"id": "issue-1"}
    assert has_provenance(record) is False


@pytest.mark.requirement("WL-201")
def test_remove_provenance():
    """Test removing provenance from a stamped record."""
    record = {"id": "issue-1", "title": "Fix bug"}
    stamp = SyncProvenanceStamp(
        sync_id="sync-789",
        timestamp="2026-02-22T12:00:00Z",
        source="github",
        operator="sync-agent",
        cycle_number=1,
    )

    stamped = stamp_sync_record(record, stamp)
    assert has_provenance(stamped) is True

    cleaned = remove_provenance(stamped)
    assert has_provenance(cleaned) is False
    assert cleaned["id"] == "issue-1"
    assert cleaned["title"] == "Fix bug"
    assert "__provenance__" not in cleaned


@pytest.mark.requirement("WL-201")
def test_remove_provenance_no_op_on_unstamped():
    """Test removing provenance from unstamped record is safe."""
    record = {"id": "issue-1"}
    result = remove_provenance(record)
    assert result == record
    assert "__provenance__" not in result


@pytest.mark.requirement("WL-201")
def test_get_current_timestamp_format():
    """Test that get_current_timestamp returns ISO 8601 with Z suffix."""
    ts = get_current_timestamp()
    assert ts.endswith("Z")
    # Should be parseable as ISO format (basic check)
    assert "T" in ts
    assert len(ts) > 10  # At least YYYY-MM-DDTHH


@pytest.mark.requirement("WL-201")
def test_extract_provenance_malformed_data():
    """Test extraction handles malformed provenance data."""
    record = {"id": "issue-1", "__provenance__": "not a dict"}
    with pytest.raises(ValueError, match="must be a dictionary"):
        extract_provenance(record)


@pytest.mark.requirement("WL-201")
def test_extract_provenance_missing_field():
    """Test extraction handles missing required fields."""
    record = {
        "id": "issue-1",
        "__provenance__": {
            "sync_id": "sync-1",
            # Missing other required fields
        },
    }
    with pytest.raises(ValueError, match="missing key"):
        extract_provenance(record)


@pytest.mark.requirement("WL-201")
def test_round_trip_stamp_extraction():
    """Test round-trip: stamp → extract → verify."""
    original_stamp = SyncProvenanceStamp(
        sync_id="sync-complete",
        timestamp="2026-02-22T14:25:30Z",
        source="board",
        operator="reconciler",
        cycle_number=99,
    )

    record = {"task_id": "task-1"}
    stamped = stamp_sync_record(record, original_stamp)
    extracted = extract_provenance(stamped)

    assert extracted.sync_id == original_stamp.sync_id
    assert extracted.timestamp == original_stamp.timestamp
    assert extracted.source == original_stamp.source
    assert extracted.operator == original_stamp.operator
    assert extracted.cycle_number == original_stamp.cycle_number
