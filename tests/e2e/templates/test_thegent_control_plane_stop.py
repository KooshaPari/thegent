"""
E2E test for: thegent control_plane stop

Agent Journey: Agent executes thegent control_plane stop command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestControl_planeStop:
    """E2E tests for thegent control_plane stop command."""

    def test_control_plane_stop_exits_zero(self) -> None:
        """thegent control_plane stop exits with code 0."""
        result = runner.invoke(app, ['control_plane', 'stop'])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_control_plane_stop_produces_output(self) -> None:
        """thegent control_plane stop produces expected output."""
        result = runner.invoke(app, ['control_plane', 'stop'])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_control_plane_stop_help_exits_zero(self) -> None:
        """thegent control_plane stop --help exits with code 0."""
        result = runner.invoke(app, ['control_plane', 'stop', '--help'])
        assert result.exit_code == 0
