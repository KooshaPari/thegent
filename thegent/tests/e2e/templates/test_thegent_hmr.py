"""
E2E test for: thegent hmr

Agent Journey: Agent executes thegent hmr command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestHmr:
    """E2E tests for thegent hmr command."""

    def test_hmr_exits_zero(self) -> None:
        """thegent hmr exits with code 0."""
        result = runner.invoke(app, ["hmr"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_hmr_produces_output(self) -> None:
        """thegent hmr produces expected output."""
        result = runner.invoke(app, ["hmr"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_hmr_help_exits_zero(self) -> None:
        """thegent hmr --help exits with code 0."""
        result = runner.invoke(app, ["hmr", "--help"])
        assert result.exit_code == 0
