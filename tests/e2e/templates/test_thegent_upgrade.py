"""
E2E test for: thegent upgrade

Agent Journey: Agent executes thegent upgrade command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestUpgrade:
    """E2E tests for thegent upgrade command."""

    def test_upgrade_exits_zero(self) -> None:
        """thegent upgrade exits with code 0."""
        result = runner.invoke(app, ['upgrade'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_upgrade_produces_output(self) -> None:
        """thegent upgrade produces expected output."""
        result = runner.invoke(app, ['upgrade'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_upgrade_help_exits_zero(self) -> None:
        """thegent upgrade --help exits with code 0."""
        result = runner.invoke(app, ['upgrade', '--help'])
        assert result.exit_code == 0
