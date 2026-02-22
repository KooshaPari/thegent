"""Next-70 sprint lane 5: mcp lifecycle and maintenance help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_mcp_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "mcp" in result.stdout


@pytest.mark.e2e
def test_mcp_install_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "install", "--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout


@pytest.mark.e2e
def test_mcp_up_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "up", "--help"])
    assert result.exit_code == 0
    assert "up" in result.stdout


@pytest.mark.e2e
def test_mcp_down_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "down", "--help"])
    assert result.exit_code == 0
    assert "down" in result.stdout


@pytest.mark.e2e
def test_mcp_restart_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "restart", "--help"])
    assert result.exit_code == 0
    assert "restart" in result.stdout


@pytest.mark.e2e
def test_mcp_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_mcp_service_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "service", "--help"])
    assert result.exit_code == 0
    assert "service" in result.stdout


@pytest.mark.e2e
def test_mcp_fix_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "fix", "--help"])
    assert result.exit_code == 0
    assert "fix" in result.stdout


@pytest.mark.e2e
def test_mcp_migrate_unimount_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "migrate-unimount", "--help"])
    assert result.exit_code == 0
    assert "migrate-unimount" in result.stdout


@pytest.mark.e2e
def test_mcp_prune_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "prune", "--help"])
    assert result.exit_code == 0
    assert "prune" in result.stdout
