"""Tests for WL-157: GitHub Projects Bidirectional Sync.

Tests cover:
- Configuration validation
- Standalone-safe behavior (no crash when disabled)
- Auth error handling (graceful skip when gh auth missing project scope)
- Sync status queries
- Read/write sync operations
- CSV export/import
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from thegent.integrations.gh_project_sync import (
    GHProjectAuthError,
    GHProjectConfig,
    GHProjectSyncError,
    export_to_csv,
    get_project_status,
    import_from_csv,
    sync_from_github,
    sync_to_github,
)


@pytest.fixture
def valid_config():
    """Valid GitHub Projects configuration."""
    return GHProjectConfig(
        enabled=True,
        owner="kooshapari",
        number=1,
        direction="bidirectional",
        standalone_mode=True,
    )


@pytest.fixture
def disabled_config():
    """Disabled GitHub Projects configuration."""
    return GHProjectConfig(
        enabled=False,
        owner="kooshapari",
        number=1,
        direction="bidirectional",
        standalone_mode=True,
    )


@pytest.fixture
def invalid_config():
    """Invalid config (no owner, no project number)."""
    return GHProjectConfig(
        enabled=True,
        owner="",
        number=0,
        direction="bidirectional",
        standalone_mode=True,
    )


class TestGHProjectConfig:
    """Test GHProjectConfig validation."""

    def test_valid_config(self, valid_config):
        """Valid config passes validation."""
        assert valid_config.is_valid() is True
        assert valid_config.can_read() is True
        assert valid_config.can_write() is True

    def test_disabled_config(self, disabled_config):
        """Disabled config fails validation."""
        assert disabled_config.is_valid() is False

    def test_invalid_config_missing_owner(self):
        """Config without owner fails validation."""
        config = GHProjectConfig(
            enabled=True,
            owner="",
            number=1,
            direction="bidirectional",
            standalone_mode=True,
        )
        assert config.is_valid() is False

    def test_invalid_config_missing_number(self):
        """Config without project number fails validation."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=0,
            direction="bidirectional",
            standalone_mode=True,
        )
        assert config.is_valid() is False

    def test_read_only_direction(self):
        """Read-only config allows reading only."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="read_only",
            standalone_mode=True,
        )
        assert config.can_read() is True
        assert config.can_write() is False

    def test_write_only_direction(self):
        """Write-only config allows writing only."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="write_only",
            standalone_mode=True,
        )
        assert config.can_read() is False
        assert config.can_write() is True


