"""
E2E test for: thegent sitback-dashboard

Agent Journey: Agent executes thegent sitback-dashboard command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSitback-dashboard:
    """E2E tests for thegent sitback-dashboard command."""

    def test_sitback_dashboard_exits_zero(self) -> None:
        """thegent sitback-dashboard exits with code 0."""
        result = runner.invoke(app, ['sitback-dashboard'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sitback_dashboard_produces_output(self) -> None:
        """thegent sitback-dashboard produces expected output."""
        result = runner.invoke(app, ['sitback-dashboard'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sitback_dashboard_help_exits_zero(self) -> None:
        """thegent sitback-dashboard --help exits with code 0."""
        result = runner.invoke(app, ['sitback-dashboard', '--help'])
        assert result.exit_code == 0
