"""Next-35 batch 17: team nested command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_team_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_team_hierarchy_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "hierarchy", "--help"])
    assert result.exit_code == 0
    assert "hierarchy" in result.stdout


@pytest.mark.e2e
def test_team_crew_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "crew", "--help"])
    assert result.exit_code == 0
    assert "crew" in result.stdout


@pytest.mark.e2e
def test_team_delegate_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "delegate", "--help"])
    assert result.exit_code == 0
    assert "delegate" in result.stdout


@pytest.mark.e2e
def test_team_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout
