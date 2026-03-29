"""Next-70b lane 6: deterministic help contracts for mixed top-level commands."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_agent_server_help_exits_zero() -> None:
    result = runner.invoke(app, ["agent-server", "--help"])
    assert result.exit_code == 0
    assert "agent-server" in result.stdout


@pytest.mark.e2e
def test_help_help_exits_zero() -> None:
    result = runner.invoke(app, ["help", "--help"])
    assert result.exit_code == 0
    assert "help" in result.stdout


@pytest.mark.e2e
def test_do_help_exits_zero() -> None:
    result = runner.invoke(app, ["do", "--help"])
    assert result.exit_code == 0
    assert "do" in result.stdout


@pytest.mark.e2e
def test_list_agents_help_exits_zero() -> None:
    result = runner.invoke(app, ["list-agents", "--help"])
    assert result.exit_code == 0
    assert "list-agents" in result.stdout


@pytest.mark.e2e
def test_list_droids_help_exits_zero() -> None:
    result = runner.invoke(app, ["list-droids", "--help"])
    assert result.exit_code == 0
    assert "list-droids" in result.stdout


@pytest.mark.e2e
def test_session_contract_health_gate_help_exits_zero() -> None:
    result = runner.invoke(app, ["session-contract-health-gate", "--help"])
    assert result.exit_code == 0
    assert "session-contract-health-gate" in result.stdout


@pytest.mark.e2e
def test_session_contract_health_report_help_exits_zero() -> None:
    result = runner.invoke(app, ["session-contract-health-report", "--help"])
    assert result.exit_code == 0
    assert "session-contract-health-report" in result.stdout


@pytest.mark.e2e
def test_session_contract_health_trend_help_exits_zero() -> None:
    result = runner.invoke(app, ["session-contract-health-trend", "--help"])
    assert result.exit_code == 0
    assert "session-contract-health-trend" in result.stdout


@pytest.mark.e2e
def test_sitback_help_exits_zero() -> None:
    result = runner.invoke(app, ["sitback", "--help"])
    assert result.exit_code == 0
    assert "sitback" in result.stdout


@pytest.mark.e2e
def test_compositor_help_exits_zero() -> None:
    result = runner.invoke(app, ["compositor", "--help"])
    assert result.exit_code == 0
    assert "compositor" in result.stdout
