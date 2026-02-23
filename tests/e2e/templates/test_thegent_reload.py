"""
E2E test for: thegent reload

Agent Journey: Agent executes thegent reload command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestReload:
    """E2E tests for thegent reload command."""

    def test_reload_exits_zero(self) -> None:
        """thegent reload exits with code 0."""
        result = runner.invoke(app, ['reload'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_reload_produces_output(self) -> None:
        """thegent reload produces expected output."""
        result = runner.invoke(app, ['reload'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_reload_help_exits_zero(self) -> None:
        """thegent reload --help exits with code 0."""
        result = runner.invoke(app, ['reload', '--help'])
        assert result.exit_code == 0
