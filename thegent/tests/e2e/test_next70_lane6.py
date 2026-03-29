"""Next-70 lane 6: deterministic help contracts for MCP/routing/registry commands."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_mcp_prune_periodic_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "prune-periodic", "--help"])
    assert result.exit_code == 0
    assert "prune-periodic" in result.stdout


@pytest.mark.e2e
def test_mcp_introspect_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "introspect", "--help"])
    assert result.exit_code == 0
    assert "introspect" in result.stdout


@pytest.mark.e2e
def test_mcp_spotlight_exclude_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "spotlight-exclude", "--help"])
    assert result.exit_code == 0
    assert "spotlight-exclude" in result.stdout


@pytest.mark.e2e
def test_mcp_mcp_stdio_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "mcp-stdio", "--help"])
    assert result.exit_code == 0
    assert "mcp-stdio" in result.stdout


@pytest.mark.e2e
def test_routing_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "--help"])
    assert result.exit_code == 0
    assert "routing" in result.stdout


@pytest.mark.e2e
def test_routing_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_routing_harvest_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "harvest", "--help"])
    assert result.exit_code == 0
    assert "harvest" in result.stdout


@pytest.mark.e2e
def test_routing_reset_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "reset", "--help"])
    assert result.exit_code == 0
    assert "reset" in result.stdout


@pytest.mark.e2e
def test_routing_pareto_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "pareto", "--help"])
    assert result.exit_code == 0
    assert "pareto" in result.stdout


@pytest.mark.e2e
def test_registry_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "--help"])
    assert result.exit_code == 0
    assert "registry" in result.stdout
