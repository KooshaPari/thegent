"""CLI tests for governance triggers Typer entrypoint."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from thegent.governance.triggers import app as triggers_app

runner = CliRunner()


def test_help_exits_zero() -> None:
    result = runner.invoke(triggers_app, ["--help"])
    assert result.exit_code == 0


def test_manual_mode_runs_once_with_health_targets(tmp_path: Path) -> None:
    health_targets = tmp_path / "health-targets.json"
    health_targets.write_text("{}", encoding="utf-8")

    trigger = MagicMock()
    trigger.run.return_value = SimpleNamespace(
        state="ok",
        health_score=95.0,
        health_band="green",
        tasks_executed=1,
        tasks_verified=1,
        error=None,
    )

    with (
        patch("thegent.governance.agileplus.AgilePlusLoop"),
        patch("thegent.governance.triggers.create_trigger", return_value=trigger),
        patch("thegent.governance.triggers.signal.signal"),
    ):
        result = runner.invoke(
            triggers_app,
            [
                "--mode",
                "manual",
                "--project-dir",
                str(tmp_path),
                "--health-targets",
                str(health_targets),
            ],
        )

    assert result.exit_code == 0
    trigger.run.assert_called_once_with(force=False)


def test_missing_health_targets_exits_one(tmp_path: Path) -> None:
    result = runner.invoke(
        triggers_app,
        [
            "--mode",
            "manual",
            "--project-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
