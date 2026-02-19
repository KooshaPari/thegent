"""
E2E test for: thegent rules sync

Agent Journey: Agent executes thegent rules sync command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestRulesSync:
    """E2E tests for thegent rules sync command."""

    def test_rules_sync_exits_zero(self) -> None:
        """thegent rules sync exits with code 0."""
        result = runner.invoke(app, ['rules', 'sync'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_rules_sync_produces_output(self) -> None:
        """thegent rules sync produces expected output."""
        result = runner.invoke(app, ['rules', 'sync'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_rules_sync_help_exits_zero(self) -> None:
        """thegent rules sync --help exits with code 0."""
        result = runner.invoke(app, ['rules', 'sync', '--help'])
        assert result.exit_code == 0
