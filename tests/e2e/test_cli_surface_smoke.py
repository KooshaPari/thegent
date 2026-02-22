"""Deterministic CLI surface smoke checks for stable command/help paths."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


def test_root_help_exits_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0


def test_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0


def test_session_contract_health_gate_help_exits_zero() -> None:
    result = runner.invoke(app, ["session-contract-health-gate", "--help"])
    assert result.exit_code == 0


def test_session_contract_health_report_help_exits_zero() -> None:
    result = runner.invoke(app, ["session-contract-health-report", "--help"])
    assert result.exit_code == 0


def test_list_agents_exits_zero() -> None:
    result = runner.invoke(app, ["list-agents"])
    assert result.exit_code == 0
    assert "gemini" in result.stdout.lower()
