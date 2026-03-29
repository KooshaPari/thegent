"""Deterministic help-surface e2e checks for selected command entry points."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_session_help_exits_zero() -> None:
    result = runner.invoke(app, ["session", "--help"])
    assert result.exit_code == 0
    assert "session" in result.stdout.lower()


@pytest.mark.e2e
def test_orchestrate_help_exits_zero() -> None:
    result = runner.invoke(app, ["orchestrate", "--help"])
    assert result.exit_code == 0
    assert "orchestrate" in result.stdout.lower()


@pytest.mark.e2e
def test_sitback_help_exits_zero() -> None:
    result = runner.invoke(app, ["sitback", "--help"])
    assert result.exit_code == 0
    assert "sitback" in result.stdout.lower()


@pytest.mark.e2e
def test_compositor_help_exits_zero() -> None:
    result = runner.invoke(app, ["compositor", "--help"])
    assert result.exit_code == 0
    assert "compositor" in result.stdout.lower()


@pytest.mark.e2e
def test_observe_help_exits_zero() -> None:
    result = runner.invoke(app, ["observe", "--help"])
    assert result.exit_code == 0
    assert "observe" in result.stdout.lower()
