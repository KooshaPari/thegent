"""
E2E test for: thegent policy check

Agent Journey: Agent executes thegent policy check command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestPolicyCheck:
    """E2E tests for thegent policy check command."""

    def test_policy_check_exits_zero(self) -> None:
        """thegent policy check exits with code 0."""
        result = runner.invoke(app, ['policy', 'check'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_policy_check_produces_output(self) -> None:
        """thegent policy check produces expected output."""
        result = runner.invoke(app, ['policy', 'check'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_policy_check_help_exits_zero(self) -> None:
        """thegent policy check --help exits with code 0."""
        result = runner.invoke(app, ['policy', 'check', '--help'])
        assert result.exit_code == 0
