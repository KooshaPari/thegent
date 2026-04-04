"""Integration tests for conformance checking with telemetry.

Tests the conformance suite running against real adapters with
telemetry recording, and drift detection across multiple runs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from thegent.contracts.conformance import run_conformance_suite
from thegent.contracts.telemetry import (
    EVENT_NORMALIZATION,
    EVENT_SCHEMA_DRIFT_STRUCTURAL,
    ContractTelemetry,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
class TestConformanceSuiteWithTelemetry:
    """Tests that the conformance suite integrates with drift telemetry."""

    def test_conformance_suite_runs_all_tests(self) -> None:
        # @trace FR-CTR-012
        """The conformance suite should run all built-in tests and produce a report."""
        report = run_conformance_suite()

        assert report["total"] > 0
        assert report["passed"] + report["failed"] == report["total"]
        assert isinstance(report["results"], list)
        assert len(report["results"]) == report["total"]

    def test_conformance_suite_with_session_dir_checks_drift(
        self,
        tmp_path: Path,
    ) -> None:
        # @trace FR-CTR-012
        """When session_dir is provided, conformance should also check drift."""
        report = run_conformance_suite(session_dir=tmp_path)

        assert report["drift_checked"] is True
        assert "drift_issues" in report
        assert isinstance(report["drift_issues"], list)
        assert "drift_budget" in report

    def test_conformance_suite_detects_budget_breach(self, tmp_path: Path) -> None:
        # @trace FR-CTR-006
        """When structural drift exceeds budget, conformance should report it."""
        telemetry = ContractTelemetry(tmp_path)

        # Seed enough structural drift events to exceed the 5% budget
        for i in range(20):
            telemetry.record_normalization(
                run_id=f"run-{i}",
                provider="test-provider",
                contract="xml-tags",
                confidence=0.8,
                success=True,
                event_type=EVENT_NORMALIZATION,
            )
        # Add structural drift events (>5% = >1 out of 20)
        for i in range(3):
            telemetry.emit_drift_event(
                run_id=f"drift-{i}",
                provider="test-provider",
                contract="xml-tags",
                drift_type="structural",
                details={"reason": "test"},
            )
            telemetry.record_normalization(
                run_id=f"drift-{i}",
                provider="test-provider",
                contract="xml-tags",
                confidence=0.3,
                success=False,
                event_type=EVENT_SCHEMA_DRIFT_STRUCTURAL,
            )

        report = run_conformance_suite(session_dir=tmp_path)

        assert report["drift_checked"] is True
        budget = report["drift_budget"]
        # With 3 structural drift events out of 23 total, rate is ~13%
        assert budget["structural_rate_pct"] > 5.0


@pytest.mark.integration
class TestDriftDetectionAcrossRuns:
    """Tests drift detection when performance degrades over multiple runs."""

    def test_no_drift_with_consistent_performance(self, tmp_path: Path) -> None:
        # @trace FR-CTR-006
        """Consistent performance across many runs should produce no drift alerts."""
        telemetry = ContractTelemetry(tmp_path)

        # Record 200 consistent normalization events
        for i in range(200):
            telemetry.record_normalization(
                run_id=f"run-{i}",
                provider="claude",
                contract="xml-tags",
                confidence=0.9,
                success=True,
                event_type=EVENT_NORMALIZATION,
            )

        drift_issues = telemetry.detect_drift(window_size=50)
        assert drift_issues == []

    def test_drift_detected_on_confidence_drop(self, tmp_path: Path) -> None:
        # @trace FR-CTR-006
        """A significant drop in confidence should trigger drift detection."""
        telemetry = ContractTelemetry(tmp_path)

        # Historical: high confidence
        for i in range(150):
            telemetry.record_normalization(
                run_id=f"hist-{i}",
                provider="claude",
                contract="xml-tags",
                confidence=0.95,
                success=True,
                event_type=EVENT_NORMALIZATION,
            )

        # Recent: low confidence (simulating degradation)
        for i in range(50):
            telemetry.record_normalization(
                run_id=f"recent-{i}",
                provider="claude",
                contract="xml-tags",
                confidence=0.4,
                success=False,
                event_type=EVENT_NORMALIZATION,
            )

        drift_issues = telemetry.detect_drift(window_size=50, drift_threshold=0.15)
        assert len(drift_issues) > 0
        assert any("confidence" in issue.lower() for issue in drift_issues)

    def test_drift_detected_on_fallback_rate_increase(self, tmp_path: Path) -> None:
        # @trace FR-CTR-012
        """An increase in fallback rate should trigger drift detection."""
        telemetry = ContractTelemetry(tmp_path)

        # Historical: no fallbacks
        for i in range(150):
            telemetry.record_normalization(
                run_id=f"hist-{i}",
                provider="claude",
                contract="xml-tags",
                confidence=0.9,
                success=True,
                event_type=EVENT_NORMALIZATION,
            )

        # Recent: lots of fallbacks
        for i in range(50):
            telemetry.record_normalization(
                run_id=f"recent-{i}",
                provider="claude",
                contract="fallback-plain",
                confidence=0.3,
                success=False,
                event_type=EVENT_NORMALIZATION,
            )

        drift_issues = telemetry.detect_drift(window_size=50, drift_threshold=0.15)
        assert len(drift_issues) > 0
        assert any("fallback" in issue.lower() for issue in drift_issues)
