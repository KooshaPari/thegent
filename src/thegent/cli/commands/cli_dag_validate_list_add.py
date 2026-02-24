"""DAG CLI validate, list, add, remove commands (WL-120).

Basic DAG manipulation: validation, listing, adding/removing tasks.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from rich.console import Console
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.cli.commands.dag_impl import (
    _check_dag_cycles,
    _dag_path,
    _ensure_dag_file,
    _parse_dag_full,
    _parse_dag_session,
    _parse_depends_on,
    _serialize_dag,
    _atomic_write,
    _validate_agent,
    _validate_dag,
    _validate_task_id,
    _ensure_contract_version_header,
)
from thegent.cli.services.run_session_helpers import resolve_cwd as _resolve_cwd
import orjson as json

console = Console()


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
    from thegent.execution import CheckpointRegistry

    ckpt_registry = CheckpointRegistry(settings.session_dir)
    ckpts = ckpt_registry.list_checkpoints(limit=1)
    if ckpts:
        last_ckpt = ckpts[0]
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
    fmt = (format or settings.output_format or "rich").lower()
    if not tasks:
        if fmt == "json":
            sys.stdout.write(json.dumps({"tasks": []}).decode() + "\n")
        else:
            console.print("[dim]No tasks in DAG.[/dim]")
        return
    if fmt == "json":
        sys.stdout.write(json.dumps({"tasks": tasks}).decode() + "\n")
        return
    if fmt == "md":
        console.print("## DAG Session\n")
        console.print("| id | agent | prompt | depends_on | status |")
        console.print("|----|-------|--------|------------|--------|")
        for t in tasks:
            console.print(
                f"| {t.get('id', '—')} | {t.get('agent', '—')} | {t.get('prompt', '—')} | {t.get('depends_on', '—')} | {t.get('status', '—')} |"
            )
    else:
        tbl = Table(title="DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        tbl.add_column("depends_on")
        tbl.add_column("status")
        for t in tasks:
            tbl.add_row(
                t.get("id", "—"),
                t.get("agent", "—"),
                t.get("prompt", "—"),
                t.get("depends_on", "—"),
                t.get("status", "—"),
            )
        console.print(tbl)


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


__all__ = [
    "dag_validate_cmd",
    "dag_list_cmd",
    "dag_add_cmd",
    "dag_remove_cmd",
]
