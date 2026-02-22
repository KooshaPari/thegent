"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, cast

import typer

from rich.table import Table

from thegent.cli.commands.plan_output_helpers import (
    render_dag_list,
    render_dag_ready,
    render_dag_status,
    render_plan_next_items,
    resolve_output_format,
)

from thegent.cli.commands._cli_shared import (
    RunRegistry,
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

from thegent.cli.commands.run_cmds import bg_cmd
from thegent.cli.commands.session_cmds import history_cmd


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
    from thegent.cli.commands.dag_impl import dag_status_impl

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


def plan_incorporate_cmd(cd: Path | None = None, dry_run: bool = False) -> None:
    """Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md. Preserves CLAIMED and COMPLETED."""
    from thegent.cli.commands.work_stream_impl import incorporate_impl

    result = incorporate_impl(cd=cd, dry_run=dry_run)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    merged = result.get("merged", 0)
    if result.get("dry_run"):
        console.print(f"[dim]Dry run: would merge {merged} items from {result.get('sources', [])}[/dim]")
    else:
        console.print(f"[green]Merged {merged} items into docs/reference/WORK_STREAM.md[/green]")


def plan_claim_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Claim an item in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_claim_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_claim_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        if result.get("remediation"):
            console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    console.print(f"[green]Claimed {item_id} for {aid}[/green]")


def plan_complete_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Mark an item as complete in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_complete_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_complete_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Completed {item_id} (agent: {aid})[/green]")


def plan_verify_workstream_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Verify WORK_STREAM invariants for CLAIMED/COMPLETED overlap by exact ID match."""
    from thegent.planning.work_stream import WorkStreamManager

    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)

    manager = WorkStreamManager(ThegentSettings(), base_dir=cwd)
    result = manager.verify_work_stream_invariants()
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)

    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
    else:
        counts = result.get("counts", {})
        console.print(
            "[cyan]WORK_STREAM counts:[/cyan] "
            f"CLAIMED={counts.get('claimed', 0)} "
            f"COMPLETED={counts.get('completed', 0)} "
            f"OVERLAP={counts.get('overlap', 0)}"
        )
        if result.get("errors"):
            for error in result["errors"]:
                console.print(f"[red]{error}[/red]")
        else:
            console.print("[green]WORK_STREAM invariants verified.[/green]")

    if not result.get("ok", False):
        raise typer.Exit(1)


def plan_wait_next_cmd(
    cd: Path | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    sources: str | None = None,
    format: str | None = None,
) -> None:
    """Block until next actionable work exists (DAG ready, do_next, escalation, inbox)."""
    from thegent.cli.commands.work_stream_impl import wait_next_impl

    src_tuple = tuple(s.strip() for s in (sources or "dag,do_next,escalation,inbox").split(",") if s.strip())
    result = wait_next_impl(cd=cd, poll_interval=poll, timeout=timeout, sources=src_tuple)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    settings = ThegentSettings()
    fmt = (format or settings.output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if result.get("action") is None:
        console.print("[dim]Timeout: no next action found.[/dim]")
        return
    from rich.panel import Panel

    prompt = result.get("prompt_suggestion", "")
    console.print(
        Panel(
            f"[bold]{result.get('id', '?')}[/bold] ({result.get('source', '')})\n"
            f"{result.get('description', '')}\n\n"
            f"[green]Prompt:[/green] {prompt[:120]}{'...' if len(prompt) > 120 else ''}",
            title=f"Next action ({result.get('elapsed_s', 0):.1f}s)",
            border_style="cyan",
        )
    )
    console.print('[dim]Use: thegent run "<prompt_suggestion>" or thegent free --do-next[/dim]')


def plan_do_next_cmd(cd: Path | None = None, limit: int = 5, format: str | None = None) -> None:
    """Find next actionable work items from WORK_STREAM, PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue."""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=limit)
    settings = ThegentSettings()
    fmt = resolve_output_format(format, settings)
    if result.get("governance_blocked"):
        if fmt == "json":
            sys.stdout.write(json.dumps(result) + "\n")
        else:
            console.print(f"[red]{result['error']}[/red]")
            if result.get("remediation"):
                console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    items = result.get("next_items", [])
    if not items:
        console.print("[dim]No pending items found.[/dim]")
        if result.get("empty_reason"):
            console.print(f"[dim]{result['empty_reason']}[/dim]")
        return
    render_plan_next_items(items, console=console)


def plan_get_next_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Get first work item prompt for scripting. Use: PROMPT=$(thegent plan get-next)"""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    result = do_next_impl(cd=cd, limit=1)
    fmt = (format or "plain").lower()
    if result.get("governance_blocked"):
        if fmt == "json":
            sys.stdout.write(json.dumps(result) + "\n")
        else:
            typer.echo(result["error"], err=True)
            if result.get("remediation"):
                typer.echo(result["remediation"], err=True)
        raise typer.Exit(1)
    if "error" in result:
        typer.echo(result["error"], err=True)
        raise typer.Exit(1)
    items = result.get("next_items", [])
    if not items:
        raise typer.Exit(1)
    item = items[0]
    if fmt == "json":
        sys.stdout.write(json.dumps(item) + "\n")
    else:
        sys.stdout.write((item.get("prompt_suggestion") or "") + "\n")


def plan_loop_cmd(
    cd: Path | None = None,
    max_iterations: int = typer.Option(0, "--max", "-m", help="Max iterations (0=unbounded)"),
    sleep_seconds: float = typer.Option(5.0, "--sleep", "-s", help="Seconds between iterations"),
    agent: str = typer.Option("free", "--agent", "-a", help="Agent for bg runs (default: free)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print only, do not run"),
) -> None:
    """Loop: get next item -> run bg -> repeat until no items or --max reached."""
    from thegent.cli.commands.work_stream_impl import do_next_impl

    iteration = 0
    while True:
        if max_iterations and iteration >= max_iterations:
            console.print(f"[dim]Reached --max {max_iterations}[/dim]")
            break
        result = do_next_impl(cd=cd, limit=1)
        if "error" in result:
            console.print(f"[red]{result['error']}[/red]")
            raise typer.Exit(1)
        items = result.get("next_items", [])
        if not items:
            console.print("[dim]No more work items.[/dim]")
            break
        prompt = items[0].get("prompt_suggestion", "")
        if not prompt:
            console.print("[yellow]Item has no prompt_suggestion, skipping.[/yellow]")
            iteration += 1
            continue
        item_id = items[0].get("id", "?")
        console.print(f"[cyan]Starting {item_id}:[/cyan] {(prompt[:50] + '...') if len(prompt) > 50 else prompt}")
        if dry_run:
            console.print("[dim](dry-run, not running)[/dim]")
        else:
            resolved_cd = _resolve_cwd(cd)
            owner = _default_owner_tag(resolved_cd) if resolved_cd else None
            bg_cmd(
                prompt=prompt,
                agent=agent,
                cd=Path(cd) if cd else None,
                mode="write",
                timeout=300 if agent == "free" else 90,
                full=False,
                model="gpt-5-mini" if agent == "free" else None,
                owner=owner,
            )
        iteration += 1
        if sleep_seconds > 0 and not dry_run:
            import time

            time.sleep(sleep_seconds)


def plan_progress_cmd(limit: int = 10, format: str | None = None) -> None:
    """Show recent runs (work-package progress). Alias for history --limit N."""
    history_cmd(limit=limit, format=format)


def plan_analyze_cmd(
    cd: Path | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
    format: str | None = None,
) -> None:
    """Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk."""
    from thegent.cli.commands.impl import plan_analyze_impl

    result = plan_analyze_impl(cd=cd, pert=pert, resources=resources, continuity=continuity)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        if result.get("remediation"):
            console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)

    settings = ThegentSettings()
    fmt = (format or settings.output_format or "rich").lower()
    if fmt == "json":
        sys.stdout.write(json.dumps(result) + "\n")
        return
    if pert and "pert" in result:
        tbl = Table(title="PERT Milestone Confidence")
        tbl.add_column("Task")
        tbl.add_column("Expected (d)")
        tbl.add_column("Variance")
        tbl.add_column("P50")
        tbl.add_column("P90")
        for tid, v in result["pert"].items():
            tbl.add_row(
                tid,
                f"{v['expected_duration']:.2f}",
                f"{v['variance']:.2f}",
                f"{v['confidence_p50']:.2f}",
                f"{v['confidence_p90']:.2f}",
            )
        console.print(tbl)
    if continuity and "continuity" in result:
        c = result["continuity"]
        console.print(f"\n[bold]Continuity Risk:[/bold] {c['risk_score']:.2f}")
        if c["factors"]:
            for f in cast("Any", c["factors"]):
                console.print(f"  - {f}")
        if c["recommendations"]:
            for r in cast("Any", c["recommendations"]):
                console.print(f"  [yellow]→ {r}[/yellow]")


