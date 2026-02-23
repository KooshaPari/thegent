"""Thegent CLI governance escalation and HITL approval commands.

Extracted from governance_cmds.py as part of CLI refactoring (WL-124).
"""

from __future__ import annotations

import sys
from typing import Any

import orjson as json
import typer
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
    from thegent.cli.commands.observability_main_impl import escalate_add_impl

    escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        lane=lane,
        priority=priority,
    )
    console.print(
        f"[green]Added run_id={run_id} to escalation queue (SLA: {sla_minutes} min, priority: {priority})[/green]"
    )


def escalate_list_cmd(
    past_sla_only: bool = False,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List governance escalation queue (WP-3008)."""
    from thegent.cli.commands.observability_main_impl import escalate_list_impl

    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items).decode().decode() + "\n")
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


def escalate_resolve_cmd(run_id: str | None = None, resolution: str = "resolved") -> None:
    """Mark an escalation item as resolved (WP-3008)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli.commands.observability_main_impl import escalate_resolve_impl

    ok = escalate_resolve_impl(run_id=rid, resolution=resolution)
    if ok:
        console.print(f"[green]Escalation {rid} resolved as '{resolution}'.[/green]")
    else:
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")


def escalate_approve_cmd(run_id: str | None = None) -> None:
    """Approve an escalation, recording an override for the owner (G-GP-05)."""
    rid = _resolve_run_id(run_id)
    from thegent.cli.commands.observability_main_impl import escalate_approve_impl

    ok = escalate_approve_impl(run_id=rid)
    if ok:
        console.print(f"[green]Escalation {rid} APPROVED. Policy override recorded for owner.[/green]")
    else:
        console.print(f"[red]Escalation {rid} not found or already resolved.[/red]")


def govern_approve_cmd(run_id: str, reason: str | None = None) -> None:
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
]
