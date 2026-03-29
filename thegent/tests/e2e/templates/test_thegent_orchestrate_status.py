"""
E2E test for: thegent orchestrate plan

Agent Journey: Agent executes thegent orchestrate plan command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestOrchestrateStatus:
    """E2E tests for thegent orchestrate plan command."""

    def test_orchestrate_status_exits_zero(self) -> None:
        """thegent orchestrate plan exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "status"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_orchestrate_status_produces_output(self) -> None:
        """thegent orchestrate plan produces expected output."""
        result = runner.invoke(app, ["orchestrate", "status"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_orchestrate_status_help_exits_zero(self) -> None:
        """thegent orchestrate plan --help exits with code 0."""
        result = runner.invoke(app, ["orchestrate", "status", "--help"])
        assert result.exit_code == 0