class TestGHProjectAuthHandling:
    """Test standalone-safe auth error handling."""

    def test_disabled_config_returns_early(self, disabled_config):
        """Disabled config should return early with no errors."""
        result = get_project_status(disabled_config)
        assert result["enabled"] is False
        assert result["reason"] == "not_configured"

    def test_invalid_config_standalone_mode(self, invalid_config):
        """Invalid config in standalone mode should return gracefully."""
        result = get_project_status(invalid_config)
        assert result["enabled"] is False
        assert result["reason"] == "not_configured"

    def test_invalid_config_strict_mode_raises(self):
        """Invalid config in strict mode should raise."""
        config = GHProjectConfig(
            enabled=True,
            owner="",
            number=0,
            direction="bidirectional",
            standalone_mode=False,
        )
        with pytest.raises(GHProjectSyncError):
            get_project_status(config)

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_standalone_mode(self, mock_run, valid_config):
        """Auth error in standalone mode should return gracefully."""
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        result = get_project_status(valid_config)
        assert result["status"] == "auth_required"
        assert "project scope" in result["reason"]

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_strict_mode(self, mock_run):
        """Auth error in strict mode should raise."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="bidirectional",
            standalone_mode=False,
        )
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        with pytest.raises(GHProjectAuthError):
            get_project_status(config)


class TestGetProjectStatus:
    """Test project status retrieval."""

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_successful_status_query(self, mock_run, valid_config):
        """Successful status query returns project metadata."""
        mock_data = {
            "title": "My Project",
            "url": "https://github.com/users/kooshapari/projects/1",
            "items": [
                {"id": "1", "title": "Task 1"},
                {"id": "2", "title": "Task 2"},
            ],
        }
        mock_run.return_value = (0, json.dumps(mock_data), "")

        result = get_project_status(valid_config)

        assert result["enabled"] is True
        assert result["title"] == "My Project"
        assert result["owner"] == "kooshapari"
        assert result["number"] == 1
        assert result["direction"] == "bidirectional"
        assert len(result["items"]) == 2

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_gh_command_not_found(self, mock_run, valid_config):
        """Missing gh CLI raises error."""
        mock_run.side_effect = GHProjectSyncError("gh CLI not found on PATH")
        with pytest.raises(GHProjectSyncError):
            get_project_status(valid_config)

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_query_failure_with_auth_in_stderr(self, mock_run, valid_config):
        """Query failure mentioning 'auth' raises GHProjectAuthError."""
        mock_run.side_effect = GHProjectAuthError("permission denied: project scope required")
        result = get_project_status(valid_config)
        assert result["status"] == "auth_required"


class TestSyncToGithub:
    """Test syncing workstream to GitHub Projects."""

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_read_only_config_returns_early(self, mock_run):
        """Read-only config should not attempt write."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="read_only",
            standalone_mode=True,
        )
        workstream = [{"id": "WL-001", "title": "Task"}]
        result = sync_to_github(config, workstream)
        assert result["items_synced"] == 0
        assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_write_only_config_allows_sync(self, _mock_run, _valid_config):
        """Write-only config should allow write."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="write_only",
            standalone_mode=True,
        )
        workstream = [{"id": "WL-001", "title": "Task"}]
        result = sync_to_github(config, workstream)
        # Should not raise and should return result
        assert "items_created" in result or "items_synced" in result

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_disabled_config_returns_early(self, mock_run, disabled_config):
        """Disabled config should return early."""
        workstream = [{"id": "WL-001", "title": "Task"}]
        result = sync_to_github(disabled_config, workstream)
        assert result["items_synced"] == 0
        assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_standalone_mode(self, mock_run, valid_config):
        """Auth error in standalone mode should return gracefully."""
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        workstream = [{"id": "WL-001", "title": "Task"}]
        result = sync_to_github(valid_config, workstream)
        assert result["status"] == "auth_required"


class TestSyncFromGithub:
    """Test syncing GitHub Projects to workstream."""

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_successful_import(self, mock_run, valid_config):
        """Successful import returns items."""
        mock_items = [
            {"id": "GHID-1", "title": "GitHub Task 1", "status": "Open"},
            {"id": "GHID-2", "title": "GitHub Task 2", "status": "In Progress"},
        ]
        mock_run.return_value = (0, json.dumps(mock_items), "")

        result = sync_from_github(valid_config)

        assert result["items_imported"] == 2
        assert len(result["items"]) == 2

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_write_only_config_returns_early(self, mock_run):
        """Write-only config should not attempt read."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="write_only",
            standalone_mode=True,
        )
        result = sync_from_github(config)
        assert result["items_imported"] == 0
        assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_disabled_config_returns_early(self, mock_run, disabled_config):
        """Disabled config should return early."""
        result = sync_from_github(disabled_config)
        assert result["items_imported"] == 0
        assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_standalone_mode(self, mock_run, valid_config):
        """Auth error in standalone mode should return gracefully."""
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        result = sync_from_github(valid_config)
        assert result["status"] == "auth_required"


