"""Next-35 batch 15: run/bench/skill help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_run_send_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "send", "--help"])
    assert result.exit_code == 0
    assert "send" in result.stdout


@pytest.mark.e2e
def test_bench_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["bench", "run", "--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout


@pytest.mark.e2e
def test_bench_compare_help_exits_zero() -> None:
    result = runner.invoke(app, ["bench", "compare", "--help"])
    assert result.exit_code == 0
    assert "compare" in result.stdout


@pytest.mark.e2e
def test_skill_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["skill", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_skill_show_help_exits_zero() -> None:
    result = runner.invoke(app, ["skill", "show", "--help"])
    assert result.exit_code == 0
    assert "show" in result.stdout
