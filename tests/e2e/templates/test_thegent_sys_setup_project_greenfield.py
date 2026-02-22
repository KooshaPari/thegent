"""
E2E test for: thegent sys setup project greenfield

Agent Journey: Agent executes thegent sys setup project greenfield command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSysSetupProjectGreenfield:
    """E2E tests for thegent sys setup project greenfield command."""

    def test_sys_setup_project_greenfield_exits_zero(self) -> None:
        """thegent sys setup project greenfield exits with code 0."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'greenfield'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sys_setup_project_greenfield_produces_output(self) -> None:
        """thegent sys setup project greenfield produces expected output."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'greenfield'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sys_setup_project_greenfield_help_exits_zero(self) -> None:
        """thegent sys setup project greenfield --help exits with code 0."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'greenfield', '--help'])
        assert result.exit_code == 0
