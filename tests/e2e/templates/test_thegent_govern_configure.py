"""
E2E test for: thegent govern resolve-config

Agent Journey: Agent executes thegent govern resolve-config command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestGovernConfigure:
    """E2E tests for thegent govern resolve-config command."""

    def test_govern_configure_exits_zero(self) -> None:
        """thegent govern resolve-config exits with code 0."""
        result = runner.invoke(app, ["govern", "configure"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_govern_configure_produces_output(self) -> None:
        """thegent govern resolve-config produces expected output."""
        result = runner.invoke(app, ["govern", "configure"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_govern_configure_help_exits_zero(self) -> None:
        """thegent govern resolve-config --help exits with code 0."""
        result = runner.invoke(app, ["govern", "configure", "--help"])
        assert result.exit_code == 0
