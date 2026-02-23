"""
E2E test for: thegent sync conflicts

Agent Journey: Agent executes thegent sync conflicts command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncConflicts:
    """E2E tests for thegent sync conflicts command."""

    def test_sync_conflicts_exits_zero(self) -> None:
        """thegent sync conflicts exits with code 0."""
        result = runner.invoke(app, ['sync', 'conflicts'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_conflicts_produces_output(self) -> None:
        """thegent sync conflicts produces expected output."""
        result = runner.invoke(app, ['sync', 'conflicts'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_conflicts_help_exits_zero(self) -> None:
        """thegent sync conflicts --help exits with code 0."""
        result = runner.invoke(app, ['sync', 'conflicts', '--help'])
        assert result.exit_code == 0
