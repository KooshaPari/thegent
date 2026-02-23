<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> main
"""Thegent CLI governance escalation and HITL approval commands.

Extracted from governance_cmds.py as part of CLI refactoring (WL-124).
"""
<<<<<<< HEAD
=======
"""Governance escalation and HITL approval handling commands (WL-124).
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main

from __future__ import annotations

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> main
import sys
from typing import Any

import orjson as json
import typer
<<<<<<< HEAD
=======
import json
import sys

import typer

from rich.panel import Panel
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    _normalize_output_format,
    _resolve_run_id,
    console,
)


def escalate_add_cmd(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> None:
    """Add a blocked run to the escalation queue (WP-3008)."""
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> main
    from thegent.cli.commands.observability_main_impl import escalate_add_impl

    escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        lane=lane,
        priority=priority,
    )
<<<<<<< HEAD
=======
    from thegent.cli.commands.impl import escalate_add_impl

    payload = {
        "run_id": run_id,
        "reason": reason,
        "sla_minutes": sla_minutes,
        "owner": owner,
        "lane": lane,
    }
    if priority:
        payload["priority"] = priority
    escalate_add_impl(**payload)
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main
    console.print(
        f"[green]Added run_id={run_id} to escalation queue (SLA: {sla_minutes} min, priority: {priority})[/green]"
    )


def escalate_list_cmd(
    past_sla_only: bool = False,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List governance escalation queue (WP-3008)."""
<<<<<<< HEAD
<<<<<<< HEAD
    from thegent.cli.commands.observability_main_impl import escalate_list_impl
=======
    from thegent.cli.commands.impl import escalate_list_impl
>>>>>>> fix/ci-remove-macos
=======
    from thegent.cli.commands.observability_main_impl import escalate_list_impl
>>>>>>> main

    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
<<<<<<< HEAD
<<<<<<< HEAD
        sys.stdout.write(json.dumps(items).decode().decode() + "\n")
=======
        sys.stdout.write(json.dumps(items) + "\n")
>>>>>>> fix/ci-remove-macos
=======
        sys.stdout.write(json.dumps(items).decode().decode() + "\n")
>>>>>>> main
        return
    if not items:
        console.print("[dim]No escalation items.[/dim]")
        return
    table = Table(title="Escalation Queue (WP-3008)")
    table.add_column("Run ID")
    table.add_column("Reason")
    table.add_column("Owner")
    table.add_column("Lane")
    table.add_column("Prio")
    table.add_column("Blocked At")
    table.add_column("SLA By")
    table.add_column("Past SLA")
    for it in items:
        past = "[red]YES[/red]" if it.get("past_sla") else "[green]No[/green]"
        table.add_row(
            it.get("run_id", "?"),
            it.get("reason", "?"),
            it.get("owner") or "-",
            it.get("lane", "standard"),
            str(it.get("priority", 0)),
            it.get("blocked_at_utc", "?")[:19],
            it.get("escalate_by_utc", "?")[:19],
            past,
        )
    console.print(table)


<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> main
def escalate_resolve_cmd(run_id: str | None = None, resolution: str = "resolved") -> None:
    """Mark an escalation item as resolved (WP-3008)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli.commands.observability_main_impl import escalate_resolve_impl
<<<<<<< HEAD
=======
def sweep_cmd(
    drift_window: int = 50,
    include_audit: bool = False,
    format: str | None = None,
) -> None:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    from thegent.cli.commands.impl import sweep_impl

    result = sweep_impl(
        drift_window=drift_window,
        include_audit=include_audit,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        # Strip non-JSON-serializable if any
        out = {k: v for k, v in result.items() if k != "audit" or v is not None}
        if result.get("audit"):
            out["audit"] = result["audit"]
        sys.stdout.write(json.dumps(out) + "\n")
        if not result["pass"]:
            raise typer.Exit(1)
        return

    if result["pass"]:
        console.print("[green]Sweep passed: no drift, no past-SLA escalations.[/green]")
        return

    parts = []
    if result["drift_issues"]:
        for i in result["drift_issues"]:
            parts.append(f"[red]![/red] {i}")
    if result["past_sla_count"] > 0:
        parts.append(
            f"[yellow]Past SLA:[/yellow] {result['past_sla_count']} escalation(s). Run `thegent govern escalate list --past-sla`"
        )
    if result.get("audit") and result["audit"].get("status") not in ("passed", "empty"):
        parts.append(f"[red]Audit:[/red] {result['audit'].get('status', 'failed')}")
    if parts:
        console.print(Panel("\n".join(parts), title="Policy Drift Sweep (WP-3005)", border_style="red"))
    raise typer.Exit(1)


def escalate_resolve_cmd(run_id: str | None = None, resolution: str = "resolved") -> None:
    """Mark an escalation item as resolved (WP-3008)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli.commands.impl import escalate_resolve_impl
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main

    ok = escalate_resolve_impl(run_id=rid, resolution=resolution)
    if ok:
        console.print(f"[green]Escalation {rid} resolved as '{resolution}'.[/green]")
    else:
<<<<<<< HEAD
<<<<<<< HEAD
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")
=======
        console.print(f"[red]Escalation {rid} has no pending item.[/red]")
>>>>>>> fix/ci-remove-macos
=======
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")
>>>>>>> main


def escalate_approve_cmd(run_id: str | None = None) -> None:
    """Approve an escalation, recording an override for the owner (G-GP-05)."""
    rid = _resolve_run_id(run_id)
<<<<<<< HEAD
<<<<<<< HEAD
    from thegent.cli.commands.observability_main_impl import escalate_approve_impl
=======
    from thegent.cli.commands.impl import escalate_approve_impl
