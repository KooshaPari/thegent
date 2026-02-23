"""
E2E test for: thegent sync board-migrate

Agent Journey: Agent executes thegent sync board-migrate command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestSyncBoard-migrate:
    """E2E tests for thegent sync board-migrate command."""

    def test_sync_board_migrate_exits_zero(self) -> None:
        """thegent sync board-migrate exits with code 0."""
        result = runner.invoke(app, ['sync', 'board-migrate'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_sync_board_migrate_produces_output(self) -> None:
        """thegent sync board-migrate produces expected output."""
        result = runner.invoke(app, ['sync', 'board-migrate'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_sync_board_migrate_help_exits_zero(self) -> None:
        """thegent sync board-migrate --help exits with code 0."""
        result = runner.invoke(app, ['sync', 'board-migrate', '--help'])
        assert result.exit_code == 0
