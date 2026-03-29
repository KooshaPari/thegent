"""Next-35 batch 21: isolation and mesh subcommand help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_isolation_check_help_exits_zero() -> None:
    result = runner.invoke(app, ["isolation", "check", "--help"])
    assert result.exit_code == 0
    assert "check" in result.stdout


@pytest.mark.e2e
def test_isolation_share_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["isolation", "share-run", "--help"])
    assert result.exit_code == 0
    assert "share-run" in result.stdout


@pytest.mark.e2e
def test_mesh_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["mesh", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_mesh_init_help_exits_zero() -> None:
    result = runner.invoke(app, ["mesh", "init", "--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout


@pytest.mark.e2e
def test_mesh_discover_help_exits_zero() -> None:
    result = runner.invoke(app, ["mesh", "discover", "--help"])
    assert result.exit_code == 0
    assert "discover" in result.stdout
