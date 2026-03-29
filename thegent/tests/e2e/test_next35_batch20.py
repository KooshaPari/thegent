"""Next-35 batch 20: sys subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_sys_cp_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "cp", "--help"])
    assert result.exit_code == 0
    assert "cp" in result.stdout


@pytest.mark.e2e
def test_sys_session_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "session", "--help"])
    assert result.exit_code == 0
    assert "session" in result.stdout


@pytest.mark.e2e
def test_sys_config_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "config", "--help"])
    assert result.exit_code == 0
    assert "config" in result.stdout


@pytest.mark.e2e
def test_sys_terminal_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "terminal", "--help"])
    assert result.exit_code == 0
    assert "terminal" in result.stdout


@pytest.mark.e2e
def test_sys_shadow_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "shadow", "--help"])
    assert result.exit_code == 0
    assert "shadow" in result.stdout
