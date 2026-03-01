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
    from thegent_cli.cli.commands.dag_impl import _validate_task_id

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
    from thegent_cli.cli.commands.dag_impl import dag_status_impl

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
    if res.get("changed"):
        console.print("[green]Synced DAG status with sessions.[/green]")
        console.print("[dim]Auto-checkpoint created.[/dim]")
        run_next = res.get("run_next", {})
        if run_next and run_next.get("spawned"):
            for item in run_next["spawned"]:
                console.print(f"[green]{item['task_id']}[/green] -> {item['session_id']}")
    else:
        console.print("[dim]No status changes detected.[/dim]")


def dag_checkpoint_cmd(cd: Path | None = None, reason: str = "Manual checkpoint") -> None:
    """Create a point-in-time checkpoint of the DAG state."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)

    settings = ThegentSettings()
    from thegent_execution.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    content = dag_path.read_text(encoding="utf-8")
    owner = _default_owner_tag(cwd)

    ckpt = registry.create_checkpoint(reason=reason, dag_content=content, owner=owner)
    console.print(f"[green]Checkpoint created:[/green] {ckpt.checkpoint_id} ({reason})")


def dag_rollback_cmd(checkpoint_id: str | None = None, cd: Path | None = None) -> None:
    """Rollback DAG state to a specific checkpoint."""
    cid = _resolve_checkpoint_id(checkpoint_id)
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"

    settings = ThegentSettings()
    from thegent_execution.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpt = registry.get_checkpoint(cid)
    if not ckpt:
        console.print(f"[red]Checkpoint not found: {cid}[/red]")
        raise typer.Exit(1)

    content = ckpt.get("dag_content")
    if content is None:
        console.print("[red]Checkpoint has no content.[/red]")
        raise typer.Exit(1)

    _atomic_write(dag_path, content, backup=True)
    console.print(f"[green]DAG rolled back to checkpoint:[/green] {cid}")
    console.print(f"[dim]Reason: {ckpt.get('reason')}[/dim]")


def dag_checkpoints_cmd(limit: int = 20) -> None:
    """List recent DAG checkpoints."""
    settings = ThegentSettings()
    from thegent_execution.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    ckpts = registry.list_checkpoints(limit=limit)
    if not ckpts:
        console.print("[dim]No checkpoints found.[/dim]")
        return

    table = Table(title=f"DAG Checkpoints (last {limit})")
    table.add_column("Checkpoint ID", style="cyan")
    table.add_column("Created (UTC)", style="magenta")
    table.add_column("Owner", style="green")
    table.add_column("Reason", style="white")

    for c in ckpts:
        cid = c.get("checkpoint_id", "?")
        created = c.get("created_at_utc", "").split("T")[-1][:8]
        owner = c.get("owner", "?")
        reason_str = c.get("reason", "")
        table.add_row(cid, created, owner, reason_str)

    console.print(table)


def dag_recover_cmd(cd: Path | None = None, action: str = "retry-failed") -> None:
    """Perform recovery playbook actions on the DAG."""
    res = dag_recover_impl(cd=cd, action=action)
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(1)
    if res.get("changed"):
        msg = {
            "retry-failed": "[green]Reset all failed tasks to pending.[/green]",
            "clear-stuck": "[green]Reset all running tasks to pending.[/green]",
            "reset-retries": "[green]Reset all retry counters.[/green]",
            "fallback": "[green]Swapped failed tasks to fallback agents.[/green]",
        }.get(action, "[green]Recovery applied.[/green]")
        console.print(msg)
    else:
        console.print("[dim]No changes needed.[/dim]")


def dag_probe_cmd(cd: Path | None = None, baseline_id: str | None = None) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or dag_path is None or not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)
    assert dag_path is not None

    settings = ThegentSettings()
    from thegent_execution.execution import CheckpointRegistry

    registry = CheckpointRegistry(settings.session_dir)

    if not baseline_id:
        ckpts = registry.list_checkpoints(limit=1)
        if not ckpts:
            console.print("[yellow]No baseline checkpoint found. Use --baseline-id.[/yellow]")
            return
        baseline_id = ckpts[0]["checkpoint_id"]

    ckpt = registry.get_checkpoint(baseline_id or "")
    if not ckpt:
        console.print(f"[red]Baseline checkpoint not found: {baseline_id}[/red]")
        raise typer.Exit(1)

    baseline_content = ckpt["dag_content"]
    current_content = dag_path.read_text(encoding="utf-8")

    if baseline_content == current_content:
        console.print(f"[green]No drift detected against baseline {baseline_id}.[/green]")
    else:
        console.print(f"[yellow]Drift detected against baseline {baseline_id}:[/yellow]")
        import difflib

        diff = difflib.unified_diff(
            baseline_content.splitlines(keepends=True),
            current_content.splitlines(keepends=True),
            fromfile=f"baseline:{baseline_id}",
            tofile="current",
        )
        console.print("".join(diff))


__all__ = [
    "TERMINAL_STATUSES",
    "dag_update_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "dag_run_cmd",
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
]
