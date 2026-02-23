"""
E2E test for: thegent sync health

Agent Journey: Agent executes thegent sync health command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncHealth:
    """E2E tests for thegent sync health command."""

    def test_sync_health_exits_zero(self) -> None:
        """thegent sync health exits with code 0."""
        result = runner.invoke(app, ["sync", "health"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_health_produces_output(self) -> None:
        """thegent sync health produces expected output."""
        result = runner.invoke(app, ["sync", "health"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_health_help_exits_zero(self) -> None:
        """thegent sync health --help exits with code 0."""
        result = runner.invoke(app, ["sync", "health", "--help"])
        assert result.exit_code == 0
