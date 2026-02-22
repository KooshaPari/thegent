"""Next-35 batch 19: govern/sys subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_govern_resolve_config_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "resolve-config", "--help"])
    assert result.exit_code == 0
    assert "resolve-config" in result.stdout.lower()


@pytest.mark.e2e
def test_govern_negotiate_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "negotiate", "--help"])
    assert result.exit_code == 0
    assert "negotiate" in result.stdout.lower()


@pytest.mark.e2e
def test_govern_session_contract_health_trend_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "session-contract-health-trend", "--help"])
    assert result.exit_code == 0
    assert "session-contract-health-trend" in result.stdout.lower()


@pytest.mark.e2e
def test_sys_mcp_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "mcp", "--help"])
    assert result.exit_code == 0
    assert "mcp" in result.stdout.lower()


@pytest.mark.e2e
def test_sys_lsp_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "lsp", "--help"])
    assert result.exit_code == 0
    assert "lsp" in result.stdout.lower()
