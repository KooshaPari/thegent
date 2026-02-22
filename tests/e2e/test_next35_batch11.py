"""Next-35 batch 11: plan subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


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
def test_plan_progress_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "progress", "--help"])
    assert result.exit_code == 0
    assert "progress" in result.stdout