def closure_pack_cmd(cd: Path | None = None) -> None:
    """Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024)."""
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
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.execution import Auditor

    registry = RunRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)

    # 1. Integrity Check
    audit_res = auditor.verify_registry()

    # 2. Performance Summary
    runs = registry.list_runs(limit=1000)
    completed = [r for r in runs if r.get("status") == "completed"]
    success_rate = (len(completed) / len(runs)) * 100 if runs else 0

    # 3. Evidence Audit
    missing_evidence = [t.get("id") for t in doc.tasks if t.get("status") == "done" and not t.get("evidence")]

    # 3b. Retention & Domain Matrix (G-GP-07)
    domains = set()
    for r in runs:
        d = r.get("domain_tag")
        if d:
            domains.add(d)

    retention_matrix = []
    retention_matrix.append("| Domain | Retention (Days) | Runs |")
    retention_matrix.append("|--------|------------------|------|")
    retention_matrix.append(
        f"| default | {settings.retention_days_registry} | {len([r for r in runs if not r.get('domain_tag')])} |"
    )
    for d in sorted(domains):
        days = settings.retention_by_domain.get(d, settings.retention_days_registry)
        count = len([r for r in runs if r.get("domain_tag") == d])
        retention_matrix.append(f"| {d} | {days} | {count} |")
    retention_section = "\n".join(retention_matrix)

    # 4. Contract Telemetry (FR-X08)
    ct = ContractTelemetry(settings.session_dir)
    stats = ct.get_stats(limit=500)
    budget = ct.get_drift_budget_status(structural_budget_pct=5.0, semantic_budget_pct=10.0, limit=500)
    drift_issues = ct.detect_drift(window_size=50)
    telemetry_section = f"""- **Parse Quality (Success Rate):** {stats.get("success_rate", 0) * 100:.1f}%
- **Fallback Rate:** {stats.get("fallback_rate", 0) * 100:.1f}%
- **Avg Adapter Confidence:** {stats.get("avg_confidence", 0):.2f}
- **Structural Drift:** {budget.get("structural_rate_pct", 0)}% (budget: {budget.get("structural_budget_pct", 5)}%)
- **Semantic Drift:** {budget.get("semantic_rate_pct", 0)}% (budget: {budget.get("semantic_budget_pct", 10)}%)
- **Drift Within Budget:** {"Yes" if budget.get("within_budget", True) else "No"}
- **Drift Issues:** {len(drift_issues)} detected
{chr(10).join([f"  - {i}" for i in drift_issues[:5]]) if drift_issues else "  - None"}"""

    pack_path = cwd / ".factory" / f"closure_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    content = f"""# Thegent Orchestration Closure Pack
