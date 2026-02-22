"""Next-35 batch 3: top-level command help E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_govern_help_exits_zero() -> None:
    result = runner.invoke(app, ["govern", "--help"])
    assert result.exit_code == 0
    assert "govern" in result.stdout


@pytest.mark.e2e
def test_sys_help_exits_zero() -> None:
    result = runner.invoke(app, ["sys", "--help"])
    assert result.exit_code == 0
    assert "sys" in result.stdout


@pytest.mark.e2e
def test_mcp_help_exits_zero() -> None:
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "mcp" in result.stdout


@pytest.mark.e2e
def test_isolation_help_exits_zero() -> None:
    result = runner.invoke(app, ["isolation", "--help"])
    assert result.exit_code == 0
    assert "isolation" in result.stdout


@pytest.mark.e2e
def test_mesh_help_exits_zero() -> None:
    result = runner.invoke(app, ["mesh", "--help"])
    assert result.exit_code == 0
    assert "mesh" in result.stdout
