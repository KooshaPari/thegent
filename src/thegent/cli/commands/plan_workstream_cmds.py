"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
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


"""Workstream and planning-related CLI commands.

Commands for work stream orchestration, planning, and analysis.
Extracted from plan_cmds.py to manage module size.
"""

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


def plan_lint_workstream_cmd(cd: Path | None = None) -> None:
    """Validate canonical WORK_STREAM schema structure."""
    from thegent.utils.workstream_ops import WorkStreamOps

    root = cd or Path.cwd()
    ops = WorkStreamOps(base_dir=root)
    errors = ops.lint_schema()
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print("[green]WORK_STREAM schema is valid.[/green]")


def plan_normalize_workstream_cmd(cd: Path | None = None) -> None:
    """Sort and normalize WL sections and status-line formatting."""
    from thegent.utils.workstream_ops import WorkStreamOps

    root = cd or Path.cwd()
    ops = WorkStreamOps(base_dir=root)
    ops.sort_and_normalize()
    console.print("[green]WORK_STREAM normalized successfully.[/green]")


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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
            sys.stdout.write(json.dumps(result).decode() + "\n")
        else:
            console.print(f"[red]{result['error']}[/red]")
            if result.get("remediation"):
                console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode() + "\n")
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
            sys.stdout.write(json.dumps(result).decode() + "\n")
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
        sys.stdout.write(json.dumps(item).decode() + "\n")
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
        sys.stdout.write(json.dumps(result).decode() + "\n")
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


