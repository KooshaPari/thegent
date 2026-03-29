"""Next 70b sprint lane 3: memory snapshot/dump and team teammates help surfaces."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_memory_snapshot_meta_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "meta", "--help"])
    assert result.exit_code == 0
    assert "meta" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_daily_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "daily-index", "--help"])
    assert result.exit_code == 0
    assert "daily-index" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_daily_export_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "daily-export", "--help"])
    assert result.exit_code == 0
    assert "daily-export" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_daily_totals_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "daily-totals", "--help"])
    assert result.exit_code == 0
    assert "daily-totals" in result.stdout


@pytest.mark.e2e
def test_memory_dump_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "dump", "--help"])
    assert result.exit_code == 0
    assert "dump" in result.stdout


@pytest.mark.e2e
def test_memory_dump_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "dump", "index", "--help"])
    assert result.exit_code == 0
    assert "index" in result.stdout


@pytest.mark.e2e
def test_memory_dump_latest_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "dump", "latest", "--help"])
    assert result.exit_code == 0
    assert "latest" in result.stdout


@pytest.mark.e2e
def test_memory_dump_categories_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "dump", "categories", "--help"])
    assert result.exit_code == 0
    assert "categories" in result.stdout


@pytest.mark.e2e
def test_team_teammates_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "--help"])
    assert result.exit_code == 0
    assert "teammates" in result.stdout


@pytest.mark.e2e
def test_team_teammates_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
