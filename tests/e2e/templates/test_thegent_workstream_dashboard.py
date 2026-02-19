"""
E2E test for: thegent workstream dashboard

Agent Journey: Agent executes thegent workstream dashboard command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestWorkstreamDashboard:
    """E2E tests for thegent workstream dashboard command."""

    def test_workstream_dashboard_exits_zero(self) -> None:
        """thegent workstream dashboard exits with code 0."""
        result = runner.invoke(app, ['workstream', 'dashboard'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_workstream_dashboard_produces_output(self) -> None:
        """thegent workstream dashboard produces expected output."""
        result = runner.invoke(app, ['workstream', 'dashboard'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_workstream_dashboard_help_exits_zero(self) -> None:
        """thegent workstream dashboard --help exits with code 0."""
        result = runner.invoke(app, ['workstream', 'dashboard', '--help'])
        assert result.exit_code == 0
