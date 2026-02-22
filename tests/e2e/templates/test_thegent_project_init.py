"""
E2E test for: thegent project init

Agent Journey: Agent executes thegent project init command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectInit:
    """E2E tests for thegent project init command."""

    def test_project_init_exits_zero(self) -> None:
        """thegent project init exits with code 0."""
        result = runner.invoke(app, ['project', 'init'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_init_produces_output(self) -> None:
        """thegent project init produces expected output."""
        result = runner.invoke(app, ['project', 'init'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_init_help_exits_zero(self) -> None:
        """thegent project init --help exits with code 0."""
        result = runner.invoke(app, ['project', 'init', '--help'])
        assert result.exit_code == 0
