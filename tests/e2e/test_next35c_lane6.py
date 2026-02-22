"""Next-35c lane 6: sys setup project help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_sys_setup_project_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_sys_setup_project_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "list", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_sys_setup_project_migrate_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "migrate", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_sys_setup_project_scaffold_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "scaffold", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_sys_setup_project_scaffold_profiles_help_exits_zero() -> None:
    result = runner.invoke(
        app,
        ["sys", "setup", "project", "scaffold-profiles", "--help"],
    )
    assert result.exit_code == 0
