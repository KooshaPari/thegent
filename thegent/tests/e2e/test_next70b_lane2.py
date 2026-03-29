"""Next 70b sprint lane 2: enterprise keys and memory help surfaces."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_enterprise_keys_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "keys", "--help"])
    assert result.exit_code == 0
    assert "keys" in result.stdout


@pytest.mark.e2e
def test_enterprise_keys_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "keys", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_enterprise_keys_rotate_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "keys", "rotate", "--help"])
    assert result.exit_code == 0
    assert "rotate" in result.stdout


@pytest.mark.e2e
def test_memory_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "--help"])
    assert result.exit_code == 0
    assert "memory" in result.stdout


@pytest.mark.e2e
def test_memory_garden_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "garden", "--help"])
    assert result.exit_code == 0
    assert "garden" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "--help"])
    assert result.exit_code == 0
    assert "snapshot" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_index_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "index", "--help"])
    assert result.exit_code == 0
    assert "index" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_export_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "export", "--help"])
    assert result.exit_code == 0
    assert "export" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_prune_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "prune", "--help"])
    assert result.exit_code == 0
    assert "prune" in result.stdout
