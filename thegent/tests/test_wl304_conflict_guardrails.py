"""Tests for WL-304 Conflict Growth Guardrails.

# @trace WL-304
"""

from __future__ import annotations

import pytest

from thegent.integrations.conflict_guardrails import (
    ConflictGrowthGuardrail,
    ConflictLimitExceeded,
)


class TestConflictGrowthGuardrailInit:
    """Tests for guardrail initialization."""

    def test_init_default_values(self) -> None:
        """Default configuration is max=50, warn=25."""
        guard = ConflictGrowthGuardrail()
        assert guard.max_conflicts == 50
        assert guard.warn_threshold == 25

    def test_init_custom_values(self) -> None:
        """Custom max and warn thresholds."""
        guard = ConflictGrowthGuardrail(max_conflicts=100, warn_threshold=50)
        assert guard.max_conflicts == 100
        assert guard.warn_threshold == 50

    def test_init_max_conflicts_zero_raises(self) -> None:
        """max_conflicts=0 raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            ConflictGrowthGuardrail(max_conflicts=0)

    def test_init_max_conflicts_negative_raises(self) -> None:
        """Negative max_conflicts raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            ConflictGrowthGuardrail(max_conflicts=-1)

    def test_init_warn_threshold_zero_raises(self) -> None:
        """warn_threshold=0 raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            ConflictGrowthGuardrail(warn_threshold=0)

    def test_init_warn_threshold_negative_raises(self) -> None:
        """Negative warn_threshold raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            ConflictGrowthGuardrail(warn_threshold=-1)

    def test_init_warn_above_max_raises(self) -> None:
        """warn_threshold > max_conflicts raises ValueError."""
        with pytest.raises(ValueError, match="<="):
            ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=100)

    @pytest.mark.requirement("WL-304")
    def test_init_warn_equal_max_allowed(self) -> None:
        """warn_threshold == max_conflicts is allowed."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=50)
        assert guard.warn_threshold == guard.max_conflicts


class TestCheck:
    """Tests for check method."""

    def test_check_below_max_passes(self) -> None:
        """Count below max doesn't raise."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        guard.check(25)  # Should not raise

    def test_check_at_max_passes(self) -> None:
        """Count at max doesn't raise."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        guard.check(50)  # Should not raise

    def test_check_above_max_raises(self) -> None:
        """Count above max raises ConflictLimitExceeded."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        with pytest.raises(ConflictLimitExceeded):
            guard.check(51)

    def test_check_well_above_max_raises(self) -> None:
        """Well above max raises ConflictLimitExceeded."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        with pytest.raises(ConflictLimitExceeded):
            guard.check(100)

    def test_check_zero_conflicts(self) -> None:
        """Zero conflicts passes."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        guard.check(0)  # Should not raise

    def test_check_negative_raises(self) -> None:
        """Negative count raises ValueError."""
        guard = ConflictGrowthGuardrail()
        with pytest.raises(ValueError, match="non-negative"):
            guard.check(-1)

    def test_check_exception_message(self) -> None:
        """Exception message includes count and limit."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        with pytest.raises(ConflictLimitExceeded) as exc_info:
            guard.check(75)
        assert "75" in str(exc_info.value)
        assert "50" in str(exc_info.value)

    @pytest.mark.requirement("WL-304")
    def test_check_is_strict(self) -> None:
        """check enforces hard limit strictly."""
        guard = ConflictGrowthGuardrail(max_conflicts=50)
        guard.check(50)
        with pytest.raises(ConflictLimitExceeded):
            guard.check(51)


class TestWarnLevel:
    """Tests for warn_level method."""

    def test_warn_level_below_threshold(self) -> None:
        """Count below threshold returns False."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        assert guard.warn_level(24) is False

    def test_warn_level_at_threshold(self) -> None:
        """Count at threshold returns True."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        assert guard.warn_level(25) is True

    def test_warn_level_above_threshold(self) -> None:
        """Count above threshold returns True."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        assert guard.warn_level(30) is True

    def test_warn_level_at_max(self) -> None:
        """Count at max also triggers warn."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        assert guard.warn_level(50) is True

    def test_warn_level_zero(self) -> None:
        """Zero conflicts doesn't warn."""
        guard = ConflictGrowthGuardrail(warn_threshold=25)
        assert guard.warn_level(0) is False

    def test_warn_level_negative_raises(self) -> None:
        """Negative count raises ValueError."""
        guard = ConflictGrowthGuardrail()
        with pytest.raises(ValueError, match="non-negative"):
            guard.warn_level(-1)

    @pytest.mark.requirement("WL-304")
    def test_warn_level_independent_of_check(self) -> None:
        """warn_level doesn't enforce hard limit."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        # Can call warn_level on exceeded count without raising
        result = guard.warn_level(100)
        assert result is True


class TestStatus:
    """Tests for status method."""

    def test_status_structure(self) -> None:
        """Status returns dict with required keys."""
        guard = ConflictGrowthGuardrail()
        result = guard.status(10)

        assert isinstance(result, dict)
        assert "count" in result
        assert "warn" in result
        assert "exceeded" in result

    def test_status_below_threshold(self) -> None:
        """Below threshold: warn=False, exceeded=False."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        status = guard.status(10)

        assert status["count"] == 10
        assert status["warn"] is False
        assert status["exceeded"] is False

    def test_status_at_threshold(self) -> None:
        """At threshold: warn=True, exceeded=False."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        status = guard.status(25)

        assert status["count"] == 25
        assert status["warn"] is True
        assert status["exceeded"] is False

    def test_status_at_max(self) -> None:
        """At max: warn=True, exceeded=False."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        status = guard.status(50)

        assert status["count"] == 50
        assert status["warn"] is True
        assert status["exceeded"] is False

    def test_status_above_max(self) -> None:
        """Above max: warn=True, exceeded=True."""
        guard = ConflictGrowthGuardrail(max_conflicts=50, warn_threshold=25)
        status = guard.status(51)

        assert status["count"] == 51
        assert status["warn"] is True
        assert status["exceeded"] is True

    def test_status_zero(self) -> None:
        """Zero conflicts: warn=False, exceeded=False."""
        guard = ConflictGrowthGuardrail()
        status = guard.status(0)

        assert status["count"] == 0
        assert status["warn"] is False
        assert status["exceeded"] is False

    def test_status_negative_raises(self) -> None:
        """Negative count raises ValueError."""
        guard = ConflictGrowthGuardrail()
        with pytest.raises(ValueError, match="non-negative"):
            guard.status(-1)

    @pytest.mark.requirement("WL-304")
    def test_status_comprehensive(self) -> None:
        """status provides complete information."""
        guard = ConflictGrowthGuardrail(max_conflicts=100, warn_threshold=50)

        # Low
        assert guard.status(10) == {"count": 10, "warn": False, "exceeded": False}
        # Warning
        assert guard.status(50) == {"count": 50, "warn": True, "exceeded": False}
        # Critical
        assert guard.status(101) == {"count": 101, "warn": True, "exceeded": True}
