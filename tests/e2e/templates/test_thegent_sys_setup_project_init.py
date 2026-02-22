"""
E2E test for: thegent sys setup project init

Agent Journey: Agent executes thegent sys setup project init command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSysSetupProjectInit:
    """E2E tests for thegent sys setup project init command."""

    def test_sys_setup_project_init_exits_zero(self) -> None:
        """thegent sys setup project init exits with code 0."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'init'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sys_setup_project_init_produces_output(self) -> None:
        """thegent sys setup project init produces expected output."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'init'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sys_setup_project_init_help_exits_zero(self) -> None:
        """thegent sys setup project init --help exits with code 0."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'init', '--help'])
        assert result.exit_code == 0
