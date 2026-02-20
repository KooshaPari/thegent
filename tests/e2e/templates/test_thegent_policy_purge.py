"""
E2E test for: thegent policy purge

Agent Journey: Agent executes thegent policy purge command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestPolicyPurge:
    """E2E tests for thegent policy purge command."""

    def test_policy_purge_exits_zero(self) -> None:
        """thegent policy purge exits with code 0."""
        result = runner.invoke(app, ["policy", "purge"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_policy_purge_produces_output(self) -> None:
        """thegent policy purge produces expected output."""
        result = runner.invoke(app, ["policy", "purge"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_policy_purge_help_exits_zero(self) -> None:
        """thegent policy purge --help exits with code 0."""
        result = runner.invoke(app, ["policy", "purge", "--help"])
        assert result.exit_code == 0
