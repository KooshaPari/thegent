"""Tests for sync policy audit command (WL-261).

# @trace WL-261
"""

from __future__ import annotations

import json

import pytest

from thegent.integrations.sync_auditor import SyncAuditor, SyncPolicyAudit


class TestSyncAuditor:
    """Test SyncAuditor class."""

    @pytest.mark.requirement("WL-261")
    def test_auditor_creation(self):
        """Test creating a sync auditor."""
        auditor = SyncAuditor()
        assert auditor is not None

    @pytest.mark.requirement("WL-261")
    def test_set_enabled_connectors(self):
        """Test setting enabled connectors."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github", "gitlab"])
        assert auditor._enabled_connectors == ["github", "gitlab"]

    @pytest.mark.requirement("WL-261")
    def test_set_quota_budgets(self):
        """Test setting quota budgets."""
        auditor = SyncAuditor()
        budgets = {"github": 100, "gitlab": 50}
        auditor.set_quota_budgets(budgets)
        assert auditor._quota_budgets == budgets

    @pytest.mark.requirement("WL-261")
    def test_set_policy_modes(self):
        """Test setting policy modes."""
        auditor = SyncAuditor()
        modes = {"github": "enforce", "gitlab": "warn"}
        auditor.set_policy_modes(modes)
        assert auditor._policy_modes == modes

    @pytest.mark.requirement("WL-261")
    def test_audit_returns_audit_info(self):
        """Test audit returns SyncPolicyAudit."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github"])
        auditor.set_quota_budgets({"github": 100})
        auditor.set_policy_modes({"github": "enforce"})

        result = auditor.audit()

        assert isinstance(result, SyncPolicyAudit)
        assert result.enabled_connectors == ["github"]
        assert result.quota_budgets == {"github": 100}
        assert result.policy_modes == {"github": "enforce"}
        assert result.audit_status == "success"
        assert result.timestamp is not None

    @pytest.mark.requirement("WL-261")
    def test_audit_as_json(self):
        """Test audit as JSON."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github"])
        auditor.set_quota_budgets({"github": 100})
        auditor.set_policy_modes({"github": "enforce"})

        json_str = auditor.audit_as_json()

        data = json.loads(json_str)
        assert data["enabled_connectors"] == ["github"]
        assert data["quota_budgets"] == {"github": 100}
        assert data["policy_modes"] == {"github": "enforce"}
        assert data["audit_status"] == "success"

    @pytest.mark.requirement("WL-261")
    def test_audit_as_dict(self):
        """Test audit as dictionary."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github", "gitlab"])
        auditor.set_quota_budgets({"github": 100, "gitlab": 50})
        auditor.set_policy_modes({"github": "enforce", "gitlab": "warn"})

        result = auditor.audit_as_dict()

        assert isinstance(result, dict)
        assert result["enabled_connectors"] == ["github", "gitlab"]
        assert result["quota_budgets"] == {"github": 100, "gitlab": 50}
        assert result["policy_modes"] == {"github": "enforce", "gitlab": "warn"}

    @pytest.mark.requirement("WL-261")
    def test_validate_policy_valid(self):
        """Test policy validation with valid config."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github", "gitlab"])
        auditor.set_quota_budgets({"github": 100, "gitlab": 50})
        auditor.set_policy_modes({"github": "enforce", "gitlab": "warn"})

        is_valid, issues = auditor.validate_policy()

        assert is_valid is True
        assert len(issues) == 0

    @pytest.mark.requirement("WL-261")
    def test_validate_policy_no_connectors(self):
        """Test policy validation with no connectors."""
        auditor = SyncAuditor()

        is_valid, issues = auditor.validate_policy()

        assert is_valid is False
        assert "No connectors are enabled" in issues

    @pytest.mark.requirement("WL-261")
    def test_validate_policy_quota_without_connector(self):
        """Test policy validation with quota for disabled connector."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github"])
        auditor.set_quota_budgets({"github": 100, "unknown": 50})

        is_valid, issues = auditor.validate_policy()

        assert is_valid is False
        assert any("disabled connector" in issue for issue in issues)

    @pytest.mark.requirement("WL-261")
    def test_validate_policy_invalid_quota(self):
        """Test policy validation with invalid quota."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github"])
        auditor.set_quota_budgets({"github": 0})
        auditor.set_policy_modes({"github": "enforce"})

        is_valid, issues = auditor.validate_policy()

        assert is_valid is False
        assert any("must be > 0" in issue for issue in issues)

    @pytest.mark.requirement("WL-261")
    def test_validate_policy_missing_mode(self):
        """Test policy validation with missing policy mode."""
        auditor = SyncAuditor()
        auditor.set_enabled_connectors(["github", "gitlab"])
        auditor.set_quota_budgets({"github": 100, "gitlab": 50})
        auditor.set_policy_modes({"github": "enforce"})  # Missing gitlab

        is_valid, issues = auditor.validate_policy()

        assert is_valid is False
        assert any("gitlab" in issue and "Missing policy mode" in issue for issue in issues)
