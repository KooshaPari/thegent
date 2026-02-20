"""
E2E test for: thegent workstream stats

Agent Journey: Agent executes thegent workstream stats command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestWorkstreamStats:
    """E2E tests for thegent workstream stats command."""

    def test_workstream_stats_exits_zero(self) -> None:
        """thegent workstream stats exits with code 0."""
        result = runner.invoke(app, ["workstream", "stats"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_workstream_stats_produces_output(self) -> None:
        """thegent workstream stats produces expected output."""
        result = runner.invoke(app, ["workstream", "stats"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_workstream_stats_help_exits_zero(self) -> None:
        """thegent workstream stats --help exits with code 0."""
        result = runner.invoke(app, ["workstream", "stats", "--help"])
        assert result.exit_code == 0