class TestExportToCsv:
    """Test CSV export functionality."""

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_successful_export(self, mock_run, valid_config):
        """Successful CSV export writes file."""
        csv_content = "id,title,status\n1,Task 1,Open\n2,Task 2,In Progress\n"
        mock_run.return_value = (0, csv_content, "")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = export_to_csv(valid_config, output_path)

            assert result["items_exported"] == 3  # 3 lines (including header)
            assert output_path.exists()
            assert output_path.read_text() == csv_content

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_read_only_config_works(self, mock_run):
        """Read-only config should allow export."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="read_only",
            standalone_mode=True,
        )
        csv_content = "id,title\n1,Task\n"
        mock_run.return_value = (0, csv_content, "")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = export_to_csv(config, output_path)

            assert result["items_exported"] >= 1

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_write_only_config_returns_early(self, mock_run):
        """Write-only config should not attempt export."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="write_only",
            standalone_mode=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = export_to_csv(config, output_path)

            assert result["items_exported"] == 0
            assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_disabled_config_returns_early(self, mock_run, disabled_config):
        """Disabled config should return early."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = export_to_csv(disabled_config, output_path)

            assert result["items_exported"] == 0
            assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_standalone_mode(self, mock_run, valid_config):
        """Auth error in standalone mode should return gracefully."""
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"
            result = export_to_csv(valid_config, output_path)

            assert result["status"] == "auth_required"


class TestImportFromCsv:
    """Test CSV import functionality."""

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_file_not_found(self, _mock_run, valid_config):
        """Import from non-existent file raises error."""
        csv_path = Path("/nonexistent/file.csv")
        with pytest.raises(GHProjectSyncError):
            import_from_csv(valid_config, csv_path)

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_read_only_config_returns_early(self, mock_run):
        """Read-only config should not attempt import."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="read_only",
            standalone_mode=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "import.csv"
            csv_path.write_text("id,title\n1,Task\n")
            result = import_from_csv(config, csv_path)

            assert result["items_imported"] == 0
            assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_write_only_config_allows_import(self, _mock_run):
        """Write-only config should allow import."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="write_only",
            standalone_mode=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "import.csv"
            csv_path.write_text("id,title\n1,Task\n")
            result = import_from_csv(config, csv_path)

            # Should not raise; may have zero items or some items
            assert "items_imported" in result

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_disabled_config_returns_early(self, mock_run, disabled_config):
        """Disabled config should return early."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "import.csv"
            csv_path.write_text("id,title\n1,Task\n")
            result = import_from_csv(disabled_config, csv_path)

            assert result["items_imported"] == 0
            assert mock_run.call_count == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_error_standalone_mode(self, mock_run, valid_config):
        """Auth error in standalone mode should return gracefully."""
        mock_run.side_effect = GHProjectAuthError("Missing project scope")
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "import.csv"
            csv_path.write_text("id,title\n1,Task\n")
            result = import_from_csv(valid_config, csv_path)

            assert result["status"] == "auth_required"


class TestStandaloneSafety:
    """Test standalone-safe behavior (WL-157 core requirement)."""

    def test_disabled_config_does_not_crash(self):
        """Disabled config should never crash any operation."""
        config = GHProjectConfig(
            enabled=False,
            owner="",
            number=0,
            direction="bidirectional",
            standalone_mode=True,
        )

        # Should return gracefully, not crash
        assert get_project_status(config)["enabled"] is False
        assert sync_from_github(config)["items_imported"] == 0
        assert sync_to_github(config, [])["items_synced"] == 0

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            assert export_to_csv(config, csv_path)["items_exported"] == 0

    def test_missing_config_does_not_crash(self):
        """Missing config should never crash any operation."""
        config = GHProjectConfig(
            enabled=True,
            owner="",
            number=0,
            direction="bidirectional",
            standalone_mode=True,
        )

        # Should return gracefully, not crash
        assert get_project_status(config)["enabled"] is False
        assert sync_from_github(config)["items_imported"] == 0
        assert sync_to_github(config, [])["items_synced"] == 0

    @patch("thegent.integrations.gh_project_sync._run_gh_command")
    def test_auth_missing_does_not_crash(self, mock_run):
        """Missing gh auth should not crash in standalone mode."""
        config = GHProjectConfig(
            enabled=True,
            owner="kooshapari",
            number=1,
            direction="bidirectional",
            standalone_mode=True,
        )
        mock_run.side_effect = GHProjectAuthError("gh: not authenticated")

        # Should return gracefully, not crash
        assert get_project_status(config)["status"] == "auth_required"
        assert sync_from_github(config)["status"] == "auth_required"
        assert sync_to_github(config, [])["status"] == "auth_required"


# End of file
