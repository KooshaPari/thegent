"""Next-70 sprint lane 7: registry, memory, enterprise help checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


@pytest.mark.e2e
def test_registry_recommend_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "recommend", "--help"])
    assert result.exit_code == 0
    assert "recommend" in result.stdout


@pytest.mark.e2e
def test_registry_doctor_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "doctor", "--help"])
    assert result.exit_code == 0
    assert "doctor" in result.stdout


@pytest.mark.e2e
def test_registry_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["registry", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_memory_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "--help"])
    assert result.exit_code == 0
    assert "memory" in result.stdout


@pytest.mark.e2e
def test_memory_garden_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "garden", "--help"])
    assert result.exit_code == 0
    assert "garden" in result.stdout


@pytest.mark.e2e
def test_memory_snapshot_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "snapshot", "--help"])
    assert result.exit_code == 0
    assert "snapshot" in result.stdout


@pytest.mark.e2e
def test_memory_dump_help_exits_zero() -> None:
    result = runner.invoke(app, ["memory", "dump", "--help"])
    assert result.exit_code == 0
    assert "dump" in result.stdout


@pytest.mark.e2e
def test_enterprise_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "--help"])
    assert result.exit_code == 0
    assert "enterprise" in result.stdout


@pytest.mark.e2e
def test_enterprise_compliance_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "compliance", "--help"])
    assert result.exit_code == 0
    assert "compliance" in result.stdout


@pytest.mark.e2e
def test_enterprise_gdpr_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "gdpr", "--help"])
    assert result.exit_code == 0
    assert "gdpr" in result.stdout
