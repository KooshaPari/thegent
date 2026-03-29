"""
E2E test for: thegent project none

Agent Journey: Agent executes thegent project none command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectNone:
    """E2E tests for thegent project none command."""

    def test_project_none_exits_zero(self) -> None:
        """thegent project none exits with code 0."""
        result = runner.invoke(app, ["project", "none"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_none_produces_output(self) -> None:
        """thegent project none produces expected output."""
        result = runner.invoke(app, ["project", "none"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_none_help_exits_zero(self) -> None:
        """thegent project none --help exits with code 0."""
        result = runner.invoke(app, ["project", "none", "--help"])
        assert result.exit_code == 0
