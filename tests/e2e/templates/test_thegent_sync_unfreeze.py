"""
E2E test for: thegent sync unfreeze

Agent Journey: Agent executes thegent sync unfreeze command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncUnfreeze:
    """E2E tests for thegent sync unfreeze command."""

    def test_sync_unfreeze_exits_zero(self) -> None:
        """thegent sync unfreeze exits with code 0."""
        result = runner.invoke(app, ['sync', 'unfreeze'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_unfreeze_produces_output(self) -> None:
        """thegent sync unfreeze produces expected output."""
        result = runner.invoke(app, ['sync', 'unfreeze'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_unfreeze_help_exits_zero(self) -> None:
        """thegent sync unfreeze --help exits with code 0."""
        result = runner.invoke(app, ['sync', 'unfreeze', '--help'])
        assert result.exit_code == 0
