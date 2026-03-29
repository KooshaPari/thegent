"""Next-70b lane 5: top-level help checks for core workflows."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout


@pytest.mark.e2e
def test_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0
    assert "plan" in result.stdout


@pytest.mark.e2e
def test_mcp_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "mcp" in result.stdout


@pytest.mark.e2e
def test_registry_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "--help"])
    assert result.exit_code == 0
    assert "registry" in result.stdout


@pytest.mark.e2e
def test_govern_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "--help"])
    assert result.exit_code == 0
    assert "govern" in result.stdout


@pytest.mark.e2e
def test_ps_help_exits_zero() -> None:
    result = runner.invoke(app, ["ps", "--help"])
    assert result.exit_code == 0
    assert "ps" in result.stdout


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
def test_help_help_exits_zero() -> None:
    result = runner.invoke(app, ["help", "--help"])
    assert result.exit_code == 0
    assert "help" in result.stdout


@pytest.mark.e2e
def test_session_help_exits_zero() -> None:
    result = runner.invoke(app, ["session", "--help"])
    assert result.exit_code == 0
    assert "session" in result.stdout
