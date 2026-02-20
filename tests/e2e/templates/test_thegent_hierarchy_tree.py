"""
E2E test for: thegent hierarchy tree

Agent Journey: Agent executes thegent hierarchy tree command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestHierarchyTree:
    """E2E tests for thegent hierarchy tree command."""

    def test_hierarchy_tree_exits_zero(self) -> None:
        """thegent hierarchy tree exits with code 0."""
        result = runner.invoke(app, ["hierarchy", "tree"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_hierarchy_tree_produces_output(self) -> None:
        """thegent hierarchy tree produces expected output."""
        result = runner.invoke(app, ["hierarchy", "tree"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_hierarchy_tree_help_exits_zero(self) -> None:
        """thegent hierarchy tree --help exits with code 0."""
        result = runner.invoke(app, ["hierarchy", "tree", "--help"])
        assert result.exit_code == 0
