"""Tests for WL-170: Error Budget and Escalation Thresholds.

# @trace WL-170
"""

from __future__ import annotations

import pytest

from thegent.integrations.error_budget import (
    ErrorBudgetConfig,
    ErrorBudgetTracker,
)


@pytest.mark.requirement("WL-170")
def test_error_budget_config_defaults() -> None:
    """Test ErrorBudgetConfig has correct default values."""
    config = ErrorBudgetConfig()

    assert config.max_consecutive_failures == 3
    assert config.max_failure_rate == 0.5
    assert config.escalation_after == 5


@pytest.mark.requirement("WL-170")
def test_error_budget_config_custom() -> None:
    """Test ErrorBudgetConfig with custom values."""
    config = ErrorBudgetConfig(
        max_consecutive_failures=5,
        max_failure_rate=0.3,
        escalation_after=10,
    )

    assert config.max_consecutive_failures == 5
    assert config.max_failure_rate == 0.3
    assert config.escalation_after == 10


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_initialization() -> None:
    """Test ErrorBudgetTracker initialization."""
    tracker = ErrorBudgetTracker()

    # Should start with no stats
    stats = tracker.get_stats()
    assert stats["success_count"] == 0
    assert stats["failure_count"] == 0
    assert stats["consecutive_failures"] == 0
    assert stats["total_operations"] == 0
    assert stats["current_failure_rate"] == 0.0


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_record_success() -> None:
    """Test recording successful operations."""
    tracker = ErrorBudgetTracker()

    tracker.record_success()
    tracker.record_success()

    stats = tracker.get_stats()
    assert stats["success_count"] == 2
    assert stats["failure_count"] == 0
    assert stats["consecutive_failures"] == 0
    assert stats["total_operations"] == 2


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_record_failure() -> None:
    """Test recording failed operations."""
    tracker = ErrorBudgetTracker()

    tracker.record_failure()
    tracker.record_failure()

    stats = tracker.get_stats()
    assert stats["success_count"] == 0
    assert stats["failure_count"] == 2
    assert stats["consecutive_failures"] == 2
    assert stats["total_operations"] == 2
    assert stats["current_failure_rate"] == 1.0


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_consecutive_failures_reset() -> None:
    """Test that consecutive failure counter resets on success."""
    tracker = ErrorBudgetTracker()

    tracker.record_failure()
    tracker.record_failure()
    assert tracker.get_stats()["consecutive_failures"] == 2

    tracker.record_success()
    assert tracker.get_stats()["consecutive_failures"] == 0


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_should_escalate_false() -> None:
    """Test should_escalate returns False below threshold."""
    tracker = ErrorBudgetTracker()

    # Record 3 failures (below default escalation_after=5)
    tracker.record_failure()
    tracker.record_failure()
    tracker.record_failure()

    assert not tracker.should_escalate()


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_should_escalate_true() -> None:
    """Test should_escalate returns True at threshold."""
    tracker = ErrorBudgetTracker()

    # Record 5 failures (meets default escalation_after=5)
    for _ in range(5):
        tracker.record_failure()

    assert tracker.should_escalate()


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_should_hard_fail_consecutive() -> None:
    """Test should_hard_fail on consecutive failure threshold."""
    tracker = ErrorBudgetTracker()

    # Record max_consecutive_failures-1 (2)
    for _ in range(2):
        tracker.record_failure()

    assert not tracker.should_hard_fail()

    # Record one more to reach max_consecutive_failures (3)
    tracker.record_failure()
    assert not tracker.should_hard_fail()

    # Record one more to exceed threshold
    tracker.record_failure()
    assert tracker.should_hard_fail()


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_should_hard_fail_rate() -> None:
    """Test should_hard_fail on failure rate threshold."""
    tracker = ErrorBudgetTracker()

    # Record 3 failures and 1 success = 75% failure rate (exceeds 50% threshold)
    for _ in range(3):
        tracker.record_failure()
    tracker.record_success()

    assert tracker.should_hard_fail()


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_should_hard_fail_false() -> None:
    """Test should_hard_fail returns False when under both thresholds."""
    tracker = ErrorBudgetTracker()

    # Record 1 failure and 3 successes = 25% failure rate, 1 consecutive
    tracker.record_failure()
    for _ in range(3):
        tracker.record_success()

    assert not tracker.should_hard_fail()


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_reset() -> None:
    """Test resetting the error budget tracker."""
    tracker = ErrorBudgetTracker()

    # Build up some stats
    for _ in range(5):
        tracker.record_failure()

    stats = tracker.get_stats()
    assert stats["failure_count"] == 5

    # Reset
    tracker.reset()

    stats = tracker.get_stats()
    assert stats["success_count"] == 0
    assert stats["failure_count"] == 0
    assert stats["consecutive_failures"] == 0
    assert stats["total_operations"] == 0
    assert stats["current_failure_rate"] == 0.0


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_get_stats() -> None:
    """Test getting full statistics."""
    tracker = ErrorBudgetTracker()

    # Record mixed results
    tracker.record_success()
    tracker.record_failure()
    tracker.record_failure()
    tracker.record_success()

    stats = tracker.get_stats()

    assert stats["success_count"] == 2
    assert stats["failure_count"] == 2
    assert stats["consecutive_failures"] == 0  # reset after last success
    assert stats["total_operations"] == 4
    assert stats["current_failure_rate"] == 0.5


@pytest.mark.requirement("WL-170")
def test_error_budget_tracker_custom_config() -> None:
    """Test ErrorBudgetTracker with custom configuration."""
    config = ErrorBudgetConfig(
        max_consecutive_failures=2,
        max_failure_rate=0.3,
        escalation_after=4,
    )
    tracker = ErrorBudgetTracker(config)

    # Test escalation at custom threshold
    for _ in range(4):
        tracker.record_failure()

    assert tracker.should_escalate()

    # Reset and test hard fail at custom threshold
    tracker.reset()
    for _ in range(3):
        tracker.record_failure()

    assert tracker.should_hard_fail()  # exceeds max_consecutive_failures=2
