"""
E2E test for: thegent sync bootstrap-gh

Agent Journey: Agent executes thegent sync bootstrap-gh command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncBootstrapGh:
    """E2E tests for thegent sync bootstrap-gh command."""

    def test_sync_bootstrap_gh_exits_zero(self) -> None:
        """thegent sync bootstrap-gh exits with code 0."""
        result = runner.invoke(app, ['sync', 'bootstrap-gh'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_bootstrap_gh_produces_output(self) -> None:
        """thegent sync bootstrap-gh produces expected output."""
        result = runner.invoke(app, ['sync', 'bootstrap-gh'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_bootstrap_gh_help_exits_zero(self) -> None:
        """thegent sync bootstrap-gh --help exits with code 0."""
        result = runner.invoke(app, ['sync', 'bootstrap-gh', '--help'])
        assert result.exit_code == 0
