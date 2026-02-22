"""Tests for WL-192: Startup scope and reachability validation.

# @trace WL-192
"""

from __future__ import annotations

import pytest

from thegent.integrations.startup_validation import StartupValidationResult, StartupValidator


class TestStartupValidationResult:
    """Tests for StartupValidationResult dataclass."""

    @pytest.mark.requirement("WL-192")
    def test_result_with_passed_true(self):
        """# @trace WL-192 — result can be created with passed=True."""
        result = StartupValidationResult(passed=True)
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []

    @pytest.mark.requirement("WL-192")
    def test_result_with_passed_false_and_errors(self):
        """# @trace WL-192 — result can contain errors when passed=False."""
        errors = ["Error 1", "Error 2"]
        result = StartupValidationResult(passed=False, errors=errors)
        assert result.passed is False
        assert result.errors == errors

    @pytest.mark.requirement("WL-192")
    def test_result_with_warnings(self):
        """# @trace WL-192 — result can contain warnings."""
        warnings = ["Warning 1", "Warning 2"]
        result = StartupValidationResult(passed=True, warnings=warnings)
        assert result.passed is True
        assert result.warnings == warnings


class TestStartupValidator:
    """Tests for StartupValidator class."""

    @pytest.mark.requirement("WL-192")
    def test_check_auth_scopes_all_available(self):
        """# @trace WL-192 — check_auth_scopes returns True when all scopes available."""
        validator = StartupValidator()
        result = validator.check_auth_scopes(
            ["read:user", "repo"],
            ["read:user", "repo", "workflow"],
        )
        assert result is True

    @pytest.mark.requirement("WL-192")
    def test_check_auth_scopes_missing_scopes(self):
        """# @trace WL-192 — check_auth_scopes returns False when scopes missing."""
        validator = StartupValidator()
        result = validator.check_auth_scopes(
            ["read:user", "repo", "workflow"],
            ["read:user", "repo"],
        )
        assert result is False

    @pytest.mark.requirement("WL-192")
    def test_check_auth_scopes_empty_required(self):
        """# @trace WL-192 — check_auth_scopes returns True for empty required scopes."""
        validator = StartupValidator()
        result = validator.check_auth_scopes([], ["read:user", "repo"])
        assert result is True

    @pytest.mark.requirement("WL-192")
    def test_check_auth_scopes_empty_available_with_required(self):
        """# @trace WL-192 — check_auth_scopes returns False when required but available empty."""
        validator = StartupValidator()
        result = validator.check_auth_scopes(["read:user"], [])
        assert result is False

    @pytest.mark.requirement("WL-192")
    def test_check_endpoint_reachability_returns_dict(self):
        """# @trace WL-192 — check_endpoint_reachability returns dict mapping endpoints to bool."""
        validator = StartupValidator()
        endpoints = ["https://api.github.com", "https://example.com"]
        result = validator.check_endpoint_reachability(endpoints)
        assert isinstance(result, dict)
        assert len(result) == 2
        assert all(isinstance(v, bool) for v in result.values())

    @pytest.mark.requirement("WL-192")
    def test_check_endpoint_reachability_all_true_stub(self):
        """# @trace WL-192 — stub implementation returns all endpoints as reachable (True)."""
        validator = StartupValidator()
        endpoints = ["https://api.github.com", "https://example.com"]
        result = validator.check_endpoint_reachability(endpoints)
        assert all(result.values()), "Stub should return all endpoints as reachable"

    @pytest.mark.requirement("WL-192")
    def test_check_endpoint_reachability_empty_list(self):
        """# @trace WL-192 — check_endpoint_reachability returns empty dict for empty endpoints."""
        validator = StartupValidator()
        result = validator.check_endpoint_reachability([])
        assert result == {}

    @pytest.mark.requirement("WL-192")
    def test_validate_all_empty_config(self):
        """# @trace WL-192 — validate_all with empty config returns passed=True."""
        validator = StartupValidator()
        result = validator.validate_all({})
        assert result.passed is True
        assert result.errors == []

    @pytest.mark.requirement("WL-192")
    def test_validate_all_missing_required_scopes(self):
        """# @trace WL-192 — validate_all fails when required scopes are missing."""
        validator = StartupValidator()
        result = validator.validate_all(
            {
                "required_scopes": ["repo", "workflow"],
                "available_scopes": ["repo"],
            }
        )
        assert result.passed is False
        assert len(result.errors) > 0
        assert "workflow" in result.errors[0]

    @pytest.mark.requirement("WL-192")
    def test_validate_all_scopes_satisfied(self):
        """# @trace WL-192 — validate_all passes when all required scopes available."""
        validator = StartupValidator()
        result = validator.validate_all(
            {
                "required_scopes": ["repo", "workflow"],
                "available_scopes": ["repo", "workflow", "read:user"],
            }
        )
        assert result.passed is True
        assert result.errors == []

    @pytest.mark.requirement("WL-192")
    def test_validate_all_with_endpoints(self):
        """# @trace WL-192 — validate_all includes endpoint check in validation."""
        validator = StartupValidator()
        result = validator.validate_all(
            {
                "endpoints": ["https://api.github.com"],
            }
        )
        # Stub returns all as reachable, so no warnings expected
        assert result.passed is True

    @pytest.mark.requirement("WL-192")
    def test_validate_all_combined_scopes_and_endpoints(self):
        """# @trace WL-192 — validate_all validates both scopes and endpoints together."""
        validator = StartupValidator()
        result = validator.validate_all(
            {
                "required_scopes": ["repo"],
                "available_scopes": ["repo", "workflow"],
                "endpoints": ["https://api.github.com"],
            }
        )
        assert result.passed is True
        assert result.errors == []
