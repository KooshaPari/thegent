"""Next-35 batch 10: sync subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_sync_all_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "all", "--help"])
    assert result.exit_code == 0
    assert "all" in result.stdout


@pytest.mark.e2e
def test_sync_rules_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "rules", "--help"])
    assert result.exit_code == 0
    assert "rules" in result.stdout


@pytest.mark.e2e
def test_sync_dag_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "dag", "--help"])
    assert result.exit_code == 0
    assert "dag" in result.stdout


@pytest.mark.e2e
def test_sync_models_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "models", "--help"])
    assert result.exit_code == 0
    assert "models" in result.stdout


@pytest.mark.e2e
def test_sync_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout
