"""Next-35c lane 5: scaffold and setup help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_scaffold_help_exits_zero() -> None:
    result = runner.invoke(app, ["scaffold", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_scaffold_brownfield_help_exits_zero() -> None:
    result = runner.invoke(app, ["scaffold", "brownfield", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_scaffold_greenfield_help_exits_zero() -> None:
    result = runner.invoke(app, ["scaffold", "greenfield", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_setup_help_exits_zero() -> None:
    result = runner.invoke(app, ["setup", "--help"])
    assert result.exit_code == 0


@pytest.mark.e2e
def test_sys_setup_project_doctor_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "setup", "project", "doctor", "--help"])
    assert result.exit_code == 0
