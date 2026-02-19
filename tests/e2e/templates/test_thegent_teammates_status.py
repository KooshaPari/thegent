"""
E2E test for: thegent teammates status

Agent Journey: Agent executes thegent teammates status command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTeammatesStatus:
    """E2E tests for thegent teammates status command."""

    def test_teammates_status_exits_zero(self) -> None:
        """thegent teammates status exits with code 0."""
        result = runner.invoke(app, ['teammates', 'status'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_teammates_status_produces_output(self) -> None:
        """thegent teammates status produces expected output."""
        result = runner.invoke(app, ['teammates', 'status'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_teammates_status_help_exits_zero(self) -> None:
        """thegent teammates status --help exits with code 0."""
        result = runner.invoke(app, ['teammates', 'status', '--help'])
        assert result.exit_code == 0
