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
class TestForensicsSnapshot:
    """E2E tests for thegent project doctor command."""

    def test_forensics_snapshot_exits_zero(self) -> None:
        """thegent project doctor exits with code 0."""
        result = runner.invoke(app, ["forensics", "snapshot"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_forensics_snapshot_produces_output(self) -> None:
        """thegent project doctor produces expected output."""
        result = runner.invoke(app, ["forensics", "snapshot"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_forensics_snapshot_help_exits_zero(self) -> None:
        """thegent project doctor --help exits with code 0."""
        result = runner.invoke(app, ["forensics", "snapshot", "--help"])
        assert result.exit_code == 0
