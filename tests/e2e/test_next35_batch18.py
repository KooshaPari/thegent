"""Next-35 batch 18: team/govern nested command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_team_teammates_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "teammates", "--help"])
    assert result.exit_code == 0
    assert "teammates" in result.stdout


@pytest.mark.e2e
def test_govern_approve_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "approve", "--help"])
    assert result.exit_code == 0
    assert "approve" in result.stdout


@pytest.mark.e2e
def test_govern_reject_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "reject", "--help"])
    assert result.exit_code == 0
    assert "reject" in result.stdout


@pytest.mark.e2e
def test_govern_vet_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "vet", "--help"])
    assert result.exit_code == 0
    assert "vet" in result.stdout


@pytest.mark.e2e
def test_govern_register_host_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "register-host", "--help"])
    assert result.exit_code == 0
    assert "register-host" in result.stdout
