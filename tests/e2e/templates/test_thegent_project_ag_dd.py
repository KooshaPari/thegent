"""
E2E test for: thegent project ag-dd

Agent Journey: Agent executes thegent project ag-dd command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectAgDd:
    """E2E tests for thegent project ag-dd command."""

    def test_project_ag_dd_exits_zero(self) -> None:
        """thegent project ag-dd exits with code 0."""
        result = runner.invoke(app, ['project', 'ag-dd'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_ag_dd_produces_output(self) -> None:
        """thegent project ag-dd produces expected output."""
        result = runner.invoke(app, ['project', 'ag-dd'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_ag_dd_help_exits_zero(self) -> None:
        """thegent project ag-dd --help exits with code 0."""
        result = runner.invoke(app, ['project', 'ag-dd', '--help'])
        assert result.exit_code == 0
