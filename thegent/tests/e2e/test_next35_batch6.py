"""Next-35 batch 6: top-level command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_roid_help_exits_zero() -> None:
    result = runner.invoke(app, ["roid", "--help"])
    assert result.exit_code == 0
    assert "roid" in result.stdout


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
