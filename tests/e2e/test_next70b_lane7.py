"""Next 70b sprint lane 7: top-level and group help surfaces."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_roid_help_exits_zero() -> None:
    result = runner.invoke(app, ["roid", "--help"])
    assert result.exit_code == 0
    assert "roid" in result.stdout


@pytest.mark.e2e
def test_observe_help_exits_zero() -> None:
    result = runner.invoke(app, ["observe", "--help"])
    assert result.exit_code == 0
    assert "observe" in result.stdout


@pytest.mark.e2e
def test_install_help_exits_zero() -> None:
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    assert "install" in result.stdout


@pytest.mark.e2e
def test_registry_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "--help"])
    assert result.exit_code == 0
    assert "registry" in result.stdout


@pytest.mark.e2e
def test_routing_help_exits_zero() -> None:
    result = runner.invoke(app, ["routing", "--help"])
    assert result.exit_code == 0
    assert "routing" in result.stdout


@pytest.mark.e2e
def test_enterprise_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "--help"])
    assert result.exit_code == 0
    assert "enterprise" in result.stdout


@pytest.mark.e2e
def test_memory_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "--help"])
    assert result.exit_code == 0
    assert "memory" in result.stdout


@pytest.mark.e2e
def test_session_help_exits_zero() -> None:
    result = runner.invoke(app, ["session", "--help"])
    assert result.exit_code == 0
    assert "session" in result.stdout


@pytest.mark.e2e
def test_orchestrate_help_exits_zero() -> None:
    result = runner.invoke(app, ["orchestrate", "--help"])
    assert result.exit_code == 0
    assert "orchestrate" in result.stdout


@pytest.mark.e2e
def test_queue_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "--help"])
    assert result.exit_code == 0
    assert "queue" in result.stdout
