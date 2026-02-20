"""
E2E test for: thegent takeover

Agent Journey: Agent executes thegent takeover command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestTakeover:
    """E2E tests for thegent takeover command."""

    def test_takeover_exits_zero(self) -> None:
        """thegent takeover exits with code 0."""
        result = runner.invoke(app, ["takeover"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_takeover_produces_output(self) -> None:
        """thegent takeover produces expected output."""
        result = runner.invoke(app, ["takeover"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_takeover_help_exits_zero(self) -> None:
        """thegent takeover --help exits with code 0."""
        result = runner.invoke(app, ["takeover", "--help"])
        assert result.exit_code == 0
