"""Next-70 sprint lane 2: plan help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0
    assert "plan" in result.stdout


@pytest.mark.e2e
def test_plan_next_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "next", "--help"])
    assert result.exit_code == 0
    assert "next" in result.stdout


@pytest.mark.e2e
def test_plan_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_plan_add_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "add", "--help"])
    assert result.exit_code == 0
    assert "add" in result.stdout


@pytest.mark.e2e
def test_plan_remove_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "remove", "--help"])
    assert result.exit_code == 0
    assert "remove" in result.stdout


@pytest.mark.e2e
def test_plan_roadmap_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "roadmap", "--help"])
    assert result.exit_code == 0
    assert "roadmap" in result.stdout


@pytest.mark.e2e
def test_plan_work_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "work", "--help"])
    assert result.exit_code == 0
    assert "work" in result.stdout


@pytest.mark.e2e
def test_plan_analyze_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "analyze", "--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout


@pytest.mark.e2e
def test_plan_checkpoint_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "checkpoint", "--help"])
    assert result.exit_code == 0
    assert "checkpoint" in result.stdout


@pytest.mark.e2e
def test_plan_rollback_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "rollback", "--help"])
    assert result.exit_code == 0
    assert "rollback" in result.stdout
