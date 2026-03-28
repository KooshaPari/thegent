"""DAG CLI run, sync, recover, checkpoint commands (WL-120).

Advanced DAG operations: execution, synchronization, recovery, checkpointing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from rich.console import Console
from rich.table import Table

from phenotype_thegent_core.config import ThegentSettings
from phenotype_thegent_cli.cli.commands.dag_impl import (
    _atomic_write,
    _check_dag_cycles,
    _dag_update_task,
    _parse_dag_full,
    _parse_depends_on,
    _serialize_dag,
    _validate_agent,
    dag_ready_impl,
)
from phenotype_thegent_cli.cli.services.run_session_helpers import (
    resolve_cwd as _resolve_cwd,
)
import orjson as json

console = Console()

TERMINAL_STATUSES = frozenset({"done", "cancelled", "skipped"})


def dag_update_cmd(
    task_id: str,
    cd: Path | None = None,
    status: str | None = None,
    session_id: str | None = None,
    prompt: str | None = None,
    agent: str | None = None,
    depends_on: str | None = None,
    contract_version: str | None = None,
) -> None:
    """Update a task in the DAG. XA4: contract_version in task metadata."""

    VALID_STATUSES = {"pending", "running", "done", "failed", "blocked", "cancelled", "skipped"}
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    tid = task_id.strip()
    if not any((t.get("id") or "").strip() == tid for t in doc.tasks):
        console.print(f"[red]Task not found: {tid}[/red]")
        raise typer.Exit(1)
    if status is not None and status.strip().lower() not in VALID_STATUSES:
        console.print(f"[red]Invalid status '{status}'; must be one of: {', '.join(sorted(VALID_STATUSES))}[/red]")
        raise typer.Exit(2)
    if agent is not None and (err := _validate_agent(agent.strip())):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    norm_depends_on: str | None = None
    if depends_on is not None:
        existing_ids = {(t.get("id") or "").strip() for t in doc.tasks}
        deps_list = _parse_depends_on(depends_on.strip())
        for d in deps_list:
            if d not in existing_ids:
                console.print(f"[red]depends_on '{d}' does not exist in DAG.[/red]")
                raise typer.Exit(2)
        norm_depends_on = ",".join(deps_list) if deps_list else "—"
    if not _dag_update_task(
        doc,
        task_id,
        status=status,
        session_id=session_id,
        prompt=prompt,
        agent=agent.strip() if agent else None,
        depends_on=norm_depends_on,
        contract_version=contract_version.strip() if contract_version else None,
    ):
        raise typer.Exit(1)
    if status is not None or depends_on is not None or agent is not None:
        cycle_errors = _check_dag_cycles(doc.tasks)
        if cycle_errors:
            for e in cycle_errors:
                console.print(f"[red]{e}[/red]")
            raise typer.Exit(2)
    content = _serialize_dag(doc)
    _atomic_write(dag_path, content)


def dag_cancel_cmd(task_id: str, cd: Path | None = None) -> None:
    """Cancel a task (set status to cancelled)."""
    dag_update_cmd(task_id=task_id, cd=cd, status="cancelled")
    console.print(f"[green]Cancelled task {task_id}[/green]")


def dag_status_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """For each task with session_id show id, status, session_id, session_status (running/exited:rc)."""
    from phenotype_thegent_cli.cli.commands.dag_impl import dag_status_impl

    res = dag_status_impl(cd=cd)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    rows = res.get("tasks", [])
    settings = ThegentSettings()
    fmt = (format or settings.output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": rows}).decode() + "\n")
        return
    if not rows:
        console.print("[dim]No tasks with session_id.[/dim]")
        return
    if fmt == "md":
        console.print("| id | status | session_id | session_status |")
        console.print("|----|--------|------------|----------------|")
        for r in rows:
            console.print(f"| {r['id']} | {r['status']} | {r['session_id']} | {r['session_status']} |")
    else:
        tbl = Table(title="DAG Status (tasks with session_id)")
        tbl.add_column("id")
        tbl.add_column("status")
        tbl.add_column("session_id")
        tbl.add_column("session_status")
        for r in rows:
            tbl.add_row(r["id"], r["status"], r["session_id"], r["session_status"])
        console.print(tbl)


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
    fmt = (format or settings.output_format or "rich").lower()
    if not ready_ids:
        console.print("[dim]No ready tasks.[/dim]")
        return
    if fmt == "ids":
        console.print("\n".join(ready_ids))
    elif fmt == "json":
        sys.stdout.write(json.dumps({"ready_task_ids": ready_ids}).decode() + "\n")
        return
    elif fmt == "md":
        console.print("| id | agent | prompt |")
        console.print("|----|-------|--------|")
        for t in tasks:
            tid = t.get("id", "")
            prompt = t.get("prompt", "")
            prompt_preview = (prompt[:60] + "...") if len(prompt) > 60 else prompt
            console.print(f"| {tid} | {t.get('agent', '—')} | {prompt_preview} |")
    else:
        tbl = Table(title="Ready DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        for t in tasks:
            tid = t.get("id", "")
            prompt = t.get("prompt", "")
            preview = (prompt[:60] + "...") if len(prompt) > 60 else (prompt or "—")
            tbl.add_row(tid, t.get("agent", "—"), preview)
        console.print(tbl)


__all__ = [
    "dag_update_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_ready_cmd",
]
