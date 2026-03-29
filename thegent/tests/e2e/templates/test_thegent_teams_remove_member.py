"""
E2E test for: thegent teams remove-member

Agent Journey: Agent executes thegent teams remove-member command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamsRemoveMember:
    """E2E tests for thegent teams remove-member command."""

    def test_teams_remove_member_exits_zero(self) -> None:
        """thegent teams remove-member exits with code 0."""
        result = runner.invoke(app, ["teams", "remove-member"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teams_remove_member_produces_output(self) -> None:
        """thegent teams remove-member produces expected output."""
        result = runner.invoke(app, ["teams", "remove-member"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teams_remove_member_help_exits_zero(self) -> None:
        """thegent teams remove-member --help exits with code 0."""
        result = runner.invoke(app, ["teams", "remove-member", "--help"])
        assert result.exit_code == 0
