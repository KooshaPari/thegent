"""Next-35c lane 3: additional git worktree and status help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_git_merge_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "merge", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_git_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "status", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_git_worktree_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_git_worktree_acquire_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "acquire", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_git_worktree_cleanup_stale_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "cleanup-stale", "--help"])
    assert result.exit_code == 0
