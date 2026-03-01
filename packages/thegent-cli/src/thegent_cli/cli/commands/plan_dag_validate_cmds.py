"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import logging
from pathlib import Path

import typer

from rich.table import Table

from thegent_cli.cli.commands.plan_output_helpers import (
    render_dag_list,
    render_dag_ready,
    render_dag_status,
    resolve_output_format,
)

from thegent_cli.cli.commands._cli_shared import (
    ThegentSettings,
    _atomic_write,
    _check_dag_cycles,
    _dag_path,
    _dag_update_task,
    _default_owner_tag,
    _ensure_contract_version_header,
    _ensure_dag_file,
    _parse_dag_full,
    _parse_dag_session,
    _parse_depends_on,
    _resolve_checkpoint_id,
    _resolve_cwd,
    _serialize_dag,
    _session_status_for,
    _validate_agent,
    _validate_dag,
    _validate_task_id,
    console,
    dag_ready_impl,
    dag_recover_impl,
    dag_run_impl,
    dag_sync_impl,
)

_log = logging.getLogger(__name__)



"""DAG-related CLI commands for plan/workflow management.

Commands for DAG validation, listing, updating, running, and synchronization.
Extracted from plan_cmds.py to manage module size.
"""

def dag_validate_cmd(cd: Path | None = None) -> None:
    """Validate DAG session from .factory/dag-session.md. Exit 2 on validation errors."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(2)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(2)
    doc = _parse_dag_full(dag_path)
    errors = _validate_dag(doc)
    if errors:
        for e in errors:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(2)

    # WP-4005: State freshness check
    settings = ThegentSettings()
    from thegent_execution.execution import CheckpointRegistry

    ckpt_registry = CheckpointRegistry(settings.session_dir)
    ckpts = ckpt_registry.list_checkpoints(limit=1)
    if ckpts:
        last_ckpt = ckpts[0]
        # In a real impl, we'd compare content hashes
        # For now, just a timestamp warning
        from datetime import UTC, datetime

        ckpt_ts = datetime.fromisoformat(last_ckpt["created_at_utc"])
        file_ts = datetime.fromtimestamp(dag_path.stat().st_mtime, UTC)
        if file_ts > ckpt_ts:
            console.print(
                f"[yellow]Warning: DAG file has been modified since last checkpoint ({last_ckpt['checkpoint_id']}).[/yellow]"
            )

    console.print("[green]DAG valid.[/green]")


def dag_list_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Parse and display DAG session from .factory/dag-session.md."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    _frontmatter, tasks = _parse_dag_session(dag_path)
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)
    render_dag_list(tasks, fmt, console=console)


def dag_add_cmd(
    task_id: str,
    agent: str,
    prompt: str,
    cd: Path | None = None,
    depends_on: str | None = None,
    contract_version: str | None = None,
) -> None:
    """Add a task to the DAG. XA4: contract_version in task metadata."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    assert dag_path is not None
    tid = task_id.strip()
    if err := _validate_task_id(tid):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    if err := _validate_agent((agent or "").strip()):
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2)
    if not (prompt or "").strip():
        console.print("[red]Prompt cannot be empty.[/red]")
        raise typer.Exit(2)
    dag_path.parent.mkdir(parents=True, exist_ok=True)
    doc = _ensure_dag_file(dag_path)
    existing_ids = {(t.get("id") or "").strip() for t in doc.tasks}
    if tid in existing_ids:
        console.print(f"[red]Task {tid} already exists.[/red]")
        raise typer.Exit(1)
    deps_str = (depends_on or "").strip() or "—"
    deps_list = _parse_depends_on(deps_str)
    for d in deps_list:
        if d not in existing_ids:
            console.print(f"[red]depends_on '{d}' does not exist in DAG.[/red]")
            raise typer.Exit(2)
    row: dict[str, str] = {
        "id": tid,
        "agent": (agent or "").strip(),
        "prompt": (prompt or "").strip(),
        "depends_on": deps_str,
        "status": "pending",
    }
    if contract_version and (cv := contract_version.strip()):
        row["contract_version"] = cv
        _ensure_contract_version_header(doc)
    doc.tasks.append(row)
    cycle_errors = _check_dag_cycles(doc.tasks)
    if cycle_errors:
        for e in cycle_errors:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(2)
    _atomic_write(dag_path, _serialize_dag(doc))
    console.print(f"[green]Added task {tid}[/green]")


def dag_remove_cmd(task_id: str, cd: Path | None = None) -> None:
    """Remove a task from the DAG."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    assert dag_path is not None
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    tid = task_id.strip()
    before = len(doc.tasks)
    doc.tasks = [t for t in doc.tasks if (t.get("id") or "").strip() != tid]
    if len(doc.tasks) == before:
        console.print(f"[red]Task {task_id} not found.[/red]")
        raise typer.Exit(1)
    _atomic_write(dag_path, _serialize_dag(doc))
    console.print(f"[green]Removed task {task_id}[/green]")


def dag_cancel_cmd(task_id: str, cd: Path | None = None) -> None:
    """Cancel a task (set status to cancelled)."""
    dag_update_cmd(task_id=task_id, cd=cd, status="cancelled")
    console.print(f"[green]Cancelled task {task_id}[/green]")


def dag_status_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """For each task with session_id show id, status, session_id, session_status (running/exited:rc)."""
    from thegent_cli.cli.commands.dag_impl import dag_status_impl

    res = dag_status_impl(cd=cd)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    rows = res.get("tasks", [])
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)
    render_dag_status(rows, fmt, console=console)


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



__all__ = [
    "dag_validate_cmd",
    "dag_list_cmd",
    "dag_add_cmd",
    "dag_remove_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_update_cmd",
]
