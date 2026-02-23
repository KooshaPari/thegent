from __future__ import annotations

import pytest

from thegent.integrations.local_orphan_detector import (
    LocalOrphanDetector,
    LocalOrphanRecord,
)


@pytest.mark.requirement("WL-249")
class TestLocalOrphanRecord:
    """Test LocalOrphanRecord dataclass."""

    def test_create_local_orphan_record_default(self) -> None:
        """Test creating a local orphan record with default reason."""
        record = LocalOrphanRecord(item_id="item_123")
        assert record.item_id == "item_123"
        assert record.reason == ""

    def test_create_local_orphan_record_with_reason(self) -> None:
        """Test creating a local orphan record with custom reason."""
        record = LocalOrphanRecord(
            item_id="item_456",
            reason="not synced to remote",
        )
        assert record.item_id == "item_456"
        assert record.reason == "not synced to remote"


@pytest.mark.requirement("WL-249")
class TestLocalOrphanDetector:
    """Test LocalOrphanDetector."""

    def test_detect_no_orphans(self) -> None:
        """Test detect when all local IDs are in remote."""
        detector = LocalOrphanDetector()
        local = {"id_1", "id_2", "id_3"}
        remote = {"id_1", "id_2", "id_3"}

        orphans = detector.detect(local, remote)
        assert orphans == []

    def test_detect_some_orphans(self) -> None:
        """Test detect identifies orphaned local items."""
        detector = LocalOrphanDetector()
        local = {"id_1", "id_2", "id_3", "id_4"}
        remote = {"id_1", "id_3"}

        orphans = detector.detect(local, remote)
        assert len(orphans) == 2
        orphan_ids = {o.item_id for o in orphans}
        assert orphan_ids == {"id_2", "id_4"}

    def test_detect_all_orphans(self) -> None:
        """Test detect when all local IDs are orphaned."""
        detector = LocalOrphanDetector()
        local = {"id_1", "id_2", "id_3"}
        remote = {"id_4", "id_5"}

        orphans = detector.detect(local, remote)
        assert len(orphans) == 3
        orphan_ids = {o.item_id for o in orphans}
        assert orphan_ids == {"id_1", "id_2", "id_3"}

    def test_detect_empty_local(self) -> None:
        """Test detect with empty local set."""
        detector = LocalOrphanDetector()
        orphans = detector.detect(set(), {"id_1", "id_2"})
        assert orphans == []

    def test_detect_empty_remote(self) -> None:
        """Test detect with empty remote set."""
        detector = LocalOrphanDetector()
        local = {"id_1", "id_2"}
        orphans = detector.detect(local, set())
        assert len(orphans) == 2

    def test_detect_returns_sorted(self) -> None:
        """Test that detect returns orphans in sorted order."""
        detector = LocalOrphanDetector()
        local = {"z_id", "a_id", "m_id"}
        remote = set()

        orphans = detector.detect(local, remote)
        orphan_ids = [o.item_id for o in orphans]
        assert orphan_ids == ["a_id", "m_id", "z_id"]

    def test_filter_known_no_matches(self) -> None:
        """Test filter_known with no matching IDs."""
        detector = LocalOrphanDetector()
        orphans = [
            LocalOrphanRecord(item_id="id_1"),
            LocalOrphanRecord(item_id="id_2"),
        ]
        known = {"id_3", "id_4"}

        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 2

    def test_filter_known_some_matches(self) -> None:
        """Test filter_known removes matching IDs."""
        detector = LocalOrphanDetector()
        orphans = [
            LocalOrphanRecord(item_id="id_1"),
            LocalOrphanRecord(item_id="id_2"),
            LocalOrphanRecord(item_id="id_3"),
        ]
        known = {"id_2"}

        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 2
        assert all(o.item_id != "id_2" for o in filtered)

    def test_filter_known_all_matches(self) -> None:
        """Test filter_known removes all matching IDs."""
        detector = LocalOrphanDetector()
        orphans = [
            LocalOrphanRecord(item_id="id_1"),
            LocalOrphanRecord(item_id="id_2"),
        ]
        known = {"id_1", "id_2"}

        filtered = detector.filter_known(orphans, known)
        assert filtered == []

    def test_filter_known_empty_orphans(self) -> None:
        """Test filter_known with empty orphan list."""
        detector = LocalOrphanDetector()
        filtered = detector.filter_known([], {"id_1", "id_2"})
        assert filtered == []

    def test_filter_known_empty_known(self) -> None:
        """Test filter_known with empty known set."""
        detector = LocalOrphanDetector()
        orphans = [
            LocalOrphanRecord(item_id="id_1"),
            LocalOrphanRecord(item_id="id_2"),
        ]

        filtered = detector.filter_known(orphans, set())
        assert len(filtered) == 2

    def test_workflow_detect_and_filter(self) -> None:
        """Test workflow: detect orphans then filter known."""
        detector = LocalOrphanDetector()
        local = {"id_1", "id_2", "id_3", "id_4"}
        remote = {"id_1", "id_3"}
        known = {"id_2"}

        # Detect orphans
        orphans = detector.detect(local, remote)
        assert len(orphans) == 2

        # Filter known
        filtered = detector.filter_known(orphans, known)
        assert len(filtered) == 1
        assert filtered[0].item_id == "id_4"

    def test_detect_asymmetric_sets(self) -> None:
        """Test detect correctly identifies asymmetric orphans."""
        detector = LocalOrphanDetector()
        # Local has more items, some not in remote
        local = {"wl_1", "wl_2", "wl_3", "wl_4", "wl_5"}
        remote = {"wl_1", "wl_2", "wl_3"}

        orphans = detector.detect(local, remote)
        assert len(orphans) == 2
        assert {o.item_id for o in orphans} == {"wl_4", "wl_5"}
