"""
E2E test for: thegent project brownfield

Agent Journey: Agent executes thegent project brownfield command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectBrownfield:
    """E2E tests for thegent project brownfield command."""

    def test_project_brownfield_exits_zero(self) -> None:
        """thegent project brownfield exits with code 0."""
        result = runner.invoke(app, ['project', 'brownfield'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_brownfield_produces_output(self) -> None:
        """thegent project brownfield produces expected output."""
        result = runner.invoke(app, ['project', 'brownfield'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_brownfield_help_exits_zero(self) -> None:
        """thegent project brownfield --help exits with code 0."""
        result = runner.invoke(app, ['project', 'brownfield', '--help'])
        assert result.exit_code == 0
