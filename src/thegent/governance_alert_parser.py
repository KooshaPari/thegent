"""Parsing helpers for governance selector alert/fail-closed CI summaries."""

from __future__ import annotations

from dataclasses import dataclass
import re

_ALERT_LINE_RE = re.compile(
    r"GOVERNANCE-GATES ALERT \[(?P<severity>[^\]]+)\]:"
    r"\s*(?P<reason>.*?)"
    r"(?:\s+policy_band=(?P<policy_band>\S+))?"
    r"(?:\s+escalation_stage=(?P<escalation_stage>\S+))?"
    r"(?:\s+remediation_directive=(?P<remediation_directive>\S+))?$"
)

_SIGNAL_RE = re.compile(r"fail-closed|GOVERNANCE-GATES FAIL|policy_band=red|critical_interrupt")


@dataclass(frozen=True)
class GovernanceAlertSummary:
    severity: str = "n/a"
    policy_band: str = "n/a"
    escalation_stage: str = "n/a"
    remediation_directive: str = "n/a"
    reason: str = "n/a"


def parse_last_alert_summary(log_text: str) -> GovernanceAlertSummary:
    """Return the last structured governance alert line from log text."""
    for line in reversed(log_text.splitlines()):
        match = _ALERT_LINE_RE.search(line.strip())
        if match is None:
            continue
        groups = match.groupdict()
        return GovernanceAlertSummary(
            severity=groups.get("severity") or "n/a",
            policy_band=groups.get("policy_band") or "n/a",
            escalation_stage=groups.get("escalation_stage") or "n/a",
            remediation_directive=groups.get("remediation_directive") or "n/a",
            reason=(groups.get("reason") or "").strip() or "n/a",
        )
    return GovernanceAlertSummary()


def extract_fail_closed_signals(log_text: str, max_lines: int = 40) -> list[str]:
    """Return up to max_lines lines that indicate fail-closed governance signals."""
    lines = [line for line in log_text.splitlines() if _SIGNAL_RE.search(line)]
    if max_lines <= 0:
        return []
    return lines[-max_lines:]


def render_markdown_summary(title: str, log_text: str, max_signal_lines: int = 40) -> str:
    """Render a markdown summary block suitable for GitHub Step Summary."""
    summary = parse_last_alert_summary(log_text)
    signal_lines = extract_fail_closed_signals(log_text, max_lines=max_signal_lines)

    out: list[str] = []
    out.append(f"### {title}")
    out.append("")
    out.append("| Field | Value |")
    out.append("|---|---|")
    out.append(f"| severity | {summary.severity} |")
    out.append(f"| policy_band | {summary.policy_band} |")
    out.append(f"| escalation_stage | {summary.escalation_stage} |")
    out.append(f"| remediation_directive | {summary.remediation_directive} |")
    out.append(f"| reason | {summary.reason} |")
    out.append("")

    if signal_lines:
        out.append("- Governance fail-closed signals detected.")
        out.append("")
        out.append("```text")
        out.extend(signal_lines)
        out.append("```")
    else:
        out.append("- No fail-closed governance signals detected.")

    out.append("")
    return "\n".join(out)
