"""
E2E test for: thegent sys setup project init

Agent Journey: Agent executes thegent sys setup project init command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


def run_sys_setup_project_init() -> str:
    """Run sys setup project init in an isolated temp directory."""
    with tempfile.TemporaryDirectory(prefix="thegent-sys-setup-init-") as project_path:
        project_name = f"thegent-test-project-{Path(project_path).name}"
        result = runner.invoke(
            app,
            [
                "sys",
                "setup",
                "project",
                "init",
                "--name",
                project_name,
                "--path",
                project_path,
            ],
        )
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"
        return result.stdout


@pytest.mark.e2e
class TestSysSetupProjectInit:
    """E2E tests for thegent sys setup project init command."""

    def test_sys_setup_project_init_exits_zero(self) -> None:
        """thegent sys setup project init exits with code 0."""
        run_sys_setup_project_init()

    def test_sys_setup_project_init_produces_output(self) -> None:
        """thegent sys setup project init produces expected output."""
        output = run_sys_setup_project_init()
        # TODO: Add specific output assertions based on command behavior
        assert len(output) > 0

    def test_sys_setup_project_init_help_exits_zero(self) -> None:
        """thegent sys setup project init --help exits with code 0."""
        result = runner.invoke(app, ['sys', 'setup', 'project', 'init', '--help'])
        assert result.exit_code == 0