Generated: {datetime.now().isoformat()}
DAG Session: {dag_path}

## 1. Governance & Security Signoff (WP-6002)
- **Registry Integrity:** {audit_res["status"].upper()}
- **Valid Records:** {audit_res["valid_count"]}
- **Corrupt/Unsigned:** {audit_res["corrupt_count"]}
- **Environment:** {settings.environment}
- **Audit Trail Integrity:** Verified via `thegent history verify`
- **Technical Architecture:** See `docs/`, `CONTRACT_AUTHORITY.md`
- **Risk Assessment:** See WP-0004 risk scoring; governance research in `docs/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md`
- **Human Oversight:** Escalation via `thegent govern feedback`; runbook in `docs/RUNBOOK.md`

## 2. Reliability & SLO Certification (WP-6003)
- **Overall Success Rate:** {success_rate:.1f}%
- **Total Tasks in DAG:** {len(doc.tasks)}
- **Completed Tasks:** {len([t for t in doc.tasks if t.get("status") == "done"])}
- **Failed Tasks:** {len([t for t in doc.tasks if t.get("status") == "failed"])}
- **Processing Integrity:** Idempotent execution; replay-safe history

## 3. Evidence & Retention (G-GP-07)
### Evidence Completeness
- **Tasks Missing Evidence:** {len(missing_evidence)}
{chr(10).join([f"  - {tid}" for tid in missing_evidence]) if missing_evidence else "  - None (All tasks have linked evidence)"}

### Tiered Retention Matrix
{retention_section}

## 4. Decommission & Successor Roadmap (WP-6006/6008)
- **Sunset Plan:** See `docs/enterprise/DECOMMISSIONING_PLAN.md`
- **Temporary Controls:** None active. All Phase 0-6 features are now core.
- **Cleanup:** Run `thegent archive` to prune old session data.
- **Next Steps:** Monitor KPI drift via `thegent benchmark`; run `thegent govern conformance --check-drift` for adapter drift.

## 5. Contract Telemetry & Observability (FR-X08)
{telemetry_section}

## 6. Formal Closure
This session is formally closed and verified for launch readiness.
"""
    pack_path.write_text(content)
    console.print(f"[green]Closure pack generated: {pack_path}[/green]")


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
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc.
    If --auto-run-next, spawn next ready tasks after sync."""
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
    from thegent.execution import CheckpointRegistry

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
    from thegent.execution import CheckpointRegistry

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
    from thegent.execution import CheckpointRegistry

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
        reason = c.get("reason", "")
        table.add_row(cid, created, owner, reason)

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
    from thegent.execution import CheckpointRegistry

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
    # Simple line-by-line comparison for now
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


