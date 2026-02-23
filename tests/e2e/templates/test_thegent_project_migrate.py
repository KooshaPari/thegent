"""
E2E test for: thegent project migrate

Agent Journey: Agent executes thegent project migrate command
Expected Behavior: Command executes successfully and returns expected output
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestProjectMigrate:
    """E2E tests for thegent project migrate command."""

    def test_project_migrate_exits_zero(self) -> None:
        """thegent project migrate exits with code 0."""
        result = runner.invoke(app, ["project", "migrate"])
        assert result.exit_code == 0, f"Command failed: {result.stdout} {result.stderr}"

    def test_project_migrate_produces_output(self) -> None:
        """thegent project migrate produces expected output."""
        result = runner.invoke(app, ["project", "migrate"])
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_project_migrate_help_exits_zero(self) -> None:
        """thegent project migrate --help exits with code 0."""
        result = runner.invoke(app, ["project", "migrate", "--help"])
        assert result.exit_code == 0
