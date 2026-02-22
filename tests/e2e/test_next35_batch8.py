"""Next-35 batch 8: run-subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_run_agent_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "agent", "--help"])
    assert result.exit_code == 0
    assert "agent" in result.stdout.lower()


@pytest.mark.e2e
def test_run_free_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "free", "--help"])
    assert result.exit_code == 0
    assert "free" in result.stdout.lower()


@pytest.mark.e2e
def test_run_history_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "history", "--help"])
    assert result.exit_code == 0
    assert "history" in result.stdout.lower()


@pytest.mark.e2e
def test_run_logs_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "logs", "--help"])
    assert result.exit_code == 0
    assert "logs" in result.stdout.lower()


@pytest.mark.e2e
def test_run_ps_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "ps", "--help"])
    assert result.exit_code == 0
    assert "ps" in result.stdout.lower()
