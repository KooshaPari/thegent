"""Next-35c sprint lane 2: git command help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_git_commit_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "commit", "--help"])
    assert result.exit_code == 0
    assert "commit" in result.stdout


@pytest.mark.e2e
def test_git_diff_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "diff", "--help"])
    assert result.exit_code == 0
    assert "diff" in result.stdout


@pytest.mark.e2e
def test_git_lock_cleanup_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "lock-cleanup", "--help"])
    assert result.exit_code == 0
    assert "lock-cleanup" in result.stdout


@pytest.mark.e2e
def test_git_lock_cleanup_service_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "lock-cleanup", "service", "--help"])
    assert result.exit_code == 0
    assert "service" in result.stdout


@pytest.mark.e2e
def test_git_log_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "log", "--help"])
    assert result.exit_code == 0
    assert "log" in result.stdout
