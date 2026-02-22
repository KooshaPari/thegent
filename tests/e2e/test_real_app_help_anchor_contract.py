"""Real-app help-anchor contracts for stable CLI commands."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


def test_root_help_contains_usage_and_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "Commands" in result.stdout


def test_run_help_contains_usage() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_plan_help_contains_usage() -> None:
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_session_contract_health_gate_help_contains_usage() -> None:
    result = runner.invoke(app, ["session-contract-health-gate", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
