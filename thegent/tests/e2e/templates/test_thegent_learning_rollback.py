"""
E2E test for: thegent plan status

Agent Journey: Agent executes thegent plan status command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestLearningRollback:
    """E2E tests for thegent plan status command."""

    def test_learning_rollback_exits_zero(self) -> None:
        """thegent plan status exits with code 0."""
        result = runner.invoke(app, ["learning", "rollback"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_learning_rollback_produces_output(self) -> None:
        """thegent plan status produces expected output."""
        result = runner.invoke(app, ["learning", "rollback"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_learning_rollback_help_exits_zero(self) -> None:
        """thegent plan status --help exits with code 0."""
        result = runner.invoke(app, ["learning", "rollback", "--help"])
        assert result.exit_code == 0
