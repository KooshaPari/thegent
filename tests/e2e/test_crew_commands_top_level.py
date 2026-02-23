"""E2E checks for top-level crew command surface."""

from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


def test_crew_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "--help"])
    assert result.exit_code == 0


def test_crew_create_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "create", "--help"])
    assert result.exit_code == 0


def test_crew_execute_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "execute", "--help"])
    assert result.exit_code == 0


def test_crew_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "list", "--help"])
    assert result.exit_code == 0


def test_crew_show_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "show", "--help"])
    assert result.exit_code == 0


def test_crew_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["crew", "status", "--help"])
    assert result.exit_code == 0
