"""Next-35 batch 14: nested command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_session_resume_help_exits_zero() -> None:
    result = runner.invoke(app, ["session", "resume", "--help"])
    assert result.exit_code == 0
    assert "resume" in result.stdout


@pytest.mark.e2e
def test_session_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["session", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_orchestrate_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["orchestrate", "plan", "--help"])
    assert result.exit_code == 0
    assert "plan" in result.stdout


@pytest.mark.e2e
def test_orchestrate_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["orchestrate", "run", "--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout


@pytest.mark.e2e
def test_registry_recommend_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "recommend", "--help"])
    assert result.exit_code == 0
    assert "recommend" in result.stdout
