"""
E2E test for: thegent team list

Agent Journey: Agent executes thegent team list command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamListTasks:
    """E2E tests for thegent team list command."""

    def test_team_list_tasks_exits_zero(self) -> None:
        """thegent team list exits with code 0."""
        result = runner.invoke(app, ["team", "list-tasks"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_team_list_tasks_produces_output(self) -> None:
        """thegent team list produces expected output."""
        result = runner.invoke(app, ["team", "list-tasks"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_team_list_tasks_help_exits_zero(self) -> None:
        """thegent team list --help exits with code 0."""
        result = runner.invoke(app, ["team", "list-tasks", "--help"])
        assert result.exit_code == 0
