"""
E2E test for: thegent learning promote

Agent Journey: Agent executes thegent learning promote command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestLearningPromote:
    """E2E tests for thegent learning promote command."""

    def test_learning_promote_exits_zero(self) -> None:
        """thegent learning promote exits with code 0."""
        result = runner.invoke(app, ['learning', 'promote'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_learning_promote_produces_output(self) -> None:
        """thegent learning promote produces expected output."""
        result = runner.invoke(app, ['learning', 'promote'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_learning_promote_help_exits_zero(self) -> None:
        """thegent learning promote --help exits with code 0."""
        result = runner.invoke(app, ['learning', 'promote', '--help'])
        assert result.exit_code == 0
