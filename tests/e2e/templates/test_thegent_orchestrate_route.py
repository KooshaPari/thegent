"""
E2E test for: thegent orchestrate route

Agent Journey: Agent executes thegent orchestrate route command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestOrchestrateRoute:
    """E2E tests for thegent orchestrate route command."""

    def test_orchestrate_route_exits_zero(self) -> None:
        """thegent orchestrate route exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "route"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_orchestrate_route_produces_output(self) -> None:
        """thegent orchestrate route produces expected output."""
        result = runner.invoke(app, ["orchestrate", "route"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_orchestrate_route_help_exits_zero(self) -> None:
        """thegent orchestrate route --help exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "route", "--help"])
        assert result.exit_code == 0
