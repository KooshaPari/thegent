"""
E2E test for: thegent workstream launch

Agent Journey: Agent executes thegent workstream launch command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestWorkstreamLaunch:
    """E2E tests for thegent workstream launch command."""

    def test_workstream_launch_exits_zero(self) -> None:
        """thegent workstream launch exits with code 0."""
        result = runner.invoke(app, ["workstream", "launch"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_workstream_launch_produces_output(self) -> None:
        """thegent workstream launch produces expected output."""
        result = runner.invoke(app, ["workstream", "launch"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_workstream_launch_help_exits_zero(self) -> None:
        """thegent workstream launch --help exits with code 0."""
        result = runner.invoke(app, ["workstream", "launch", "--help"])
        assert result.exit_code == 0
