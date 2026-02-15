"""Conformance test suite for provider adapters.

Ensures that adapters correctly normalize common provider output patterns
and handle edge cases/malformed input gracefully. Supports optional drift
alarm checks via ContractTelemetry.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from thegent.contracts.adapters import normalize_output
from thegent.contracts.csm import CSMStatus


@dataclass
class ConformanceTest:
    name: str
    provider: str
    raw_output: str | dict[str, Any]
    expected_status: CSMStatus
    min_confidence: float = 0.5
    check_summary: bool = True


def _build_conformance_tests() -> list[ConformanceTest]:
    """Build the full conformance test suite."""
    return [
        ConformanceTest(
            name="XML Basic (Gemini)",
            provider="gemini",
            raw_output="<STATUS>COMPLETED</STATUS><SUMMARY>Done</SUMMARY><PROGRESS>100%</PROGRESS>",
            expected_status=CSMStatus.COMPLETED,
            min_confidence=0.9,
        ),
        ConformanceTest(
            name="XML Partial (Claude)",
            provider="claude",
            raw_output="<STATUS>IN_PROGRESS</STATUS><PROGRESS>50</PROGRESS>",
            expected_status=CSMStatus.IN_PROGRESS,
            min_confidence=0.8,
            check_summary=False,
        ),
        ConformanceTest(
            name="Plain Text Fallback",
            provider="unknown",
            raw_output="The task is finished and everything looks good.",
            expected_status=CSMStatus.COMPLETED,
            min_confidence=0.3,
        ),
        ConformanceTest(
            name="XML Malformed (truncated)",
            provider="copilot",
            raw_output="<STATUS>COMPLETED<SUMMARY>Missing close tag",
            expected_status=CSMStatus.PENDING,  # Parser returns truncated; we stay conservative
            min_confidence=0.0,
            check_summary=False,
        ),
        ConformanceTest(
            name="Generic Adapter (Minimax)",
            provider="minimax",
            raw_output="Detailed output from a generic provider.",
            expected_status=CSMStatus.COMPLETED,
            min_confidence=0.6,
        ),
        ConformanceTest(
            name="Generic Adapter (Cliproxy)",
            provider="cliproxy",
            raw_output="Proxy provider response.",
            expected_status=CSMStatus.COMPLETED,
            min_confidence=0.6,
        ),
        ConformanceTest(
            name="XML cursor-agent",
            provider="cursor-agent",
            raw_output="<SUMMARY>Task done</SUMMARY><STATUS>completed</STATUS><PROGRESS>100</PROGRESS>",
            expected_status=CSMStatus.COMPLETED,
            min_confidence=0.9,
        ),
    ]


def run_conformance_suite(
    session_dir: Path | None = None,
    drift_window: int = 50,
) -> dict[str, Any]:
    """Run a suite of conformance tests against registered adapters.

    Args:
        session_dir: If provided, run drift detection on contract telemetry
            and include drift_issues in the report (drift alarm).
        drift_window: Window size for drift detection when session_dir is set.

    Returns:
        Report dict with total, passed, failed, results, and optionally drift_issues.
    """
    tests = _build_conformance_tests()
    results = []
    passed = 0
    for t in tests:
        res = normalize_output(t.provider, t.raw_output)
        issues = []
        if res.csm.status != t.expected_status:
            issues.append(f"Status mismatch: expected {t.expected_status}, got {res.csm.status}")
        if res.confidence < t.min_confidence:
            issues.append(f"Confidence too low: {res.confidence:.2f} < {t.min_confidence}")
        if t.check_summary and not res.csm.summary:
            issues.append("Missing summary")

        success = len(issues) == 0
        if success:
            passed += 1

        results.append(
            {
                "name": t.name,
                "provider": t.provider,
                "success": success,
                "issues": issues,
                "confidence": res.confidence,
            }
        )

    report: dict[str, Any] = {
        "total": len(tests),
        "passed": passed,
        "failed": len(tests) - passed,
        "results": results,
    }

    # Drift alarm (G-CA-03 C2): run ContractTelemetry.detect_drift + budget check when session_dir provided
    if session_dir is not None:
        from thegent.contracts.telemetry import ContractTelemetry

        ct = ContractTelemetry(session_dir)
        drift_issues = ct.detect_drift(window_size=drift_window)
        budget = ct.get_drift_budget_status(structural_budget_pct=5.0, semantic_budget_pct=10.0)
        if not budget["within_budget"]:
            drift_issues.append(
                f"Drift budget exceeded: structural {budget['structural_rate_pct']}% "
                f"(budget {budget['structural_budget_pct']}%), semantic {budget['semantic_rate_pct']}% "
                f"(budget {budget['semantic_budget_pct']}%)"
            )
        report["drift_issues"] = drift_issues
        report["drift_checked"] = True
        report["drift_budget"] = budget
    else:
        report["drift_issues"] = []
        report["drift_checked"] = False

    return report
