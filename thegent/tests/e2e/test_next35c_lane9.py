"""Next-35c lane 9: project help coverage."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_project_brownfield_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "brownfield", "--help"])
    assert result.exit_code == 0
    assert "brownfield" in result.stdout


@pytest.mark.e2e
def test_project_greenfield_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "greenfield", "--help"])
    assert result.exit_code == 0
    assert "greenfield" in result.stdout


@pytest.mark.e2e
def test_project_migrate_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "migrate", "--help"])
    assert result.exit_code == 0
    assert "migrate" in result.stdout


@pytest.mark.e2e
def test_project_init_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "init", "--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout


@pytest.mark.e2e
def test_project_scaffold_help_exits_zero() -> None:
    result = runner.invoke(app, ["project", "scaffold", "--help"])
    assert result.exit_code == 0
    assert "scaffold" in result.stdout
