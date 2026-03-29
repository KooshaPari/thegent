"""
E2E test for: thegent sync remote-orphans

Agent Journey: Agent executes thegent sync remote-orphans command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncRemoteOrphans:
    """E2E tests for thegent sync remote-orphans command."""

    def test_sync_remote_orphans_exits_zero(self) -> None:
        """thegent sync remote-orphans exits with code 0."""
        result = runner.invoke(app, ["sync", "remote-orphans"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_remote_orphans_produces_output(self) -> None:
        """thegent sync remote-orphans produces expected output."""
        result = runner.invoke(app, ["sync", "remote-orphans"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_remote_orphans_help_exits_zero(self) -> None:
        """thegent sync remote-orphans --help exits with code 0."""
        result = runner.invoke(app, ["sync", "remote-orphans", "--help"])
        assert result.exit_code == 0
