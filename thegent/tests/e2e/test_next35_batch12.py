"""Next-35 batch 12: queue subcommand help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_queue_add_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "add", "--help"])
    assert result.exit_code == 0
    assert "add" in result.stdout.lower()


@pytest.mark.e2e
def test_queue_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout.lower()


@pytest.mark.e2e
def test_queue_next_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "next", "--help"])
    assert result.exit_code == 0
    assert "next" in result.stdout.lower()


@pytest.mark.e2e
def test_queue_done_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "done", "--help"])
    assert result.exit_code == 0
    assert "done" in result.stdout.lower()


@pytest.mark.e2e
def test_queue_tui_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "tui", "--help"])
    assert result.exit_code == 0
    assert "tui" in result.stdout.lower()
