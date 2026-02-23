"""Tests for environment profile drift validation.

# @trace WL-246
"""

from __future__ import annotations

import pytest

from thegent.integrations.env_profile_drift import (
    EnvDriftIssue,
    EnvProfileDriftValidator,
)


@pytest.mark.requirement("WL-246")
class TestEnvDriftIssue:
    """Test EnvDriftIssue dataclass."""

    def test_env_drift_issue_all_fields(self) -> None:
        """Test creating an EnvDriftIssue with all fields."""
        issue = EnvDriftIssue(key="DB_HOST", expected="localhost", actual="remote")
        assert issue.key == "DB_HOST"
        assert issue.expected == "localhost"
        assert issue.actual == "remote"

    def test_env_drift_issue_missing_expected(self) -> None:
        """Test creating an EnvDriftIssue with missing expected."""
        issue = EnvDriftIssue(key="UNUSED_VAR", expected=None, actual="value")
        assert issue.key == "UNUSED_VAR"
        assert issue.expected is None
        assert issue.actual == "value"

    def test_env_drift_issue_missing_actual(self) -> None:
        """Test creating an EnvDriftIssue with missing actual."""
        issue = EnvDriftIssue(key="REQUIRED_VAR", expected="needed", actual=None)
        assert issue.key == "REQUIRED_VAR"
        assert issue.expected == "needed"
        assert issue.actual is None


@pytest.mark.requirement("WL-246")
class TestEnvProfileDriftValidator:
    """Test EnvProfileDriftValidator."""

    def test_init(self) -> None:
        """Test initialization."""
        validator = EnvProfileDriftValidator()
        assert validator is not None

    def test_set_profile_empty(self) -> None:
        """Test setting an empty profile."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({})
        issues = validator.validate({})
        assert issues == []

    def test_set_profile_single(self) -> None:
        """Test setting a profile with one variable."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"DB_HOST": "localhost"})
        issues = validator.validate({"DB_HOST": "localhost"})
        assert issues == []

    def test_set_profile_multiple(self) -> None:
        """Test setting a profile with multiple variables."""
        validator = EnvProfileDriftValidator()
        profile = {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_USER": "admin"}
        validator.set_profile(profile)
        issues = validator.validate(profile)
        assert issues == []

    def test_validate_exact_match(self) -> None:
        """Test validate returns no issues for exact match."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "value1", "VAR2": "value2"})
        issues = validator.validate({"VAR1": "value1", "VAR2": "value2"})
        assert issues == []

    def test_validate_missing_variable(self) -> None:
        """Test validate detects missing variables."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "value1", "VAR2": "value2"})
        issues = validator.validate({"VAR1": "value1"})
        assert len(issues) == 1
        assert issues[0].key == "VAR2"
        assert issues[0].expected == "value2"
        assert issues[0].actual is None

    def test_validate_mismatched_value(self) -> None:
        """Test validate detects mismatched values."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "expected"})
        issues = validator.validate({"VAR1": "actual"})
        assert len(issues) == 1
        assert issues[0].key == "VAR1"
        assert issues[0].expected == "expected"
        assert issues[0].actual == "actual"

    def test_validate_unexpected_variable(self) -> None:
        """Test validate detects unexpected variables."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "value1"})
        issues = validator.validate({"VAR1": "value1", "VAR2": "unexpected"})
        assert len(issues) == 1
        assert issues[0].key == "VAR2"
        assert issues[0].expected is None
        assert issues[0].actual == "unexpected"

    def test_validate_multiple_issues(self) -> None:
        """Test validate returns all issues."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "v1", "VAR2": "v2", "VAR3": "v3"})
        env = {"VAR1": "v1", "VAR2": "wrong", "VAR4": "extra"}
        issues = validator.validate(env)
        assert len(issues) == 3
        keys = {issue.key for issue in issues}
        assert keys == {"VAR2", "VAR3", "VAR4"}

    def test_validate_empty_profile(self) -> None:
        """Test validate with empty profile."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({})
        issues = validator.validate({"VAR1": "value1"})
        assert len(issues) == 1
        assert issues[0].key == "VAR1"
        assert issues[0].expected is None

    def test_validate_empty_env(self) -> None:
        """Test validate with empty environment."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "value1", "VAR2": "value2"})
        issues = validator.validate({})
        assert len(issues) == 2
        assert all(issue.actual is None for issue in issues)

    def test_is_valid_true(self) -> None:
        """Test is_valid returns True for matching config."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "v1", "VAR2": "v2"})
        assert validator.is_valid({"VAR1": "v1", "VAR2": "v2"}) is True

    def test_is_valid_false_missing(self) -> None:
        """Test is_valid returns False for missing variables."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "v1"})
        assert validator.is_valid({"VAR2": "v2"}) is False

    def test_is_valid_false_mismatch(self) -> None:
        """Test is_valid returns False for mismatched values."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "expected"})
        assert validator.is_valid({"VAR1": "actual"}) is False

    def test_is_valid_false_extra(self) -> None:
        """Test is_valid returns False for extra variables."""
        validator = EnvProfileDriftValidator()
        validator.set_profile({"VAR1": "v1"})
        assert validator.is_valid({"VAR1": "v1", "VAR2": "extra"}) is False

    def test_profile_isolation(self) -> None:
        """Test that setting profile doesn't affect previous instances."""
        v1 = EnvProfileDriftValidator()
        v2 = EnvProfileDriftValidator()
        v1.set_profile({"VAR1": "v1"})
        v2.set_profile({"VAR2": "v2"})
        assert v1.is_valid({"VAR1": "v1"}) is True
        assert v2.is_valid({"VAR2": "v2"}) is True
        assert v1.is_valid({"VAR2": "v2"}) is False
        assert v2.is_valid({"VAR1": "v1"}) is False
