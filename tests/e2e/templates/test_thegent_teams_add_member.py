"""
E2E test for: thegent teams add-member

Agent Journey: Agent executes thegent teams add-member command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeamsAddMember:
    """E2E tests for thegent teams add-member command."""

    def test_teams_add_member_exits_zero(self) -> None:
        """thegent teams add-member exits with code 0."""
        result = runner.invoke(app, ["teams", "add-member"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teams_add_member_produces_output(self) -> None:
        """thegent teams add-member produces expected output."""
        result = runner.invoke(app, ["teams", "add-member"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teams_add_member_help_exits_zero(self) -> None:
        """thegent teams add-member --help exits with code 0."""
        result = runner.invoke(app, ["teams", "add-member", "--help"])
        assert result.exit_code == 0
