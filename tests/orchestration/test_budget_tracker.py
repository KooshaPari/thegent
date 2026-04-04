"""Tests for BudgetTracker: per-node token budget enforcement.

@trace FR-ORC-086
"""

from __future__ import annotations

import pytest
from thegent.orchestration.budget_tracker import BudgetExceededError, BudgetTracker


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetExceededError:
    def test_budget_exceeded_error_attributes(self) -> None:
        """BudgetExceededError carries node_id, budget, and used attributes."""
        err = BudgetExceededError(node_id="node-1", budget=100, used=150)
        assert err.node_id == "node-1"
        assert err.budget == 100
        assert err.used == 150
        assert isinstance(err, RuntimeError)

    def test_budget_exceeded_error_message(self) -> None:
        """BudgetExceededError str includes node_id, budget, and used."""
        err = BudgetExceededError(node_id="node-x", budget=50, used=75)
        msg = str(err)
        assert "node-x" in msg
        assert "50" in msg
        assert "75" in msg


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerCheck:
    def test_budget_tracker_check_within_budget(self) -> None:
        """check() passes when tokens <= budget."""
        tracker = BudgetTracker(budgets={"n1": 1000})
        tracker.check("n1", 999)  # must not raise
        tracker.check("n1", 1000)  # exactly at budget must not raise

    def test_budget_tracker_check_exceeds_budget_raises(self) -> None:
        """check() raises BudgetExceededError when tokens > budget."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(BudgetExceededError) as exc_info:
            tracker.check("n1", 101)
        assert exc_info.value.node_id == "n1"
        assert exc_info.value.budget == 100
        assert exc_info.value.used == 101

    def test_budget_tracker_check_unknown_node_raises(self) -> None:
        """check() raises KeyError for unknown node_id."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(KeyError):
            tracker.check("unknown", 10)


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerRecord:
    def test_budget_tracker_record_cumulative(self) -> None:
        """record() accumulates usage cumulatively."""
        tracker = BudgetTracker(budgets={"n1": 1000})
        tracker.record("n1", 300)
        tracker.record("n1", 400)
        assert tracker.usage("n1") == 700

    def test_budget_tracker_record_exceeds_cumulative_raises(self) -> None:
        """record() raises BudgetExceededError when cumulative usage exceeds budget."""
        tracker = BudgetTracker(budgets={"n1": 500})
        tracker.record("n1", 300)
        with pytest.raises(BudgetExceededError) as exc_info:
            tracker.record("n1", 250)  # 300 + 250 = 550 > 500
        assert exc_info.value.node_id == "n1"
        assert exc_info.value.budget == 500
        assert exc_info.value.used == 550

    def test_budget_tracker_record_exactly_at_budget_passes(self) -> None:
        """record() does not raise when cumulative equals budget exactly."""
        tracker = BudgetTracker(budgets={"n1": 500})
        tracker.record("n1", 250)
        tracker.record("n1", 250)  # total = 500, must not raise
        assert tracker.usage("n1") == 500

    def test_budget_tracker_record_unknown_node_raises(self) -> None:
        """record() raises KeyError for unknown node_id."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(KeyError):
            tracker.record("unknown", 10)


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerUsage:
    def test_budget_tracker_usage_returns_cumulative(self) -> None:
        """usage() returns the sum of all recorded tokens for a node."""
        tracker = BudgetTracker(budgets={"n1": 1000})
        assert tracker.usage("n1") == 0
        tracker.record("n1", 100)
        assert tracker.usage("n1") == 100
        tracker.record("n1", 200)
        assert tracker.usage("n1") == 300

    def test_budget_tracker_usage_unknown_node_raises(self) -> None:
        """usage() raises KeyError for unknown node_id."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(KeyError):
            tracker.usage("unknown")


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerRemaining:
    def test_budget_tracker_remaining_calculation(self) -> None:
        """remaining() returns budget minus cumulative usage."""
        tracker = BudgetTracker(budgets={"n1": 1000})
        tracker.record("n1", 300)
        assert tracker.remaining("n1") == 700

    def test_budget_tracker_remaining_zero_usage(self) -> None:
        """remaining() equals full budget when no usage recorded."""
        tracker = BudgetTracker(budgets={"n1": 500})
        assert tracker.remaining("n1") == 500

    def test_budget_tracker_remaining_unknown_node_raises(self) -> None:
        """remaining() raises KeyError for unknown node_id."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(KeyError):
            tracker.remaining("unknown")


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerReset:
    def test_budget_tracker_reset_clears_usage(self) -> None:
        """reset() zeroes the usage counter for a given node_id."""
        tracker = BudgetTracker(budgets={"n1": 1000})
        tracker.record("n1", 500)
        assert tracker.usage("n1") == 500
        tracker.reset("n1")
        assert tracker.usage("n1") == 0

    def test_budget_tracker_reset_allows_new_records(self) -> None:
        """After reset(), recording works again up to full budget."""
        tracker = BudgetTracker(budgets={"n1": 500})
        tracker.record("n1", 499)
        tracker.reset("n1")
        tracker.record("n1", 499)  # must not raise
        assert tracker.usage("n1") == 499

    def test_budget_tracker_reset_unknown_node_raises(self) -> None:
        """reset() raises KeyError for unknown node_id."""
        tracker = BudgetTracker(budgets={"n1": 100})
        with pytest.raises(KeyError):
            tracker.reset("unknown")


@pytest.mark.requirement("FR-ORC-086")
class TestBudgetTrackerMultipleNodes:
    def test_budget_tracker_multiple_nodes_independent(self) -> None:
        """Usage for one node does not affect another node's budget."""
        tracker = BudgetTracker(budgets={"n1": 100, "n2": 200})
        tracker.record("n1", 80)
        assert tracker.usage("n2") == 0
        assert tracker.remaining("n2") == 200

    def test_budget_tracker_empty_budgets(self) -> None:
        """BudgetTracker works with empty budgets dict."""
        tracker = BudgetTracker(budgets={})
        with pytest.raises(KeyError):
            tracker.check("any", 10)
