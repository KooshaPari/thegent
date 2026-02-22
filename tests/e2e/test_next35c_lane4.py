"""Next-35c lane 4: git worktree and routing pareto help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_git_worktree_release_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "release", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_git_worktree_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "status", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_routing_pareto_config_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "pareto", "config", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_routing_pareto_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "pareto", "status", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_routing_pareto_verify_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "pareto", "verify", "--help"])
    assert result.exit_code == 0
