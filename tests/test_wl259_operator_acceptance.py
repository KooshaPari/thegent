"""Tests for WL-259: Operator Acceptance Tests.

Verifies suite management, test registration, pass/fail/pending tracking,
and summary reporting.

# @trace WL-259
"""

from __future__ import annotations

import pytest


@pytest.mark.requirement("WL-259")
class TestOperatorAcceptanceSuite:
    """WL-259: Operator Acceptance Test suite management."""

    def test_add_test_creates_pending_test(self):
        """# @trace WL-259 — add() creates a test with passed=None."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        test = suite.add("smoke_test", "Basic smoke test")

        assert test.name == "smoke_test"
        assert test.description == "Basic smoke test"
        assert test.passed is None

    def test_add_test_duplicate_raises_error(self):
        """# @trace WL-259 — adding duplicate test name raises ValueError."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("test1", "First test")

        with pytest.raises(ValueError, match="already exists"):
            suite.add("test1", "Duplicate test")

    def test_mark_passed_sets_flag(self):
        """# @trace WL-259 — mark_passed() sets passed=True."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("test_a", "Test A")
        suite.mark_passed("test_a")

        results = suite.results()
        assert results[0].passed is True

    def test_mark_failed_sets_flag(self):
        """# @trace WL-259 — mark_failed() sets passed=False."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("test_b", "Test B")
        suite.mark_failed("test_b")

        results = suite.results()
        assert results[0].passed is False

    def test_mark_passed_nonexistent_test_raises_keyerror(self):
        """# @trace WL-259 — mark_passed() on missing test raises KeyError."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()

        with pytest.raises(KeyError, match="not found"):
            suite.mark_passed("nonexistent")

    def test_mark_failed_nonexistent_test_raises_keyerror(self):
        """# @trace WL-259 — mark_failed() on missing test raises KeyError."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()

        with pytest.raises(KeyError, match="not found"):
            suite.mark_failed("nonexistent")

    def test_results_returns_sorted_list(self):
        """# @trace WL-259 — results() returns tests sorted by name."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("zebra", "Z test")
        suite.add("alpha", "A test")
        suite.add("beta", "B test")

        results = suite.results()
        names = [t.name for t in results]

        assert names == ["alpha", "beta", "zebra"]

    def test_summary_counts_passed(self):
        """# @trace WL-259 — summary() correctly counts passed tests."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("t1", "T1")
        suite.add("t2", "T2")
        suite.add("t3", "T3")
        suite.mark_passed("t1")
        suite.mark_passed("t2")

        summary = suite.summary()

        assert summary["passed"] == 2

    def test_summary_counts_failed(self):
        """# @trace WL-259 — summary() correctly counts failed tests."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("t1", "T1")
        suite.add("t2", "T2")
        suite.mark_failed("t1")

        summary = suite.summary()

        assert summary["failed"] == 1

    def test_summary_counts_pending(self):
        """# @trace WL-259 — summary() correctly counts pending tests."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("t1", "T1")
        suite.add("t2", "T2")
        suite.add("t3", "T3")
        suite.mark_passed("t1")
        suite.mark_failed("t2")

        summary = suite.summary()

        assert summary["pending"] == 1

    def test_summary_all_fields(self):
        """# @trace WL-259 — summary() includes passed, failed, pending keys."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()
        suite.add("t1", "T1")
        suite.add("t2", "T2")
        suite.add("t3", "T3")
        suite.add("t4", "T4")
        suite.mark_passed("t1")
        suite.mark_passed("t2")
        suite.mark_failed("t3")

        summary = suite.summary()

        assert set(summary.keys()) == {"passed", "failed", "pending"}
        assert summary == {"passed": 2, "failed": 1, "pending": 1}

    def test_summary_empty_suite(self):
        """# @trace WL-259 — summary() on empty suite returns zeros."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()

        summary = suite.summary()

        assert summary == {"passed": 0, "failed": 0, "pending": 0}

    def test_results_empty_suite(self):
        """# @trace WL-259 — results() on empty suite returns empty list."""
        from thegent.integrations.operator_acceptance import OperatorAcceptanceSuite

        suite = OperatorAcceptanceSuite()

        results = suite.results()

        assert results == []
