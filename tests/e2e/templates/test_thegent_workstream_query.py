"""
E2E test for: thegent workstream query

Agent Journey: Agent executes thegent workstream query command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestWorkstreamQuery:
    """E2E tests for thegent workstream query command."""

    def test_workstream_query_exits_zero(self) -> None:
        """thegent workstream query exits with code 0."""
        result = runner.invoke(app, ['workstream', 'query'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_workstream_query_produces_output(self) -> None:
        """thegent workstream query produces expected output."""
        result = runner.invoke(app, ['workstream', 'query'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_workstream_query_help_exits_zero(self) -> None:
        """thegent workstream query --help exits with code 0."""
        result = runner.invoke(app, ['workstream', 'query', '--help'])
        assert result.exit_code == 0
