"""
E2E test for: thegent project doctor

Agent Journey: Agent executes thegent project doctor command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestRecoverStatus:
    """E2E tests for thegent project doctor command."""

    def test_recover_status_exits_zero(self) -> None:
        """thegent project doctor exits with code 0."""
        result = runner.invoke(app, ["recover", "status"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_recover_status_produces_output(self) -> None:
        """thegent project doctor produces expected output."""
        result = runner.invoke(app, ["recover", "status"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_recover_status_help_exits_zero(self) -> None:
        """thegent project doctor --help exits with code 0."""
        result = runner.invoke(app, ["recover", "status", "--help"])
        assert result.exit_code == 0
