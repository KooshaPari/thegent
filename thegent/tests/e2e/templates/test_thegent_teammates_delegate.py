"""
E2E test for: thegent team teammates delegate

Agent Journey: Agent executes thegent team teammates delegate command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeammatesDelegate:
    """E2E tests for thegent team teammates delegate command."""

    def test_teammates_delegate_exits_zero(self) -> None:
        """thegent team teammates delegate exits with code 0."""
        result = runner.invoke(app, ["teammates", "delegate"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teammates_delegate_produces_output(self) -> None:
        """thegent team teammates delegate produces expected output."""
        result = runner.invoke(app, ["teammates", "delegate"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teammates_delegate_help_exits_zero(self) -> None:
        """thegent team teammates delegate --help exits with code 0."""
        result = runner.invoke(app, ["teammates", "delegate", "--help"])
        assert result.exit_code == 0
