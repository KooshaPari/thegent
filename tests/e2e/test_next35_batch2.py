"""Next-35 batch 2: top-level command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_plan_help_exits_zero() -> None:
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0
    assert "plan" in result.stdout


@pytest.mark.e2e
def test_queue_help_exits_zero() -> None:
    result = runner.invoke(app, ["queue", "--help"])
    assert result.exit_code == 0
    assert "queue" in result.stdout


@pytest.mark.e2e
def test_rules_help_exits_zero() -> None:
    result = runner.invoke(app, ["rules", "--help"])
    assert result.exit_code == 0
    assert "rules" in result.stdout


@pytest.mark.e2e
def test_team_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "--help"])
    assert result.exit_code == 0
    assert "team" in result.stdout


@pytest.mark.e2e
def test_domain_help_exits_zero() -> None:
    result = runner.invoke(app, ["domain", "--help"])
    assert result.exit_code == 0
    assert "domain" in result.stdout
