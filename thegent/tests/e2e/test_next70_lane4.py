"""Next-70 sprint lane 4: sync help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_sync_rules_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "rules", "--help"])
    assert result.exit_code == 0
    assert "rules" in result.stdout


@pytest.mark.e2e
def test_sync_research_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "research", "--help"])
    assert result.exit_code == 0
    assert "research" in result.stdout


@pytest.mark.e2e
def test_sync_dag_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "dag", "--help"])
    assert result.exit_code == 0
    assert "dag" in result.stdout


@pytest.mark.e2e
def test_sync_work_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "work", "--help"])
    assert result.exit_code == 0
    assert "work" in result.stdout


@pytest.mark.e2e
def test_sync_catalog_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "catalog", "--help"])
    assert result.exit_code == 0
    assert "catalog" in result.stdout


@pytest.mark.e2e
def test_sync_update_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "update", "--help"])
    assert result.exit_code == 0
    assert "update" in result.stdout


@pytest.mark.e2e
def test_sync_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_sync_push_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "push", "--help"])
    assert result.exit_code == 0
    assert "push" in result.stdout


@pytest.mark.e2e
def test_sync_pull_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "pull", "--help"])
    assert result.exit_code == 0
    assert "pull" in result.stdout


@pytest.mark.e2e
def test_sync_reset_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "reset", "--help"])
    assert result.exit_code == 0
    assert "reset" in result.stdout
