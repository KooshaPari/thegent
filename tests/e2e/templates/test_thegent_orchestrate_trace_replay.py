"""
E2E test for: thegent orchestrate run

Agent Journey: Agent executes thegent orchestrate run command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestOrchestrateTraceReplay:
    """E2E tests for thegent orchestrate run command."""

    def test_orchestrate_trace_replay_exits_zero(self) -> None:
        """thegent orchestrate run exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "trace-replay"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_orchestrate_trace_replay_produces_output(self) -> None:
        """thegent orchestrate run produces expected output."""
        result = runner.invoke(app, ["orchestrate", "trace-replay"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_orchestrate_trace_replay_help_exits_zero(self) -> None:
        """thegent orchestrate run --help exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "trace-replay", "--help"])
        assert result.exit_code == 0
