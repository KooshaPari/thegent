"""Next-35c lane 10: project and git help-path coverage."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_project_scaffold_profiles_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "scaffold-profiles", "--help"])
    assert result.exit_code == 0
    assert "scaffold-profiles" in result.stdout


@pytest.mark.e2e
def test_project_doctor_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "doctor", "--help"])
    assert result.exit_code == 0
    assert "doctor" in result.stdout


@pytest.mark.e2e
def test_install_project_brownfield_help_exits_zero() -> None:
    result = runner.invoke(app, ["install", "project", "brownfield", "--help"])
    assert result.exit_code == 0
    assert "brownfield" in result.stdout


@pytest.mark.e2e
def test_git_worktree_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_git_worktree_claim_help_exits_zero() -> None:
    result = runner.invoke(app, ["git", "worktree", "claim", "--help"])
    assert result.exit_code == 0
    assert "claim" in result.stdout
