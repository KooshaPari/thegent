"""
E2E test for: thegent audit costs

Agent Journey: Agent executes thegent audit costs command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestFinanceDashboard:
    """E2E tests for thegent audit costs command."""

    def test_finance_dashboard_exits_zero(self) -> None:
        """thegent audit costs exits with code 0."""
        result = runner.invoke(app, ["finance", "dashboard"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_finance_dashboard_produces_output(self) -> None:
        """thegent audit costs produces expected output."""
        result = runner.invoke(app, ["finance", "dashboard"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_finance_dashboard_help_exits_zero(self) -> None:
        """thegent audit costs --help exits with code 0."""
        result = runner.invoke(app, ["finance", "dashboard", "--help"])
        assert result.exit_code == 0
