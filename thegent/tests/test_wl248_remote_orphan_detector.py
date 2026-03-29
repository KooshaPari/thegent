from __future__ import annotations

import pytest

from thegent.integrations.remote_orphan_detector import (
    OrphanRecord,
    RemoteOrphanDetector,
)


@pytest.mark.requirement("WL-248")
class TestOrphanRecord:
    """Test OrphanRecord dataclass."""

    def test_create_orphan_record_default(self) -> None:
        """Test creating an orphan record with default reason."""
        record = OrphanRecord(item_id="item_123", source="remote")
        assert record.item_id == "item_123"
        assert record.source == "remote"
        assert record.reason == ""

    def test_create_orphan_record_with_reason(self) -> None:
        """Test creating an orphan record with custom reason."""
        record = OrphanRecord(
            item_id="item_456",
            source="github",
            reason="deleted from workstream",
        )
        assert record.item_id == "item_456"
        assert record.source == "github"
        assert record.reason == "deleted from workstream"


@pytest.mark.requirement("WL-248")
class TestRemoteOrphanDetector:
    """Test RemoteOrphanDetector."""

    def test_detect_no_orphans(self) -> None:
        """Test detect when all remote IDs are in local."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2", "id_3"}
        local = {"id_1", "id_2", "id_3"}

        orphans = detector.detect(remote, local)
        assert orphans == []

    def test_detect_some_orphans(self) -> None:
        """Test detect identifies orphaned remote items."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2", "id_3", "id_4"}
        local = {"id_1", "id_3"}

        orphans = detector.detect(remote, local)
        assert len(orphans) == 2
        orphan_ids = {o.item_id for o in orphans}
        assert orphan_ids == {"id_2", "id_4"}

    def test_detect_all_orphans(self) -> None:
        """Test detect when all remote IDs are orphaned."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2", "id_3"}
        local = {"id_4", "id_5"}

        orphans = detector.detect(remote, local)
        assert len(orphans) == 3
        orphan_ids = {o.item_id for o in orphans}
        assert orphan_ids == {"id_1", "id_2", "id_3"}

    def test_detect_empty_remote(self) -> None:
        """Test detect with empty remote set."""
        detector = RemoteOrphanDetector()
        orphans = detector.detect(set(), {"id_1", "id_2"})
        assert orphans == []

    def test_detect_empty_local(self) -> None:
        """Test detect with empty local set."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2"}
        orphans = detector.detect(remote, set())
        assert len(orphans) == 2

    def test_detect_default_source(self) -> None:
        """Test detect uses default source label."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2"}
        local = {"id_1"}

        orphans = detector.detect(remote, local)
        assert all(o.source == "remote" for o in orphans)

    def test_detect_custom_source(self) -> None:
        """Test detect with custom source label."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2"}
        local = {"id_1"}

        orphans = detector.detect(remote, local, source="github")
        assert all(o.source == "github" for o in orphans)

    def test_detect_returns_sorted(self) -> None:
        """Test that detect returns orphans in sorted order."""
        detector = RemoteOrphanDetector()
        remote = {"z_id", "a_id", "m_id"}
        local = set()

        orphans = detector.detect(remote, local)
        orphan_ids = [o.item_id for o in orphans]
        assert orphan_ids == ["a_id", "m_id", "z_id"]

    def test_filter_known_no_matches(self) -> None:
        """Test filter_known with no matching IDs."""
        detector = RemoteOrphanDetector()
        orphans = [
            OrphanRecord(item_id="id_1", source="remote"),
            OrphanRecord(item_id="id_2", source="remote"),
        ]
        known = {"id_3", "id_4"}

        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 2

    def test_filter_known_some_matches(self) -> None:
        """Test filter_known removes matching IDs."""
        detector = RemoteOrphanDetector()
        orphans = [
            OrphanRecord(item_id="id_1", source="remote"),
            OrphanRecord(item_id="id_2", source="remote"),
            OrphanRecord(item_id="id_3", source="remote"),
        ]
        known = {"id_2"}

        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 2
        assert all(o.item_id != "id_2" for o in filtered)

    def test_filter_known_all_matches(self) -> None:
        """Test filter_known removes all matching IDs."""
        detector = RemoteOrphanDetector()
        orphans = [
            OrphanRecord(item_id="id_1", source="remote"),
            OrphanRecord(item_id="id_2", source="remote"),
        ]
        known = {"id_1", "id_2"}

        filtered = detector.filter_known(orphans, known)
        assert filtered == []

    def test_filter_known_empty_orphans(self) -> None:
        """Test filter_known with empty orphan list."""
        detector = RemoteOrphanDetector()
        filtered = detector.filter_known([], {"id_1", "id_2"})
        assert filtered == []

    def test_filter_known_empty_known(self) -> None:
        """Test filter_known with empty known set."""
        detector = RemoteOrphanDetector()
        orphans = [
            OrphanRecord(item_id="id_1", source="remote"),
            OrphanRecord(item_id="id_2", source="remote"),
        ]

        filtered = detector.filter_known(orphans, set())
        assert len(filtered) == 2

    def test_workflow_detect_and_filter(self) -> None:
        """Test workflow: detect orphans then filter known."""
        detector = RemoteOrphanDetector()
        remote = {"id_1", "id_2", "id_3", "id_4"}
        local = {"id_1", "id_3"}
        known = {"id_2"}

        # Detect orphans
        orphans = detector.detect(remote, local, source="github")
        assert len(orphans) == 2

        # Filter known
        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 1
        assert filtered[0].item_id == "id_4"
