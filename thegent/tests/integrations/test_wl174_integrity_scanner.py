"""Tests for thegent.integrations.integrity_scanner — Local-vs-Remote integrity scanning.

@trace WL-174
"""

from __future__ import annotations

import pytest

from thegent.integrations.integrity_scanner import (
    IntegrityMismatch,
    IntegrityScanner,
    SeverityLevel,
)


class TestIntegrityMismatch:
    """Test IntegrityMismatch dataclass. @trace WL-174"""

    @pytest.mark.requirement("WL-174")
    def test_create_mismatch(self) -> None:
        """Can create an IntegrityMismatch with all fields."""
        mismatch = IntegrityMismatch(
            wl_id="WL-123",
            field="status",
            local_value="completed",
            remote_value="in_progress",
            connector="github",
            severity=SeverityLevel.MEDIUM,
        )

        assert mismatch.wl_id == "WL-123"
        assert mismatch.field == "status"
        assert mismatch.local_value == "completed"
        assert mismatch.remote_value == "in_progress"
        assert mismatch.connector == "github"
        assert mismatch.severity == SeverityLevel.MEDIUM

    @pytest.mark.requirement("WL-174")
    def test_severity_enum_values(self) -> None:
        """SeverityLevel enum has expected values."""
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.CRITICAL.value == "critical"


class TestIntegrityScanner:
    """Test IntegrityScanner operations. @trace WL-174"""

    @pytest.fixture
    def scanner(self) -> IntegrityScanner:
        """Provide an IntegrityScanner instance."""
        return IntegrityScanner()

    @pytest.mark.requirement("WL-174")
    def test_scan_no_items(self, scanner: IntegrityScanner) -> None:
        """Scan with empty local/remote lists returns no mismatches."""
        result = scanner.scan([], [], "github")
        assert result == []

    @pytest.mark.requirement("WL-174")
    def test_scan_status_mismatch(self, scanner: IntegrityScanner) -> None:
        """Detects status field mismatches."""
        local_items = [{"id": "item-1", "status": "completed", "priority": "high"}]
        remote_items = [{"id": "item-1", "status": "in_progress", "priority": "high"}]

        result = scanner.scan(local_items, remote_items, "github")

        assert len(result) == 1
        assert result[0].field == "status"
        assert result[0].local_value == "completed"
        assert result[0].remote_value == "in_progress"
        assert result[0].severity == SeverityLevel.MEDIUM

    @pytest.mark.requirement("WL-174")
    def test_scan_priority_mismatch(self, scanner: IntegrityScanner) -> None:
        """Detects priority field mismatches."""
        local_items = [{"id": "item-1", "status": "done", "priority": "low"}]
        remote_items = [{"id": "item-1", "status": "done", "priority": "high"}]

        result = scanner.scan(local_items, remote_items, "linear")

        assert len(result) == 1
        assert result[0].field == "priority"
        assert result[0].local_value == "low"
        assert result[0].remote_value == "high"
        assert result[0].severity == SeverityLevel.LOW
        assert result[0].connector == "linear"

    @pytest.mark.requirement("WL-174")
    def test_scan_multiple_mismatches(self, scanner: IntegrityScanner) -> None:
        """Detects multiple mismatches in same item."""
        local_items = [{"id": "item-1", "status": "done", "priority": "low"}]
        remote_items = [{"id": "item-1", "status": "pending", "priority": "high"}]

        result = scanner.scan(local_items, remote_items, "github")

        assert len(result) == 2
        field_names = {m.field for m in result}
        assert field_names == {"status", "priority"}

    @pytest.mark.requirement("WL-174")
    def test_scan_ignores_missing_remote_items(self, scanner: IntegrityScanner) -> None:
        """Ignores local items with no remote equivalent."""
        local_items = [
            {"id": "item-1", "status": "done"},
            {"id": "item-2", "status": "pending"},
        ]
        remote_items = [{"id": "item-1", "status": "done"}]

        result = scanner.scan(local_items, remote_items, "github")

        # Should not report mismatch for item-2 (missing in remote)
        assert len(result) == 0

    @pytest.mark.requirement("WL-174")
    def test_scan_none_values_ignored(self, scanner: IntegrityScanner) -> None:
        """Ignores comparisons where either side is None."""
        local_items = [{"id": "item-1", "status": None, "priority": "high"}]
        remote_items = [{"id": "item-1", "status": "pending", "priority": "high"}]

        result = scanner.scan(local_items, remote_items, "github")

        # Status mismatch should be ignored because local is None
        assert len(result) == 0
