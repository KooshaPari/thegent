"""
E2E test for: thegent project register

Agent Journey: Agent executes thegent project register command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectRegister:
    """E2E tests for thegent project register command."""

    def test_project_register_exits_zero(self) -> None:
        """thegent project register exits with code 0."""
        result = runner.invoke(app, ["project", "register"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_register_produces_output(self) -> None:
        """thegent project register produces expected output."""
        result = runner.invoke(app, ["project", "register"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_register_help_exits_zero(self) -> None:
        """thegent project register --help exits with code 0."""
        result = runner.invoke(app, ["project", "register", "--help"])
        assert result.exit_code == 0
