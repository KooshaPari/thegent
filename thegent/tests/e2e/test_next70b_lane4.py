"""Next-70B lane 4: teammate, sync, setup, install, and observe help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_team_teammates_delegate_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "delegate", "--help"])
    assert result.exit_code == 0
    assert "delegate" in result.stdout


@pytest.mark.e2e
def test_team_teammates_status_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "status", "--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout


@pytest.mark.e2e
def test_team_teammates_show_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "show", "--help"])
    assert result.exit_code == 0
    assert "show" in result.stdout


@pytest.mark.e2e
def test_sync_models_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "models", "--help"])
    assert result.exit_code == 0
    assert "models" in result.stdout


@pytest.mark.e2e
def test_sync_models_tui_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "models", "tui", "--help"])
    assert result.exit_code == 0
    assert "tui" in result.stdout


@pytest.mark.e2e
def test_sync_models_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "models", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_sys_setup_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "--help"])
    assert result.exit_code == 0
    assert "setup" in result.stdout


@pytest.mark.e2e
def test_sys_setup_project_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "--help"])
    assert result.exit_code == 0
    assert "project" in result.stdout


@pytest.mark.e2e
def test_install_project_help_exits_zero() -> None:
    result = runner.invoke(app, ["install", "project", "--help"])
    assert result.exit_code == 0
    assert "project" in result.stdout


@pytest.mark.e2e
def test_observe_compositor_help_exits_zero() -> None:
    result = runner.invoke(app, ["observe", "compositor", "--help"])
    assert result.exit_code == 0
    assert "compositor" in result.stdout
