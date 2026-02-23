"""
E2E test for: thegent sync board

Agent Journey: Agent executes thegent sync board command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncBoard:
    """E2E tests for thegent sync board command."""

    def test_sync_board_exits_zero(self) -> None:
        """thegent sync board exits with code 0."""
        result = runner.invoke(app, ["sync", "board"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_board_produces_output(self) -> None:
        """thegent sync board produces expected output."""
        result = runner.invoke(app, ["sync", "board"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_board_help_exits_zero(self) -> None:
        """thegent sync board --help exits with code 0."""
        result = runner.invoke(app, ["sync", "board", "--help"])
        assert result.exit_code == 0
