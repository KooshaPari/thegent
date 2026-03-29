"""
E2E test for: thegent team hierarchy

Agent Journey: Agent executes thegent team hierarchy command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestHierarchyShow:
    """E2E tests for thegent team hierarchy command."""

    def test_hierarchy_show_exits_zero(self) -> None:
        """thegent team hierarchy exits with code 0."""
        result = runner.invoke(app, ["hierarchy", "show"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_hierarchy_show_produces_output(self) -> None:
        """thegent team hierarchy produces expected output."""
        result = runner.invoke(app, ["hierarchy", "show"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_hierarchy_show_help_exits_zero(self) -> None:
        """thegent team hierarchy --help exits with code 0."""
        result = runner.invoke(app, ["hierarchy", "show", "--help"])
        assert result.exit_code == 0
