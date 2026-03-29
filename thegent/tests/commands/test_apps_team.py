from __future__ import annotations
import pytest

from typer.testing import CliRunner

from thegent.cli.apps.team import app

runner = CliRunner()


@pytest.mark.skip(reason="module path issue")
def test_team_list_routes_to_team_commands(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake(*, format: str, console) -> None:
        captured["format"] = format
        captured["console"] = console

    monkeypatch.setattr("thegent.cli.commands.team_commands.team_list_cmd", _fake)
    result = runner.invoke(app, ["list", "--format", "json"])

    assert result.exit_code == 0
    assert captured["format"] == "json"
    assert captured["console"] is not None


def test_team_hierarchy_routes_to_team_commands(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake(*, format: str, console) -> None:
        captured["format"] = format
        captured["console"] = console

    monkeypatch.setattr("thegent.cli.commands.team_commands.team_hierarchy_cmd", _fake)
    result = runner.invoke(app, ["hierarchy", "--format", "rich"])

    assert result.exit_code == 0
    assert captured["format"] == "rich"
    assert captured["console"] is not None


def test_team_crew_routes_to_team_commands(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake(*, format: str, console) -> None:
        captured["format"] = format
        captured["console"] = console

    monkeypatch.setattr("thegent.cli.commands.team_commands.team_crew_cmd", _fake)
    result = runner.invoke(app, ["crew"])

    assert result.exit_code == 0
    assert captured["format"] == "rich"
    assert captured["console"] is not None


def test_team_list_rejects_invalid_format() -> None:
    result = runner.invoke(app, ["list", "--format", "yaml"])
    assert result.exit_code == 2
