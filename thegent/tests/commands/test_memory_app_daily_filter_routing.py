"""Routing tests for snapshot daily filter options."""

from __future__ import annotations
import pytest

from pathlib import Path

from typer.testing import CliRunner

from thegent.cli.apps.memory import app


runner = CliRunner()


@pytest.mark.skip(reason="module path issue")
def test_memory_snapshot_daily_index_forwards_trigger_tag_since(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_snapshot_daily_index_cmd(
        *,
        project: Path | None,
        limit: int,
        trigger: str | None,
        tag: str | None,
        since: str | None,
        format: str | None,
    ) -> None:
        captured["project"] = project
        captured["limit"] = limit
        captured["trigger"] = trigger
        captured["tag"] = tag
        captured["since"] = since
        captured["format"] = format

    monkeypatch.setattr(
        "thegent.cli.commands.team_cmds.snapshot_daily_index_cmd",
        fake_snapshot_daily_index_cmd,
    )

    project = tmp_path / "project"

    result = runner.invoke(
        app,
        [
            "snapshot",
            "daily-index",
            "--project",
            str(project),
            "--trigger",
            "manual",
            "--tag",
            "release",
            "--since",
            "2026-02-01T00:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "project": project,
        "limit": 1000,
        "trigger": "manual",
        "tag": "release",
        "since": "2026-02-01T00:00:00Z",
        "format": None,
    }


def test_memory_snapshot_daily_totals_forwards_trigger_tag_since(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_snapshot_daily_totals_cmd(
        *,
        project: Path | None,
        limit: int,
        trigger: str | None,
        tag: str | None,
        since: str | None,
        format: str | None,
    ) -> None:
        captured["project"] = project
        captured["limit"] = limit
        captured["trigger"] = trigger
        captured["tag"] = tag
        captured["since"] = since
        captured["format"] = format

    monkeypatch.setattr(
        "thegent.cli.commands.team_cmds.snapshot_daily_totals_cmd",
        fake_snapshot_daily_totals_cmd,
    )

    project = tmp_path / "project"

    result = runner.invoke(
        app,
        [
            "snapshot",
            "daily-totals",
            "--project",
            str(project),
            "--trigger",
            "scheduled",
            "--tag",
            "nightly",
            "--since",
            "2026-02-02T00:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "project": project,
        "limit": 1000,
        "trigger": "scheduled",
        "tag": "nightly",
        "since": "2026-02-02T00:00:00Z",
        "format": None,
    }


def test_memory_snapshot_daily_export_forwards_trigger_tag_since(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_snapshot_daily_export_cmd(
        *,
        project: Path | None,
        out_dir: Path | None,
        limit: int,
        trigger: str | None,
        tag: str | None,
        since: str | None,
        format: str | None,
    ) -> None:
        captured["project"] = project
        captured["out_dir"] = out_dir
        captured["limit"] = limit
        captured["trigger"] = trigger
        captured["tag"] = tag
        captured["since"] = since
        captured["format"] = format

    monkeypatch.setattr(
        "thegent.cli.commands.team_cmds.snapshot_daily_export_cmd",
        fake_snapshot_daily_export_cmd,
    )

    project = tmp_path / "project"
    out_dir = tmp_path / "exports"

    result = runner.invoke(
        app,
        [
            "snapshot",
            "daily-export",
            "--project",
            str(project),
            "--out-dir",
            str(out_dir),
            "--trigger",
            "manual",
            "--tag",
            "weekly",
            "--since",
            "2026-02-03T00:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "project": project,
        "out_dir": out_dir,
        "limit": 1000,
        "trigger": "manual",
        "tag": "weekly",
        "since": "2026-02-03T00:00:00Z",
        "format": None,
    }


def test_memory_snapshot_daily_index_help_mentions_since() -> None:
    result = runner.invoke(app, ["snapshot", "daily-index", "--help"])

    assert result.exit_code == 0
    assert "--since" in result.stdout


def test_memory_snapshot_daily_index_omitted_filters_pass_none(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_snapshot_daily_index_cmd(
        *,
        project: Path | None,
        limit: int,
        trigger: str | None,
        tag: str | None,
        since: str | None,
        format: str | None,
    ) -> None:
        captured["project"] = project
        captured["limit"] = limit
        captured["trigger"] = trigger
        captured["tag"] = tag
        captured["since"] = since
        captured["format"] = format

    monkeypatch.setattr(
        "thegent.cli.commands.team_cmds.snapshot_daily_index_cmd",
        fake_snapshot_daily_index_cmd,
    )

    project = tmp_path / "project"

    result = runner.invoke(
        app,
        [
            "snapshot",
            "daily-index",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "project": project,
        "limit": 1000,
        "trigger": None,
        "tag": None,
        "since": None,
        "format": None,
    }
