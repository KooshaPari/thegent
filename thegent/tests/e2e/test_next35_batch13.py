"""Next-35 batch 13: MCP nested command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_mcp_install_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "install", "--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout


@pytest.mark.e2e
def test_mcp_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_mcp_prune_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "prune", "--help"])
    assert result.exit_code == 0
    assert "prune" in result.stdout


@pytest.mark.e2e
def test_mcp_introspect_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "introspect", "--help"])
    assert result.exit_code == 0
    assert "introspect" in result.stdout


@pytest.mark.e2e
def test_mcp_stdio_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "mcp-stdio", "--help"])
    assert result.exit_code == 0
    assert "mcp-stdio" in result.stdout
