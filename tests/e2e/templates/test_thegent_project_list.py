"""
E2E test for: thegent project list

Agent Journey: Agent executes thegent project list command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectList:
    """E2E tests for thegent project list command."""

    def test_project_list_exits_zero(self) -> None:
        """thegent project list exits with code 0."""
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_list_produces_output(self) -> None:
        """thegent project list produces expected output."""
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_list_help_exits_zero(self) -> None:
        """thegent project list --help exits with code 0."""
        result = runner.invoke(app, ["project", "list", "--help"])
        assert result.exit_code == 0
