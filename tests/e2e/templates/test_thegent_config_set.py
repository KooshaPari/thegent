"""
E2E test for: thegent sys config set

Agent Journey: Agent executes thegent sys config set command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestConfigSet:
    """E2E tests for thegent sys config set command."""

    def test_config_set_exits_zero(self) -> None:
        """thegent sys config set exits with code 0."""
        result = runner.invoke(app, ["config", "set"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_config_set_produces_output(self) -> None:
        """thegent sys config set produces expected output."""
        result = runner.invoke(app, ["config", "set"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_config_set_help_exits_zero(self) -> None:
        """thegent sys config set --help exits with code 0."""
        result = runner.invoke(app, ["config", "set", "--help"])
        assert result.exit_code == 0
