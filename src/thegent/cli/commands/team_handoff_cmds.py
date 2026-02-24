"""Thegent CLI handoff and continuity commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys

import typer

from rich.table import Table
from rich.panel import Panel

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _normalize_output_format,
    console,
)


def handoff_cmd(owner: str) -> None:
    """Create a continuity snapshot for a shift handoff (WP-4006, WP-3008)."""
    settings = ThegentSettings()

    from thegent.cli.commands.observability_main_impl import escalate_list_impl  # pyright: ignore[reportMissingImports]
    from thegent.execution import HandoffManager, RunRegistry

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=50)
    run_ids = [r["run_id"] for r in runs if r.get("status") == "running"]
    failed = [r for r in runs if r.get("status") == "failed"]

    escalation_items = escalate_list_impl(past_sla_only=False, limit=50)
    escalation_run_ids = [e["run_id"] for e in escalation_items]
    past_sla = escalate_list_impl(past_sla_only=True, limit=50)

    next_steps: list[str] = []
    if past_sla:
        next_steps.append(f"Resolve {len(past_sla)} past-SLA escalation(s)")
    if failed:
        next_steps.append(f"Review {len(failed)} failed run(s)")
    if run_ids:
        next_steps.append(f"Monitor {len(run_ids)} active run(s)")

    hm = HandoffManager(settings.session_dir)

    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(settings.session_dir)
    queued_prompts = pq.list_pending()

    snapshot_id = hm.create_snapshot(owner, run_ids)

    msg = (
        f"Handoff snapshot [bold cyan]{snapshot_id}[/bold cyan] created for owner [bold]{owner}[/bold].\n"
        f"Transferred [green]{len(run_ids)}[/green] active runs."
    )
    if escalation_run_ids:
        msg += f"\nIncluded [yellow]{len(escalation_run_ids)}[/yellow] pending escalation(s)."
    if queued_prompts:
        msg += f"\nIncluded [blue]{len(queued_prompts)}[/blue] queued prompt(s)."
    if next_steps:
        msg += "\nNext steps: " + "; ".join(next_steps)
    console.print(Panel(msg, title="Shift Handoff", border_style="green"))


def handoff_show_cmd(snapshot_id: str, format: str | None = None) -> None:
    """Show full handoff summary (state, evidence, next steps) for a snapshot (WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    snap = hm.get_snapshot(snapshot_id)
    if not snap:
        console.print(f"[red]Snapshot {snapshot_id} not found.[/red]")
        raise typer.Exit(1)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(snap, indent=2) + "\n")
        return
    lines = [
        f"[bold]Handoff Snapshot:[/bold] {snapshot_id}",
        f"Owner: {snap.get('owner', '?')}",
        f"Timestamp: {snap.get('timestamp', '?')[:19]}",
        f"Active runs: {len(snap.get('run_ids', []))}",
    ]
    if snap.get("escalation_run_ids"):
        lines.append(f"Escalation backlog: {len(snap['escalation_run_ids'])}")
    if snap.get("queued_prompts"):
        lines.append(f"Queued prompts: {len(snap['queued_prompts'])}")
    state = snap.get("state_summary", {})
    if state:
        lines.append(f"State: running={state.get('running_count', 0)}, past_sla={state.get('past_sla_count', 0)}")
    steps = snap.get("next_steps", [])
    if steps:
        lines.append("Next steps: " + "; ".join(steps))
    evidence = snap.get("evidence_summary", [])
    if evidence:
        lines.append(f"Evidence: {len(evidence)} recent run(s)")
    console.print("\n".join(lines))


def handoff_list_cmd(limit: int = 10, format: str | None = None) -> None:
    """List pending handoff snapshots (WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    snapshots = hm.list_pending_snapshots(limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(snapshots).decode() + "\n")
        return
    if not snapshots:
        console.print("[dim]No pending handoffs.[/dim]")
        return
    table = Table(title="Pending Handoffs (WP-4006)")
    table.add_column("Snapshot ID")
    table.add_column("Owner")
    table.add_column("Timestamp")
    table.add_column("Runs")
    table.add_column("Escalations")
    for s in snapshots:
        table.add_row(
            s.get("snapshot_id", "?"),
            s.get("owner", "?"),
            (s.get("timestamp", "?")[:19]),
            str(len(s.get("run_ids", []))),
            str(len(s.get("escalation_run_ids", []))),
        )
    console.print(table)


def handoff_confirm_cmd(snapshot_id: str, incoming_owner: str, confidence: float = 1.0) -> None:
    """Incoming owner confirms handoff completeness (WP-3008, WP-4006)."""
    settings = ThegentSettings()
    from thegent.execution import HandoffManager

    hm = HandoffManager(settings.session_dir)
    ok = hm.confirm_handoff(snapshot_id=snapshot_id, incoming_owner=incoming_owner, confidence=confidence)
    if ok:
        console.print(f"[green]Handoff {snapshot_id} confirmed by {incoming_owner}[/green]")
    else:
        console.print(f"[red]Failed to confirm handoff {snapshot_id}[/red]")
        raise typer.Exit(1)


__all__ = [
    "handoff_cmd",
    "handoff_confirm_cmd",
    "handoff_list_cmd",
    "handoff_show_cmd",
]
