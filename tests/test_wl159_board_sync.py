"""Tests for WL-159: Cross-Repo Board Sync Operationalization.

# @trace WL-159
"""

import tempfile
from pathlib import Path

import pytest

from thegent.commands.sync import SyncCommand, SyncOperationStatus


class TestBoardSyncWorkflow:
    """Test suite for board sync operationalization."""

    @pytest.fixture
    def temp_project(self) -> Path:
        """Create temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs" / "reference").mkdir(parents=True)
            yield root

    def test_board_sync_no_board_id(self, temp_project: Path) -> None:
        """Board sync should skip when no board_id is configured."""
        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id=None, source="github", dry_run=False)

        assert result.status == SyncOperationStatus.SKIPPED
        assert "no board_id" in result.message

    def test_board_sync_dry_run(self, temp_project: Path) -> None:
        """Board sync dry-run should report what would be synced."""
        # Create WORK_STREAM.md with sample items
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Cross-Repo Board Sync
**Status:** IN PROGRESS
**Priority:** P2

### [WL-160] Full Automatic Workstream Reflection
**Status:** BACKLOG
**Priority:** P1
"""
        )

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="123", source="github", dry_run=True)

        assert result.status == SyncOperationStatus.DRY_RUN
        assert "dry-run" in result.message.lower()
        assert result.ok is True
        assert result.details["board_id"] == "123"
        assert result.details["source"] == "github"

    def test_board_sync_no_items(self, temp_project: Path) -> None:
        """Board sync should succeed with no items when WORK_STREAM.md is empty."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text("# WORK_STREAM\n\nNo items yet.\n")

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="123", source="github", dry_run=False)

        assert result.status == SyncOperationStatus.SUCCESS
        assert "no work stream items" in result.message.lower()
        assert result.details["items"] == 0

    def test_board_sync_success(self, temp_project: Path) -> None:
        """Board sync should succeed and sync work items."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Cross-Repo Board Sync
**Status:** IN PROGRESS

### [WL-160] Workstream Reflection
**Status:** COMPLETED

### [WL-161] Board-ID Reconciliation
**Status:** BACKLOG
"""
        )

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="456", source="linear", dry_run=False)

        assert result.status == SyncOperationStatus.SUCCESS
        assert "Board sync complete" in result.message
        assert result.details["board_id"] == "456"
        assert result.details["source"] == "linear"
        assert result.details["items_synced"] >= 3

    def test_parse_work_stream_items(self, temp_project: Path) -> None:
        """Test parsing of WORK_STREAM.md items with status."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Cross-Repo Board Sync
**Status:** IN PROGRESS
**Priority:** P2

### [WL-160] Workstream Reflection
**Status:** COMPLETED

### [WL-161] Board-ID Reconciliation
**Status:** BACKLOG
"""
        )

        cmd = SyncCommand(project_root=temp_project)
        items = cmd._parse_work_stream_items()

        assert len(items) >= 3
        item_ids = [item["id"] for item in items]
        assert "WL-159" in item_ids
        assert "WL-160" in item_ids
        assert "WL-161" in item_ids

        # Check status parsing
        wl159 = next(item for item in items if item["id"] == "WL-159")
        assert wl159["status"] == "IN_PROGRESS"

    def test_parse_work_stream_no_file(self, temp_project: Path) -> None:
        """Test parsing when WORK_STREAM.md doesn't exist."""
        cmd = SyncCommand(project_root=temp_project)
        items = cmd._parse_work_stream_items()

        assert items == []

    def test_perform_board_sync_stub(self, temp_project: Path) -> None:
        """Test board sync stub implementation (returns canned result)."""
        items = [
            {"id": "WL-159", "title": "Board Sync", "status": "IN_PROGRESS"},
            {"id": "WL-160", "title": "Workstream Reflection", "status": "COMPLETED"},
        ]

        cmd = SyncCommand(project_root=temp_project)
        result = cmd._perform_board_sync("123", "github", items)

        assert result["synced"] == len(items)
        assert result["failed"] == 0
        assert len(result["updated_items"]) == len(items)
        assert result.get("stub") is True

    @pytest.mark.requirement("FR-SYNC-041")
    def test_board_sync_cli_integration(self, temp_project: Path) -> None:
        """Integration test: board sync command via CLI interface."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Cross-Repo Board Sync
**Status:** IN PROGRESS
"""
        )

        cmd = SyncCommand(project_root=temp_project)

        # Test with board_id
        result = cmd.sync_board(board_id="789", source="github", dry_run=True)
        assert result.ok is True
        assert "dry-run" in result.message.lower()

    def test_board_sync_github_source(self, temp_project: Path) -> None:
        """Test board sync with GitHub as source."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Board Sync
**Status:** IN PROGRESS
"""
        )

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="123", source="github", dry_run=True)

        assert result.details["source"] == "github"
        assert result.ok is True

    def test_board_sync_linear_source(self, temp_project: Path) -> None:
        """Test board sync with Linear as source."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text(
            """# WORK_STREAM

### [WL-159] Board Sync
**Status:** COMPLETED
"""
        )

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="PROJ-1", source="linear", dry_run=True)

        assert result.details["source"] == "linear"
        assert result.ok is True


class TestBoardSyncErrorHandling:
    """Test error handling in board sync."""

    @pytest.fixture
    def temp_project(self) -> Path:
        """Create temporary project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs" / "reference").mkdir(parents=True)
            yield root

    def test_board_sync_malformed_work_stream(self, temp_project: Path) -> None:
        """Board sync should handle malformed WORK_STREAM.md gracefully."""
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text("### Invalid markdown without closing\n\nNo status")

        cmd = SyncCommand(project_root=temp_project)
        result = cmd.sync_board(board_id="123", source="github", dry_run=False)

        # Should succeed with 0 items parsed
        assert result.status in (SyncOperationStatus.SUCCESS, SyncOperationStatus.SKIPPED)

    def test_board_sync_exception_handling(self, temp_project: Path) -> None:
        """Board sync should report errors properly."""
        # Create a scenario where parsing might fail
        work_stream = temp_project / "docs" / "reference" / "WORK_STREAM.md"
        work_stream.write_text("# WORK_STREAM\n\n### [WL-159] Test\n**Status:** INVALID")

        cmd = SyncCommand(project_root=temp_project)
        # Even with invalid status, should not raise
        result = cmd.sync_board(board_id="123", source="github", dry_run=False)

        assert result.status != SyncOperationStatus.FAILED or result.errors
