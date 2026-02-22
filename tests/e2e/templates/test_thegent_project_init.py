"""
E2E test for: thegent project init

Agent Journey: Agent executes thegent project init command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


def run_project_init() -> str:
    """Run project init in an isolated temp directory and return CLI output."""
    with tempfile.TemporaryDirectory(prefix="thegent-project-init-") as project_path:
        project_name = f"thegent-test-project-{Path(project_path).name}"
        result = runner.invoke(
            app,
            [
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
class TestProjectInit:
    """E2E tests for thegent project init command."""

    def test_project_init_exits_zero(self) -> None:
        """thegent project init exits with code 0."""
        run_project_init()

    def test_project_init_produces_output(self) -> None:
        """thegent project init produces expected output."""
        output = run_project_init()
        assert len(output) > 0

    def test_project_init_help_exits_zero(self) -> None:
        """thegent project init --help exits with code 0."""
        result = runner.invoke(app, ['project', 'init', '--help'])
        assert result.exit_code == 0
