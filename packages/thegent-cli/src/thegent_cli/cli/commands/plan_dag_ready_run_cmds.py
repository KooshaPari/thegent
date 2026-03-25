"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import logging
from pathlib import Path

import typer


from thegent_cli.cli.commands.plan_output_helpers import (
    render_dag_ready,
    resolve_output_format,
)

from thegent_cli.cli.commands._cli_shared import (
    ThegentSettings,
    _atomic_write,
    _parse_dag_full,
    _resolve_cwd,
    _serialize_dag,
    _session_status_for,
    console,
    dag_ready_impl,
)

_log = logging.getLogger(__name__)


"""DAG-related CLI commands for plan/workflow management.

Commands for DAG validation, listing, updating, running, and synchronization.
Extracted from plan_cmds.py to manage module size.
"""


def dag_ready_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """List task ids that are ready (pending with all deps done|cancelled|skipped)."""
    res = dag_ready_impl(cd)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if res.get("remediation"):
            console.print(f"[dim]{res['remediation']}[/dim]")
        raise typer.Exit(1)
    ready_ids = res["ready_task_ids"]
    tasks = res.get("tasks", [])
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)
    render_dag_ready(ready_ids, tasks, fmt, console=console)


def dag_reconcile_cmd(cd: Path | None = None) -> None:
    """Reconcile DAG state with reality (clean up stuck 'running' tasks)."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    changed = False
    reconciled_count = 0

    for t in doc.tasks:
        if t.get("status", "").lower() != "running":
            continue

        sids = [s.strip() for s in (t.get("session_id") or "").split(",") if s.strip()]
        if not sids:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1
            continue

        any_alive = False
        for sid in sids:
            try:
                status = _session_status_for(sid, settings)
                if status == "running":
                    any_alive = True
                    break
            except Exception as exc:
                _log.debug("Failed to resolve session status for %s: %s", sid, exc)

        if not any_alive:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))
        console.print(f"[green]Reconciled {reconciled_count} stuck tasks.[/green]")
    else:
        console.print("[dim]DAG is in sync with live processes.[/dim]")


__all__ = [
    "dag_ready_cmd",
    "dag_reconcile_cmd",
]
