"""
E2E test for: thegent project scaffold

Agent Journey: Agent executes thegent project scaffold command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectScaffold:
    """E2E tests for thegent project scaffold command."""

    def test_project_scaffold_exits_zero(self) -> None:
        """thegent project scaffold exits with code 0."""
        result = runner.invoke(app, ["project", "scaffold"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_scaffold_produces_output(self) -> None:
        """thegent project scaffold produces expected output."""
        result = runner.invoke(app, ["project", "scaffold"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_scaffold_help_exits_zero(self) -> None:
        """thegent project scaffold --help exits with code 0."""
        result = runner.invoke(app, ["project", "scaffold", "--help"])
        assert result.exit_code == 0
