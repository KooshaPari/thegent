"""Next-35 batch 7: top-level command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_review_help_exits_zero() -> None:
    result = runner.invoke(app, ["review", "--help"])
    assert result.exit_code == 0
    assert "review" in result.stdout


@pytest.mark.e2e
def test_resume_help_exits_zero() -> None:
    result = runner.invoke(app, ["resume", "--help"])
    assert result.exit_code == 0
    assert "resume" in result.stdout


@pytest.mark.e2e
def test_fork_help_exits_zero() -> None:
    result = runner.invoke(app, ["fork", "--help"])
    assert result.exit_code == 0
    assert "fork" in result.stdout


@pytest.mark.e2e
def test_rollback_help_exits_zero() -> None:
    result = runner.invoke(app, ["rollback", "--help"])
    assert result.exit_code == 0
    assert "rollback" in result.stdout


@pytest.mark.e2e
def test_ps_help_exits_zero() -> None:
    result = runner.invoke(app, ["ps", "--help"])
    assert result.exit_code == 0
    assert "ps" in result.stdout