>>>>>>> fix/ci-remove-macos
=======
    from thegent.cli.commands.observability_main_impl import escalate_approve_impl
>>>>>>> main

    ok = escalate_approve_impl(run_id=rid)
    if ok:
        console.print(f"[green]Escalation {rid} APPROVED. Policy override recorded for owner.[/green]")
    else:
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")


def govern_approve_cmd(run_id: str, reason: str | None = None) -> None:
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> main
    """Approve a HITL-blocked run, updating governance_events.jsonl to 'approved'."""
    from thegent.cli.commands.observability_main_impl import govern_approve_impl

    result = govern_approve_impl(run_id=run_id, reason=reason)
    console.print(f"[green]Run {run_id} approved.[/green]")
    if result and result.get("approved"):
        console.print(f"[dim]Event recorded at {result.get('timestamp_utc', 'unknown')}[/dim]")


def govern_reject_cmd(run_id: str, reason: str | None = None) -> None:
    """Reject a HITL-blocked run, updating governance_events.jsonl to 'rejected'."""
    from thegent.cli.commands.observability_main_impl import govern_reject_impl

    result = govern_reject_impl(run_id=run_id, reason=reason)
    console.print(f"[red]Run {run_id} rejected.[/red]")
    if result and result.get("rejected"):
        console.print(f"[dim]Event recorded at {result.get('timestamp_utc', 'unknown')}[/dim]")


def govern_list_pending_cmd() -> None:
    """List all pending HITL approval events from governance_events.jsonl."""
    from thegent.cli.commands.observability_main_impl import govern_list_pending_impl

    items = govern_list_pending_impl()
    if not items:
        console.print("[dim]No pending HITL approvals.[/dim]")
        return
    table = Table(title="Pending HITL Approvals")
    table.add_column("Run ID")
    table.add_column("Status")
    table.add_column("Timestamp")
    for it in items:
        table.add_row(
            it.get("run_id", "?"),
            it.get("status", "unknown"),
            it.get("timestamp_utc", "?")[:19],
<<<<<<< HEAD
=======
    """WL-019-B: Approve a HITL-blocked run (G-GP-05).

    Reads pending approvals from governance_events.jsonl, updates status to
    'approved', and triggers continuation of the blocked run.
    """
    from thegent.cli.commands.impl import govern_approve_impl
    from thegent.cli.services.governance import govern_get_pending_approval_impl
    from thegent.governance.diff_renderer import DiffPayload, DiffRenderer

    pending = govern_get_pending_approval_impl(run_id=run_id)
    unified_diff = str(pending.get("unified_diff") or "")
    if unified_diff:
        payload = DiffPayload(before="", after="", unified_diff=unified_diff)
        console.print("[bold cyan]Review Diff:[/bold cyan]")
        console.print(f"[dim]{DiffRenderer.render_summary(payload)}[/dim]")
        console.print(DiffRenderer.render_ansi(payload))
    else:
        console.print("[dim]No unified diff available for this approval request.[/dim]")
    if reason is None:
        reason = typer.prompt("Approval reason", default="approved")
    result = govern_approve_impl(run_id=run_id, reason=reason)
    console.print(
        f"[green]HITL run_id={result['run_id']} APPROVED[/green]" + (f" (reason: {reason})" if reason else "")
    )


def govern_reject_cmd(run_id: str, reason: str | None = None) -> None:
    """WL-019-B: Reject a HITL-blocked run (G-GP-05).

    Reads pending approvals from governance_events.jsonl, updates status to
    'rejected', and cancels the blocked run.
    """
    from thegent.cli.commands.impl import govern_reject_impl

    result = govern_reject_impl(run_id=run_id, reason=reason)
    console.print(
        f"[yellow]HITL run_id={result['run_id']} REJECTED[/yellow]" + (f" (reason: {reason})" if reason else "")
    )


def govern_list_pending_cmd(format: str | None = None) -> None:
    """WL-019-B: List all pending HITL approval requests (G-GP-05)."""
    from thegent.cli.commands.impl import govern_list_pending_impl
    from thegent.governance.diff_renderer import DiffPayload, DiffRenderer

    items = govern_list_pending_impl()
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items) + "\n")
        return
    if not items:
        console.print("[dim]No pending HITL approval requests.[/dim]")
        return
    table = Table(title="Pending HITL Approvals (G-GP-05 / WL-019)")
    table.add_column("Run ID")
    table.add_column("Policy")
    table.add_column("Reason")
    table.add_column("Agent")
    table.add_column("Lane")
    table.add_column("Owner")
    table.add_column("Emitted At")
    table.add_column("Diff")
    for it in items:
        unified_diff = str(it.get("unified_diff") or "")
        diff_summary = "none"
        if unified_diff:
            diff_summary = DiffRenderer.render_summary(DiffPayload(before="", after="", unified_diff=unified_diff))
        table.add_row(
            it.get("run_id", "?"),
            it.get("policy", "?"),
            it.get("reason", "?"),
            it.get("agent", "-"),
            it.get("lane", "standard"),
            it.get("owner", "-"),
            (it.get("emitted_at_utc") or "?")[:19],
            diff_summary,
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main
        )
    console.print(table)


__all__ = [
    "escalate_add_cmd",
    "escalate_approve_cmd",
    "escalate_list_cmd",
    "escalate_resolve_cmd",
    "govern_approve_cmd",
    "govern_list_pending_cmd",
    "govern_reject_cmd",
<<<<<<< HEAD
<<<<<<< HEAD
=======
    "sweep_cmd",
>>>>>>> fix/ci-remove-macos
=======
>>>>>>> main
]
