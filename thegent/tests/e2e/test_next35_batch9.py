"""Next-35 batch 9: run command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_run_stop_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "stop", "--help"])
    assert result.exit_code == 0
    assert "stop" in result.stdout


@pytest.mark.e2e
def test_run_resume_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "resume", "--help"])
    assert result.exit_code == 0
    assert "resume" in result.stdout


@pytest.mark.e2e
def test_run_fork_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "fork", "--help"])
    assert result.exit_code == 0
    assert "fork" in result.stdout


@pytest.mark.e2e
def test_run_rollback_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "rollback", "--help"])
    assert result.exit_code == 0
    assert "rollback" in result.stdout


@pytest.mark.e2e
def test_run_attach_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "attach", "--help"])
    assert result.exit_code == 0
    assert "attach" in result.stdout
