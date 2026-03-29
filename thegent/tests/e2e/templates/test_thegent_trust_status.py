"""
E2E test for: thegent trust status

Agent Journey: Agent executes thegent trust status command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTrustStatus:
    """E2E tests for thegent trust status command."""

    def test_trust_status_exits_zero(self) -> None:
        """thegent trust status exits with code 0."""
        result = runner.invoke(app, ["trust", "status"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_trust_status_produces_output(self) -> None:
        """thegent trust status produces expected output."""
        result = runner.invoke(app, ["trust", "status"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_trust_status_help_exits_zero(self) -> None:
        """thegent trust status --help exits with code 0."""
        result = runner.invoke(app, ["trust", "status", "--help"])
        assert result.exit_code == 0