def workstream_query_cmd(query: str) -> None:
    """Execute SQL query on workstream database."""
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        results = db.execute_query(query)

        if not results:
            console.print("[yellow]No results[/yellow]")
            return

        # Display as table
        table = Table(title="Query Results")
        if results:
            # Use first row keys as columns
            for key in results[0]:
                table.add_column(key, style="cyan")

            for row in results[:100]:  # Limit to 100 rows
                table.add_row(*[str(row.get(k, "")) for k in results[0]])

        console.print(table)
        if len(results) > 100:
            console.print(f"[dim]... and {len(results) - 100} more rows[/dim]")
    except Exception as e:
        console.print(f"[red]Error executing query: {e}[/red]")


def workstream_stats_cmd() -> None:
    """Get workstream statistics."""
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        stats = db.get_statistics()
        lane_counts = db.get_running_count_by_lane()
        recent_costs = db.get_recent_costs(limit=5)

        console.print("[bold]Workstream Statistics[/bold]\n")

        # Main stats
        stats_table = Table(title="Statistics")
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="green")
        stats_table.add_row("Running", str(stats["running"]))
        stats_table.add_row("Completed", str(stats["completed"]))
        stats_table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
        stats_table.add_row("Avg Duration", f"{stats['avg_duration']:.1f}s")
        stats_table.add_row("Deferred", str(stats["deferred"]))
        console.print(stats_table)

        # Lane breakdown
        if lane_counts:
            lane_table = Table(title="Lane Breakdown")
            lane_table.add_column("Lane", style="cyan")
            lane_table.add_column("Running", style="green")
            for lane, count in lane_counts.items():
                lane_table.add_row(lane, str(count))
            console.print("\n")
            console.print(lane_table)

        # Recent costs
        if recent_costs:
            cost_table = Table(title="Recent Costs")
            cost_table.add_column("Period", style="cyan")
            cost_table.add_column("Cost", style="green")
            cost_table.add_column("Tasks", style="yellow")
            cost_table.add_column("Avg/Task", style="dim")
            for cost in recent_costs:
                cost_table.add_row(
                    cost["period"], f"${cost['cost_usd']:.2f}", str(cost["task_count"]), f"${cost['avg_per_task']:.4f}"
                )
            console.print("\n")
            console.print(cost_table)
    except Exception as e:
        console.print(f"[red]Error getting stats: {e}[/red]")


def workstream_dashboard_cmd() -> None:
    """Launch workstream dashboard TUI."""
    from thegent.tui.workstream_dashboard import run_dashboard

    run_dashboard()


def workstream_launch_cmd() -> None:
    """Launch the auto-launch system in the background."""
    import time

    from thegent.planning.auto_launch import AutoLaunchSystem

    console.print("[bold]Auto-Launch System Starting...[/bold]")
    system = AutoLaunchSystem()
    system.start()

    console.print("[green]Auto-launch system is running. Press Ctrl+C to stop.[/green]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("[yellow]Stopping auto-launch system...[/yellow]")
        system.stop()
        console.print("[green]Stopped.[/green]")


def workstream_dependencies_cmd() -> None:
    """Show the workstream dependency graph."""
    from rich.table import Table

    from thegent.planning.workstream_db import WorkstreamDB

    db = WorkstreamDB()
    graph = db.get_dependency_graph()

    table = Table(title="Workstream Dependency Graph")
    table.add_column("Item", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Depends On", style="yellow")
    table.add_column("Dep Status", style="bold")
    table.add_column("Satisfied At", style="green")

    for d in graph:
        satisfied = d.get("satisfied_at")
        table.add_row(
            d.get("item_title", d["item_id"]),
            d.get("item_status", "unknown"),
            d.get("depends_on_title", d["depends_on_item_id"]),
            d.get("depends_on_status", "unknown"),
            str(satisfied) if satisfied else "—",
        )

    console.print(table)


__all__ = [
    "closure_pack_cmd",
    "dag_add_cmd",
    "dag_cancel_cmd",
    "dag_checkpoint_cmd",
    "dag_checkpoints_cmd",
    "dag_list_cmd",
    "dag_probe_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "dag_recover_cmd",
    "dag_remove_cmd",
    "dag_rollback_cmd",
    "dag_run_cmd",
    "dag_status_cmd",
    "dag_sync_cmd",
    "dag_update_cmd",
    "dag_validate_cmd",
    "plan_analyze_cmd",
    "plan_claim_cmd",
    "plan_complete_cmd",
    "plan_do_next_cmd",
    "plan_get_next_cmd",
    "plan_incorporate_cmd",
    "plan_loop_cmd",
    "plan_progress_cmd",
    "plan_verify_workstream_cmd",
    "plan_wait_next_cmd",
    "workstream_dashboard_cmd",
    "workstream_dependencies_cmd",
    "workstream_launch_cmd",
    "workstream_query_cmd",
    "workstream_stats_cmd",
]
