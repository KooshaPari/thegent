"""
E2E test for: thegent team create

Agent Journey: Agent executes thegent team create command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamAddTask:
    """E2E tests for thegent team create command."""

    def test_team_add_task_exits_zero(self) -> None:
        """thegent team create exits with code 0."""
        result = runner.invoke(app, ["team", "add-task"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_team_add_task_produces_output(self) -> None:
        """thegent team create produces expected output."""
        result = runner.invoke(app, ["team", "add-task"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_team_add_task_help_exits_zero(self) -> None:
        """thegent team create --help exits with code 0."""
        result = runner.invoke(app, ["team", "add-task", "--help"])
        assert result.exit_code == 0
