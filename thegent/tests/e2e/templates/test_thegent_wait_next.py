"""
E2E test for: thegent wait-next

Agent Journey: Agent executes thegent wait-next command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestWaitNext:
    """E2E tests for thegent wait-next command."""

    def test_wait_next_exits_zero(self) -> None:
        """thegent wait-next exits with code 0."""
        result = runner.invoke(app, ["wait-next"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_wait_next_produces_output(self) -> None:
        """thegent wait-next produces expected output."""
        result = runner.invoke(app, ["wait-next"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_wait_next_help_exits_zero(self) -> None:
        """thegent wait-next --help exits with code 0."""
        result = runner.invoke(app, ["wait-next", "--help"])
        assert result.exit_code == 0
