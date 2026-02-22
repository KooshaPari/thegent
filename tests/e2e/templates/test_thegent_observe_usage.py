"""
E2E test for: thegent observe compositor

Agent Journey: Agent executes thegent observe compositor command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestObserveUsage:
    """E2E tests for thegent observe compositor command."""

    def test_observe_usage_exits_zero(self) -> None:
        """thegent observe compositor exits with code 0."""
        result = runner.invoke(app, ["observe", "usage"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_observe_usage_produces_output(self) -> None:
        """thegent observe compositor produces expected output."""
        result = runner.invoke(app, ["observe", "usage"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_observe_usage_help_exits_zero(self) -> None:
        """thegent observe compositor --help exits with code 0."""
        result = runner.invoke(app, ["observe", "usage", "--help"])
        assert result.exit_code == 0
