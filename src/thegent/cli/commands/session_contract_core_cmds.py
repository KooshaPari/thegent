"""Thegent CLI session commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _coerce_issue_types,
    _default_owner_tag,
    _normalize_output_format,
    _safe_dict,
    _serialize_health_gate_md,
    _serialize_health_report_md,
    _serialize_health_trend_md,
    _write_health_gate_export,
    _write_health_trend_export,
    _write_report_export,
    console,
    EXIT_HEALTH_GATE_FAILED,
)
from thegent.cli.commands.session_cmds_helpers import (
    resolve_export_format_with_notice,
)


"""Session contract management commands.

Commands for viewing and managing session contracts.
Extracted from session_cmds.py to manage module size.
"""

def session_contracts_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> None:
    from thegent.cli.commands.impl import session_contract_audit_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    audit = session_contract_audit_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )
    rows = audit["rows"]
    summary = audit["summary"]
    if not rows and not summary_only:
        console.print("[dim]No sessions match contract audit criteria.[/dim]")
        if missing_only:
            console.print("[dim]No contract gaps detected.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        sys.stdout.write(json.dumps(audit).decode() + "\n")
        return
    if fmt == "md":
        if summary_only:
            console.print(f"summary: {json.dumps(summary).decode()}")
            return
        console.print("## Session Contract Audit")
        console.print(
            "| id | agent | owner | status | state | health | requested_model | requested_provider | "
            "resolved_alias | policy | issues |"
        )
        console.print(
            "|----|-------|-------|--------|-------|--------|----------------|-------------------|"
            "----------|--------|--------|"
        )
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            console.print(
                "| "
                f"{r['session_id']} | "
                f"{r['agent']} | "
                f"{r['owner']} | "
                f"{r['status']} | "
                f"{r['contract_state']} | "
                f"{r.get('contract_health', '—')} | "
                f"{r.get('requested_model', '—')} | "
                f"{r.get('requested_provider_hint', '—')} | "
                f"{r.get('resolved_model_alias', '—')} | "
                f"{r.get('policy', '—')} | "
                f"{issues or '—'} |"
            )
        console.print("")
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']} "
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")
    else:
        if summary_only:
            console.print(
                "summary: "
                f"complete={summary['complete']} partial={summary['partial']} "
                f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
                f"untracked={summary['untracked']} total={summary['total']} "
                f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
                f"error={summary['health']['error']} missing={summary['health']['missing']}"
            )
            return
        t = Table(title="Session Contract Audit")
        t.add_column("Session")
        t.add_column("Agent")
        t.add_column("Owner")
        t.add_column("Status")
        t.add_column("State")
        t.add_column("Health")
        t.add_column("Requested Model")
        t.add_column("Provider")
        t.add_column("Alias")
        t.add_column("Policy")
        t.add_column("Issues")
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            t.add_row(
                str(r["session_id"]),
                str(r["agent"]),
                str(r["owner"]),
                str(r["status"]),
                str(r["contract_state"]),
                str(r.get("contract_health", "—")),
                str(r.get("requested_model", "—")),
                str(r.get("requested_provider_hint", "—")),
                str(r.get("resolved_model_alias", "—")),
                str(r.get("policy", "—")),
                issues or "—",
            )
        console.print(t)
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']}"
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")



__all__ = [
    "session_contracts_cmd",
]
