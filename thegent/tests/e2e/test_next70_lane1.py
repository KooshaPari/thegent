"""Next-70 lane 1: audit help command E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_audit_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "audit" in result.stdout


@pytest.mark.e2e
def test_audit_all_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "all", "--help"])
    assert result.exit_code == 0
    assert "all" in result.stdout


@pytest.mark.e2e
def test_audit_doctor_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "doctor", "--help"])
    assert result.exit_code == 0
    assert "doctor" in result.stdout


@pytest.mark.e2e
def test_audit_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "plan", "--help"])
    assert result.exit_code == 0
    assert "plan" in result.stdout


@pytest.mark.e2e
def test_audit_security_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "security", "--help"])
    assert result.exit_code == 0
    assert "security" in result.stdout


@pytest.mark.e2e
def test_audit_sweep_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "sweep", "--help"])
    assert result.exit_code == 0
    assert "sweep" in result.stdout


@pytest.mark.e2e
def test_audit_registry_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "registry", "--help"])
    assert result.exit_code == 0
    assert "registry" in result.stdout


@pytest.mark.e2e
def test_audit_fatigue_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "fatigue", "--help"])
    assert result.exit_code == 0
    assert "fatigue" in result.stdout


@pytest.mark.e2e
def test_audit_costs_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "costs", "--help"])
    assert result.exit_code == 0
    assert "costs" in result.stdout


@pytest.mark.e2e
def test_audit_journal_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "journal", "--help"])
    assert result.exit_code == 0
    assert "journal" in result.stdout
