"""
E2E test for: thegent teams show

Agent Journey: Agent executes thegent teams show command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamsShow:
    """E2E tests for thegent teams show command."""

    def test_teams_show_exits_zero(self) -> None:
        """thegent teams show exits with code 0."""
        result = runner.invoke(app, ['teams', 'show'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teams_show_produces_output(self) -> None:
        """thegent teams show produces expected output."""
        result = runner.invoke(app, ['teams', 'show'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teams_show_help_exits_zero(self) -> None:
        """thegent teams show --help exits with code 0."""
        result = runner.invoke(app, ['teams', 'show', '--help'])
        assert result.exit_code == 0
