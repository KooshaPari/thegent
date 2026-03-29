"""CLI help smoke tests for memory snapshot and dump subcommands."""

from typer.testing import CliRunner

from thegent.cli.apps.memory import app

runner = CliRunner()


def test_memory_snapshot_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["snapshot", "list", "--help"])
    assert result.exit_code == 0


def test_memory_snapshot_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["snapshot", "index", "--help"])
    assert result.exit_code == 0


def test_memory_snapshot_daily_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["snapshot", "daily-index", "--help"])
    assert result.exit_code == 0


def test_memory_dump_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["dump", "index", "--help"])
    assert result.exit_code == 0


def test_memory_dump_latest_help_exits_zero() -> None:
    result = runner.invoke(app, ["dump", "latest", "--help"])
    assert result.exit_code == 0
