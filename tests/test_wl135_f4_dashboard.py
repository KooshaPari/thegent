# @trace WL-135 B90-W3-F4
"""SLO dashboard report validation for WL-135."""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
REPORT = REPO_ROOT / "docs/reports/2026-02-21-B90-W3-F4-slo-dashboard.md"


def test_f4_report_exists():
    assert REPORT.exists(), f"Report not found: {REPORT}"


def test_f4_report_mentions_slo():
    text = REPORT.read_text()
    assert "SLO" in text or "slo" in text.lower(), "Report must mention 'SLO' or 'slo'"


def test_f4_report_mentions_loc():
    text = REPORT.read_text()
    assert "LOC" in text or "loc" in text.lower(), "Report must mention 'LOC' or 'loc'"
