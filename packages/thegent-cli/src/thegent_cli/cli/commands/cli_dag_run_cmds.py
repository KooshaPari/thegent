"""DAG CLI run, sync, recover, checkpoint commands (WL-120).

Advanced DAG operations: execution, synchronization, recovery, checkpointing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from rich.console import Console
from rich.table import Table

from thegent_core.config import ThegentSettings
from thegent_cli.cli.commands.dag_impl import (
    _atomic_write,
    _check_dag_cycles,
    _dag_path,
    _dag_update_task,
    _ensure_dag_file,
    _parse_dag_full,
    _parse_depends_on,
    _serialize_dag,
    _session_status_for,
    _validate_agent,
    dag_ready_impl,
    dag_recover_impl,
    dag_run_impl,
    dag_sync_impl,
)
from thegent_cli.cli.commands._cli_shared import _resolve_checkpoint_id
from thegent_cli.cli.services.run_session_helpers import (
    default_owner_tag as _default_owner_tag,
    resolve_cwd as _resolve_cwd,
)
import orjson as json

console = Console()

TERMINAL_STATUSES = frozenset({"done", "cancelled", "skipped"})


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
                console.print(f"[yellow]Could not resolve session status for '{sid}': {exc}[/yellow]")
                continue

        if not any_alive:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))
        console.print(f"[green]Reconciled {reconciled_count} stuck tasks.[/green]")
    else:
        console.print("[dim]DAG is in sync with live processes.[/dim]")


def dag_run_cmd(
    cd: Path | None = None,
    dry_run: bool = False,
    task: str | None = None,
    max_parallel: int | None = None,
    lane: str | None = None,
    check_drift: bool = False,
    contract_version: str | None = None,
) -> None:
    """Spawn thegent bg for each ready task; update status=running and session_id."""
    res = dag_run_impl(
        cd=cd,
        dry_run=dry_run,
        task=task,
        max_parallel=max_parallel,
        lane=lane,
        check_drift=check_drift,
        contract_version=contract_version,
    )
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if res.get("drift_issues"):
            for issue in res["drift_issues"]:
                console.print(f"  [dim]{issue}[/dim]")
            console.print("[dim]Resolve with: thegent govern conformance --check-drift[/dim]")
        raise typer.Exit(2 if res.get("error") == "Drift detected" else 1)
    if res.get("dry_run"):
        for item in res.get("would_run", []):
            console.print(
                f"[dim]Would run: {item['task_id']} agent={item['agent']} prompt={item['prompt_preview']}[/dim]"
            )
        return
    if res.get("message"):
        console.print(f"[dim]{res['message']}[/dim]")
    for item in res.get("spawned", []):
        console.print(f"[green]{item['task_id']}[/green] -> {item['session_id']}")
    for err in res.get("errors", []):
        console.print(f"[red]{err['task_id']}: {err['error']}[/red]")


def dag_sync_cmd(cd: Path | None = None, auto_run_next: bool = False) -> None:
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc."""
    res = dag_sync_impl(cd=cd, auto_run_next=auto_run_next)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)


__all__ = [
    "dag_reconcile_cmd",
    "dag_run_cmd",
]
