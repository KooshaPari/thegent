"""Next-35 batch 16: nested command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_skill_validate_help_exits_zero() -> None:
    result = runner.invoke(app, ["skill", "validate", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.stdout


@pytest.mark.e2e
def test_skill_select_help_exits_zero() -> None:
    result = runner.invoke(app, ["skill", "select", "--help"])
    assert result.exit_code == 0
    assert "select" in result.stdout


@pytest.mark.e2e
def test_rules_sync_help_exits_zero() -> None:
    result = runner.invoke(app, ["rules", "sync", "--help"])
    assert result.exit_code == 0
    assert "sync" in result.stdout


@pytest.mark.e2e
def test_domain_map_help_exits_zero() -> None:
    result = runner.invoke(app, ["domain", "map", "--help"])
    assert result.exit_code == 0
    assert "map" in result.stdout


@pytest.mark.e2e
def test_team_create_help_exits_zero() -> None:
    result = runner.invoke(app, ["team", "create", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout
