"""Next-70b lane 1: enterprise help command E2E checks."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.e2e.cli_runner_compat import CompatCliRunner

sys.modules.setdefault("thegent_git", MagicMock())
from thegent.main import app

runner = CompatCliRunner()


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
def test_enterprise_compliance_audit_export_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "compliance", "audit-export", "--help"])
    assert result.exit_code == 0
    assert "audit-export" in result.stdout


@pytest.mark.e2e
def test_enterprise_compliance_evidence_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "compliance", "evidence", "--help"])
    assert result.exit_code == 0
    assert "evidence" in result.stdout


@pytest.mark.e2e
def test_enterprise_gdpr_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "gdpr", "--help"])
    assert result.exit_code == 0
    assert "gdpr" in result.stdout


@pytest.mark.e2e
def test_enterprise_gdpr_purge_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "gdpr", "purge", "--help"])
    assert result.exit_code == 0
    assert "purge" in result.stdout


@pytest.mark.e2e
def test_enterprise_org_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "org", "--help"])
    assert result.exit_code == 0
    assert "org" in result.stdout


@pytest.mark.e2e
def test_enterprise_org_list_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "org", "list", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


@pytest.mark.e2e
def test_enterprise_org_create_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "org", "create", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout


@pytest.mark.e2e
def test_enterprise_org_show_help_exits_zero() -> None:
    result = runner.invoke(app, ["enterprise", "org", "show", "--help"])
    assert result.exit_code == 0
    assert "show" in result.stdout
