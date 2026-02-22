"""Tests for governance alert log parsing/summary helpers."""

from __future__ import annotations

from thegent.governance_alert_parser import (
    extract_fail_closed_signals,
    parse_last_alert_summary,
    render_markdown_summary,
)


def test_parse_last_alert_summary_extracts_structured_fields() -> None:
    log_text = """
noise
GOVERNANCE-GATES ALERT [warning]: regression-spiral-guard violations=1 policy_band=yellow escalation_stage=yellow_retry remediation_directive=remediate_yellow
"""
    summary = parse_last_alert_summary(log_text)
    assert summary.severity == "warning"
    assert summary.policy_band == "yellow"
    assert summary.escalation_stage == "yellow_retry"
    assert summary.remediation_directive == "remediate_yellow"
    assert "violations=1" in summary.reason


def test_extract_fail_closed_signals_filters_expected_lines() -> None:
    log_text = "\n".join(
        [
            "ok",
            "GOVERNANCE-GATES FAIL: [regression-spiral-guard]: policy_band=red pressure_score=0.9",
            "critical_interrupt",
            "fine",
        ]
    )
    lines = extract_fail_closed_signals(log_text, max_lines=10)
    assert len(lines) == 2
    assert "policy_band=red" in lines[0]
    assert "critical_interrupt" in lines[1]


def test_render_markdown_summary_includes_table_and_signals() -> None:
    log_text = """
GOVERNANCE-GATES ALERT [critical]: regression-spiral-guard policy_band=red pressure_score=0.9 policy_band=red escalation_stage=red_hard_interrupt remediation_directive=interrupt_red
GOVERNANCE-GATES FAIL: [regression-spiral-guard]: policy_band=red pressure_score=0.9
"""
    md = render_markdown_summary("Selector Strict", log_text, max_signal_lines=20)
    assert "### Selector Strict" in md
    assert "| policy_band | red |" in md
    assert "| escalation_stage | red_hard_interrupt |" in md
    assert "| remediation_directive | interrupt_red |" in md
    assert "Governance fail-closed signals detected." in md
    assert "GOVERNANCE-GATES FAIL" in md
