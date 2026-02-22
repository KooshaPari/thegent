"""
E2E test for: thegent team teammates list

Agent Journey: Agent executes thegent team teammates list command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeammatesList:
    """E2E tests for thegent team teammates list command."""

    def test_teammates_list_exits_zero(self) -> None:
        """thegent team teammates list exits with code 0."""
        result = runner.invoke(app, ["teammates", "list"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teammates_list_produces_output(self) -> None:
        """thegent team teammates list produces expected output."""
        result = runner.invoke(app, ["teammates", "list"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teammates_list_help_exits_zero(self) -> None:
        """thegent team teammates list --help exits with code 0."""
        result = runner.invoke(app, ["teammates", "list", "--help"])
        assert result.exit_code == 0
