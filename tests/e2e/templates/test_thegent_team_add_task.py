"""
E2E test for: thegent team add-task

Agent Journey: Agent executes thegent team add-task command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamAdd-task:
    """E2E tests for thegent team add-task command."""

    def test_team_add_task_exits_zero(self) -> None:
        """thegent team add-task exits with code 0."""
        result = runner.invoke(app, ['team', 'add-task'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_team_add_task_produces_output(self) -> None:
        """thegent team add-task produces expected output."""
        result = runner.invoke(app, ['team', 'add-task'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_team_add_task_help_exits_zero(self) -> None:
        """thegent team add-task --help exits with code 0."""
        result = runner.invoke(app, ['team', 'add-task', '--help'])
        assert result.exit_code == 0
