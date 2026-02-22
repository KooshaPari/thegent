"""Next-35 batch 1: top-level command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_run_help_exits_zero() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout


@pytest.mark.e2e
def test_bench_help_exits_zero() -> None:
    result = runner.invoke(app, ["bench", "--help"])
    assert result.exit_code == 0
    assert "bench" in result.stdout


@pytest.mark.e2e
def test_sync_help_exits_zero() -> None:
    result = runner.invoke(app, ["sync", "--help"])
    assert result.exit_code == 0
    assert "sync" in result.stdout


@pytest.mark.e2e
def test_skill_help_exits_zero() -> None:
    result = runner.invoke(app, ["skill", "--help"])
    assert result.exit_code == 0
    assert "skill" in result.stdout


@pytest.mark.e2e
def test_audit_help_exits_zero() -> None:
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "audit" in result.stdout
