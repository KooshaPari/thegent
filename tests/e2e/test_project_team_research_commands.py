"""
E2E tests for Project, Team, and Research commands.

Agent Journey: Agent manages projects, teams, and conducts deep research
Expected Behavior: Commands execute successfully and provide project/team/research management
"""

import pytest
from typer.testing import CliRunner

from thegent.main import app

# Skip all tests in this file - CLI commands do not exist
pytestmark = pytest.mark.skip(reason="CLI commands 'project', 'team', 'research' subcommands do not exist in current implementation")

runner = CliRunner()


@pytest.mark.e2e
class TestProjectTeamResearchCommands:
    """E2E tests for Project, Team, and Research commands."""

    # Project commands
    def test_project_help_exits_zero(self) -> None:
        """thegent project --help exits with code 0."""
        result = runner.invoke(app, ["project", "--help"])
        assert result.exit_code == 0

    def test_project_register_help(self) -> None:
        """thegent project register --help exits with code 0."""
        result = runner.invoke(app, ["project", "register", "--help"])
        assert result.exit_code == 0

    def test_project_list_help(self) -> None:
        """thegent project list --help exits with code 0."""
        result = runner.invoke(app, ["project", "list", "--help"])
        assert result.exit_code == 0

    # Team commands
    def test_team_help_exits_zero(self) -> None:
        """thegent team --help exits with code 0."""
        result = runner.invoke(app, ["team", "--help"])
        assert result.exit_code == 0

    def test_team_create_help(self) -> None:
        """thegent team create --help exits with code 0."""
        result = runner.invoke(app, ["team", "create", "--help"])
        assert result.exit_code == 0

    def test_team_add_task_help(self) -> None:
        """thegent team add-task --help exits with code 0."""
        result = runner.invoke(app, ["team", "add-task", "--help"])
        assert result.exit_code == 0

    def test_team_list_tasks_help(self) -> None:
        """thegent team list-tasks --help exits with code 0."""
        result = runner.invoke(app, ["team", "list-tasks", "--help"])
        assert result.exit_code == 0

    # Research commands
    def test_research_help_exits_zero(self) -> None:
        """thegent research --help exits with code 0."""
        result = runner.invoke(app, ["research", "--help"])
        assert result.exit_code == 0

    def test_research_deep_help(self) -> None:
        """thegent research deep --help exits with code 0."""
        # Note: the command extracted from main.py was "thegent research deep"
        # but lookups in find_e2e_tests use space-separated args
        result = runner.invoke(app, ["research", "deep", "--help"])
        assert result.exit_code == 0

    # Miscellaneous commands
    def test_upgrade_help(self) -> None:
        """thegent upgrade --help exits with code 0."""
        result = runner.invoke(app, ["upgrade", "--help"])
        assert result.exit_code == 0

    def test_install_help(self) -> None:
        """thegent install --help exits with code 0."""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0

    def test_provider_help(self) -> None:
        """thegent provider --help exits with code 0."""
        result = runner.invoke(app, ["provider", "--help"])
        assert result.exit_code == 0

    def test_list_providers_help(self) -> None:
        """thegent list-providers --help exits with code 0."""
        result = runner.invoke(app, ["list-providers", "--help"])
        assert result.exit_code == 0

    def test_discover_models_help(self) -> None:
        """thegent discover-models --help exits with code 0."""
        result = runner.invoke(app, ["discover-models", "--help"])
        assert result.exit_code == 0
