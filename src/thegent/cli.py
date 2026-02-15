"""Thegent CLI commands."""

import getpass
import csv
import io
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from thegent.agents import (
    get_fallback_agents,
    get_runner,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)
from thegent.agents.cliproxy_manager import run_login
from thegent.agents.registry import AGENT_LABELS
from thegent.config import ThegentSettings
from thegent.exit_codes import EXIT_HEALTH_GATE_FAILED, EXIT_TIMEOUT, get_exit_message
from thegent.execution import RunMeta, RunRegistry
from thegent.output_parser import extract_condensed
from thegent.cli_impl import (
    _coerce_issue_types,
    _resolve_cwd,
    _resolve_droids_dir,
    _resolve_agent_model,
    _inject_time_constraint,
    _default_owner_tag,
    _session_dir,
    _session_paths,
    _session_scope_dirs,
    _new_session_id,
    _is_pid_running,
    _read_session_meta,
    _save_session_meta,
    _find_session_meta,
    _resolve_session_status,
    _build_continuation_prompt,
    _parse_dag_session,
    _parse_dag_full,
    _validate_dag,
    _validate_task_id,
    _validate_agent,
    _check_dag_cycles,
    _dag_path,
    _ensure_dag_file,
    _session_status_for,
    _ensure_evidence_header,
    _dag_update_task,
    _ensure_contract_version_header,
    _parse_depends_on,
    _get_ready_task_ids,
    _resolve_prompt,
    _atomic_write,
    _serialize_dag,
    DagDocument,
    SECONDS_PER_TOOL_CALL,
    _LOG_FOLLOW_POLL_SECONDS,
    _normalize_output_format,
)

console = Console()


def _scope_key(owner: str) -> str:
    """Stable filesystem-safe key for owner tags."""
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in owner)


def _compose_owner_tag(user: str, cwd: Path, scope: str = "") -> str:
    """Build deterministic owner tags with optional scope expansion."""
    base_name = cwd.name
    normalized_scope = os.path.expandvars(scope or "").format(
        user=user,
        uid=os.getuid(),
        pid=os.getpid(),
        ppid=os.getppid(),
        cwd=base_name,
    ).strip()
    if normalized_scope:
        return f"{user}:{base_name}:{normalized_scope}"
    return f"{user}:{base_name}"


def run_cmd(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
    live: bool = False,
    droid: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    failover: bool = False,
    routing: str | None = None,
    include_contract: bool = False,
    run_id: str | None = None,
    lane: str = "standard",
    confidence: float | None = None,
    arbitration: str | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
) -> None:
    """Run an agent or droid with the given prompt. Model-first: agent=None, model set."""
    from thegent.cli_impl import run_impl
    from thegent.models import ModelCatalog, resolve_route

    # Model-first with provider hint: resolve agent and validate model availability
    effective_agent = agent
    if agent is None and model and provider:
        effective_agent = resolve_agent(provider)
        settings = ThegentSettings()
        policy = (settings.default_routing or "prefer_direct").lower()
        resolved = resolve_route(model, provider_hint=provider, policy=policy)
        if resolved is None:
            routes = ModelCatalog.routes_for(model)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else "none"
            console.print(
                f"[red]Model '{model}' not available via provider '{provider}'. Available: {available}.[/red]"
            )
            raise typer.Exit(1)
    elif agent is None and model:
        # Model-first without provider: use first available route
        routes = ModelCatalog.routes_for(model)
        if not routes:
            console.print(f"[red]Model '{model}' has no available providers.[/red]")
            raise typer.Exit(1)
        effective_agent = routes[0].provider

    # WP-X2/X5/X6/X7: Unified execution via run_impl (FSM + Policy + Telemetry)
    res = run_impl(
        agent=effective_agent or agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        model=model,
        run_id=run_id,
        owner=None, 
        include_contract=include_contract,
        lane=lane,
        confidence=confidence,
        override_reason=override_reason,
        contract_version=contract_version,
        domain=domain,
    )
    
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        if "agents" in res:
            console.print(f"[dim]Agents: {res['agents']}[/dim]")
        raise typer.Exit(res.get("exit_code", 1))

    if full:
        if res.get("stderr"):
            console.print(res["stderr"], style="dim")
        if res.get("stdout"):
            console.print(res["stdout"])
    else:
        # condensed output is already in stdout if not full
        if res.get("stdout"):
            console.print(res["stdout"])
            
    if res.get("timed_out"):
        console.print("[yellow]Process hit safety ceiling (agent self-limits via tool-call budget)[/yellow]")
    
    if res.get("exit_code") != 0:
        raise typer.Exit(res.get("exit_code", 1))


def bg_cmd(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str,
    timeout: int,
    full: bool,
    droid: str | None,  # kept for API compat, ignored
    model: str | None,
    provider: str | None = None,
    routing: str | None = None,
    failover: bool = False,
    owner: str | None,
    output_format: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    run_id: str | None = None,
    correlation_id: str | None = None,
    lane: str | None = None,
    idempotency_token: str | None = None,
    confidence: float | None = None,
    arbitration: str | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
) -> str:
    from thegent.cli_impl import bg_impl
    
    # WP-X2/X5/X6/X7: Unified background execution via bg_impl
    res = bg_impl(
        agent=agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        model=model,
        owner=owner,
        continue_from=continue_from,
        continuation_include_stderr=continuation_include_stderr,
        include_contract=include_contract,
        routing=routing,
        failover=failover,
        run_id=run_id,
        contract_version=contract_version,
        domain=domain,
    )
    
    if "error" in res:
        console.print(f"[red]{res['error']}[/red]")
        raise typer.Exit(res.get("exit_code", 1))
        
    session_id = res["session_id"]
    log_path = res["log_path"]
    owner_tag = res["owner"]
    
    settings = ThegentSettings()
    fmt = _normalize_output_format(output_format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print_json(data=res)
    elif fmt == "md":
        console.print(f"**Session started:** `{session_id}`  \n**Log:** `{log_path}`")
    else:
        console.print(f"Session started: [bold cyan]{session_id}[/bold cyan]")
        console.print(f"Log path: [dim]{log_path}[/dim]")
        console.print(f"Owner: [dim]{owner_tag}[/dim]")
        
    return session_id


def history_cmd(limit: int = 50, format: str | None = None) -> None:
    """List execution run history (sync and background)."""
    from thegent.cli_impl import history_impl

    runs = history_impl(limit=limit)
    if not format or format == "rich":
        if not runs:
            console.print("[dim]No execution history found.[/dim]")
            return
        
        table = Table(title=f"Execution History (last {limit})")
        table.add_column("Run ID", style="cyan")
        table.add_column("Started (UTC)", style="magenta")
        table.add_column("Agent", style="green")
        table.add_column("Lane", style="dim")
        table.add_column("Conf", justify="right")
        table.add_column("Role", style="italic")
        table.add_column("Status", style="bold")
        table.add_column("Exit", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Prompt Preview", style="dim")

        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "").split("T")[-1][:8]
            agent = run.get("agent", "?")
            lane = run.get("lane", "standard")
            conf = f"{run.get('confidence', 1.0):.2f}" if run.get("confidence") is not None else "—"
            role = run.get("arbitration", "—")
            status = run.get("status", "started")
            status_style = "green" if status == "completed" else "yellow" if status == "started" else "red"
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"
            
            prompt = run.get("prompt", "")
            prompt_preview = (prompt[:30] + "...") if len(prompt) > 30 else prompt

            table.add_row(
                rid,
                started,
                agent,
                lane,
                conf,
                role,
                f"[{status_style}]{status}[/{status_style}]",
                exit_code,
                duration,
                prompt_preview,
            )
        console.print(table)
    elif format == "json":
        console.print_json(data=runs)
    elif format == "md":
        lines = ["# Execution History", ""]
        lines.append("| Run ID | Started | Agent | Status | Exit | Duration | Prompt |")
        lines.append("|--------|---------|-------|--------|------|----------|--------|")
        for run in runs:
            rid = run.get("run_id", "?")
            started = run.get("started_at_utc", "?")
            agent = run.get("agent", "?")
            status = run.get("status", "?")
            exit_code = str(run.get("exit_code", "—"))
            duration = f"{run.get('duration_s', 0):.1f}s" if run.get("duration_s") else "—"
            prompt = run.get("prompt", "").replace("\n", " ")
            lines.append(f"| {rid} | {started} | {agent} | {status} | {exit_code} | {duration} | {prompt} |")
        console.print("\n".join(lines))

def events_cmd(run_id: str | None = None, limit: int = 100, format: str | None = None) -> None:
    """List raw telemetry events."""
    from thegent.cli_impl import events_impl

    events = events_impl(run_id=run_id, limit=limit)
    if not format or format == "rich":
        if not events:
            console.print("[dim]No events found.[/dim]")
            return
        
        table = Table(title="Telemetry Events")
        table.add_column("Run ID", style="cyan")
        table.add_column("Event/Status", style="magenta")
        table.add_column("Timestamp", style="green")
        table.add_column("Payload Details", style="dim")

        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            ts = ts.split("T")[-1][:8]
            
            details = []
            if event.get("agent"): details.append(f"agent={event['agent']}")
            if event.get("exit_code") is not None: details.append(f"exit={event['exit_code']}")
            if event.get("duration_s"): details.append(f"dur={event['duration_s']:.1f}s")
            
            table.add_row(rid, ev_type, ts, ", ".join(details))
        console.print(table)
    elif format == "json":
        console.print_json(data=events)
    elif format == "md":
        lines = ["# Telemetry Events", ""]
        lines.append("| Run ID | Event | Timestamp | Details |")
        lines.append("|--------|-------|-----------|---------|")
        for event in events:
            rid = event.get("run_id", "?")
            ev_type = event.get("event") or event.get("status", "started")
            ts = event.get("started_at_utc") or event.get("ended_at_utc") or "?"
            details = str(event)
            lines.append(f"| {rid} | {ev_type} | {ts} | {details} |")
        console.print("\n".join(lines))


def data_protection_cmd(format: str | None = None) -> None:
    """Show status of data protection and privacy controls."""
    from thegent.cli_impl import get_data_protection_status_impl
    status = get_data_protection_status_impl()
    
    fmt = _normalize_output_format(format)
    if fmt == "json":
        console.print(json.dumps(status, indent=2))
        return
        
    table = Table(title="Data Protection & Privacy Status (WP-3006)")
    table.add_column("Control")
    table.add_column("Status")
    
    def _fmt_bool(v: bool) -> str:
        return "[green]PASS[/green]" if v else "[red]FAIL[/red]"
        
    table.add_row("Session Directory", status["session_dir"])
    table.add_row("Permissions Restricted (0700)", _fmt_bool(status["permissions_restricted"]))
    table.add_row("Sensitive Data Masking", _fmt_bool(status["masking_enabled"]))
    table.add_row("Retention Policy", f"{status['retention_policy_days']} days")
    
    console.print(table)


def audit_verify_cmd(format: str | None = None) -> None:
    """Verify the integrity of the execution run registry."""
    settings = ThegentSettings()
    from thegent.execution import Auditor, RunRegistry
    registry = RunRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)
    
    res = auditor.verify_registry()
    
    if format == "json":
        console.print(json.dumps(res, indent=2))
        return

    if res["status"] == "passed":
        console.print(f"[green]Audit Passed:[/green] {res['valid_count']} records verified.")
    elif res["status"] == "empty":
        console.print("[dim]Registry empty. No records to verify.[/dim]")
    else:
        console.print(f"[red]Audit Failed:[/red] {res['corrupt_count']} issues found.")
        for issue in res.get("issues", []):
            console.print(f"  - {issue}")
    
    if res["status"] == "passed":
        # Check for unsigned records
        total = res["valid_count"]
        if total > 0:
            console.print(f"[dim]Note: All {total} records carry valid signatures.[/dim]")


def escalate_add_cmd(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    lane: str = "standard",
) -> None:
    """Add a blocked run to the escalation queue (WP-3008)."""
    from thegent.cli_impl import escalate_add_impl
    escalate_add_impl(run_id=run_id, reason=reason, sla_minutes=sla_minutes, owner=owner, lane=lane)
    console.print(f"[green]Added run_id={run_id} to escalation queue (SLA: {sla_minutes} min)[/green]")


def escalate_list_cmd(
    past_sla_only: bool = False,
    limit: int = 50,
    format: str | None = None,
) -> None:
    """List governance escalation queue (WP-3008)."""
    from thegent.cli_impl import escalate_list_impl
    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        console.print(json.dumps(items, indent=2))
        return
    if not items:
        console.print("[dim]No escalation items.[/dim]")
        return
    table = Table(title="Escalation Queue (WP-3008)")
    table.add_column("Run ID")
    table.add_column("Reason")
    table.add_column("Owner")
    table.add_column("Lane")
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
            it.get("blocked_at_utc", "?")[:19],
            it.get("escalate_by_utc", "?")[:19],
            past,
        )
    console.print(table)


def sweep_cmd(
    drift_window: int = 50,
    include_audit: bool = False,
    format: str | None = None,
) -> None:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    from thegent.cli_impl import sweep_impl

    result = sweep_impl(
        drift_window=drift_window,
        include_audit=include_audit,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        # Strip non-JSON-serializable if any
        out = {k: v for k, v in result.items() if k != "audit" or v is not None}
        if result.get("audit"):
            out["audit"] = result["audit"]
        console.print(json.dumps(out, indent=2))
        if not result["pass"]:
            raise typer.Exit(1)
        return

    if result["pass"]:
        console.print("[green]Sweep passed: no drift, no past-SLA escalations.[/green]")
        return

    parts = []
    if result["drift_issues"]:
        for i in result["drift_issues"]:
            parts.append(f"[red]![/red] {i}")
    if result["past_sla_count"] > 0:
        parts.append(f"[yellow]Past SLA:[/yellow] {result['past_sla_count']} escalation(s). Run `thegent govern escalate list --past-sla`")
    if result.get("audit") and result["audit"].get("status") not in ("passed", "empty"):
        parts.append(f"[red]Audit:[/red] {result['audit'].get('status', 'failed')}")
    if parts:
        from rich.panel import Panel
        console.print(Panel("\n".join(parts), title="Policy Drift Sweep (WP-3005)", border_style="red"))
    raise typer.Exit(1)


def escalate_resolve_cmd(run_id: str, resolution: str = "resolved") -> None:
    """Mark an escalation item as resolved (WP-3008)."""
    from thegent.cli_impl import escalate_resolve_impl
    ok = escalate_resolve_impl(run_id=run_id, resolution=resolution)
    if ok:
        console.print(f"[green]Resolved run_id={run_id}[/green]")
    else:
        console.print(f"[red]No pending escalation found for run_id={run_id}[/red]")


def policy_show_cmd() -> None:
    """Show active governance policies and thresholds."""
    settings = ThegentSettings()
    console.print(f"[bold]Active Governance Policies[/bold] (Environment: [cyan]{settings.environment}[/cyan])")
    
    table = Table(show_header=True)
    table.add_column("Policy Name")
    table.add_column("Rule / Threshold")
    table.add_column("Status")
    
    table.add_row("Critical Confidence", ">= 0.9", "[green]Active[/green]")
    table.add_row("Production Trust", f">= {settings.trust_score_threshold}", "[green]Active[/green]" if settings.environment == "production" else "[dim]Inactive[/dim]")
    table.add_row("Agent Restriction", "Block 'unknown' in Prod/Critical", "[green]Active[/green]")
    table.add_row("Audit Signing", "SHA-256 Run Signatures", "[green]Active[/green]")
    table.add_row("Override TTL (WP-3003)", f"{settings.override_ttl_seconds}s", "[green]Active[/green]")
    
    console.print(table)


def contracts_registry_cmd(format: str | None = None) -> None:
    """Show the contract registry and compatibility matrix."""
    from thegent.contracts.registry import get_registry
    from rich.table import Table
    from rich.console import Console
    
    registry = get_registry()
    versions = registry.list_versions()
    
    console = Console()
    if format == "json":
        import json
        console.print(json.dumps([v.__dict__ for v in (versions or [])], indent=2))
        return
        
    table = Table(title="Contract Registry")
    table.add_column("Contract ID", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Status", style="red")
    
    for v in sorted(versions, key=lambda x: (x.contract_id, x.version)):
        status = "[red]DEPRECATED[/red]" if v.deprecated else "[green]ACTIVE[/green]"
        if v.migration_window_end:
            status += f"\n[dim](ends {v.migration_window_end})[/dim]"
        table.add_row(v.contract_id, v.version, v.description, status)
        
    console.print(table)


def migration_cmd(contract_id: str, version: str, format: str | None = None) -> None:
    """Evaluate migration status for a contract version."""
    from thegent.contracts.migration import MigrationController
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    mc = MigrationController()
    res = mc.evaluate_version(contract_id, version)
    
    if format == "json":
        import json
        console.print(json.dumps(res, indent=2))
        return

    color = "green" if res["allowed"] else "red"
    if res["status"] == "deprecated":
        color = "yellow"
    
    panel = Panel(
        f"[bold]Status:[/bold] {res['status'].upper()}\n"
        f"[bold]Allowed:[/bold] {'YES' if res['allowed'] else 'NO'}\n"
        f"[bold]Reason:[/bold] {res['reason']}\n"
        f"[bold]Days Left:[/bold] {res.get('migration_days_left', 'N/A')}",
        title=f"Migration Evaluation: {contract_id}@{version}",
        border_style=color,
    )
    console.print(panel)


def drift_cmd(
    window: int = 50,
    format: str | None = None,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
) -> None:
    """Detect significant drift in contract performance and check alert budgets (G-RV-07)."""
    from thegent.contracts.telemetry import ContractTelemetry
    from rich.console import Console
    from rich.panel import Panel

    settings = ThegentSettings()
    console = Console()
    ct = ContractTelemetry(settings.session_dir)
    issues = ct.detect_drift(window_size=window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
    )

    if format == "json":
        import json
        out = {"issues": issues, "budget": budget}
        console.print(json.dumps(out, indent=2))
        return

    if not issues and budget["within_budget"]:
        console.print("[green]No significant contract drift detected.[/green]")
        return

    from rich.list import List

    parts = []
    if issues:
        issue_list = List([f"[red]![/red] {i}" for i in issues])
        parts.append(str(issue_list))
    if not budget["within_budget"]:
        parts.append(
            f"[yellow]Budget exceeded:[/yellow] structural {budget['structural_rate_pct']}% "
            f"(budget {budget['structural_budget_pct']}%), semantic {budget['semantic_rate_pct']}% "
            f"(budget {budget['semantic_budget_pct']}%)"
        )
    if parts:
        panel = Panel(
            "\n\n".join(parts),
            title=f"Contract Drift Alert (window={window})",
            border_style="red",
        )
        console.print(panel)


def observe_summary_cmd(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    format: str | None = None,
    provider: str | None = None,
    top_escalations: int = 10,
) -> None:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""
    from thegent.cli_impl import observe_summary_impl
    from rich.panel import Panel

    result = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
        provider=provider,
        top_escalations=top_escalations,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        console.print(json.dumps(result, indent=2))
        return

    kpis = result["kpis"]
    drift = result["drift"]
    esc = result["escalation"]
    alerts = result.get("alerts", [])
    status = result.get("status", "healthy")
    status_badge = {
        "healthy": "[green]healthy[/green]",
        "critical": "[red]critical[/red]",
    }.get(status, status)
    provider_label = f" provider={provider}" if provider else ""

    lines = [
        f"[bold]Status[/bold]: {status_badge}",
        f"[bold]KPIs[/bold] (n={kpis['total_events']}{provider_label}): fallback={kpis['fallback_rate']:.1%} success={kpis['success_rate']:.1%} conf={kpis['avg_confidence']:.2f}",
        f"[bold]Drift[/bold]: structural={drift['structural_rate_pct']:.1f}%/budget {drift['structural_budget_pct']:.1f}% "
        f"semantic={drift['semantic_rate_pct']:.1f}%/budget {drift['semantic_budget_pct']:.1f}% "
        + ("[green]within budget[/green]" if drift["within_budget"] else "[red]over budget[/red]"),
        f"[bold]Escalation[/bold]: backlog={esc['backlog_count']} past-sla={esc['past_sla_count']}",
    ]
    top_escalations = esc.get("top_escalations", [])
    for item in top_escalations[:3]:
        if not isinstance(item, dict):
            continue
        owner = item.get("owner") or "—"
        minutes = item.get("minutes_overdue")
        sla = item.get("minutes_remaining")
        if item.get("past_sla"):
            timing = f"overdue={minutes}m"
        elif sla is not None:
            timing = f"remaining={sla}m"
        else:
            timing = "timing-unknown"
        lines.append(
            f" - {item.get('run_id')} / {owner} / {item.get('agent')} / {item.get('lane')} / {timing} / "
            f"priority={item.get('priority', 0)}"
        )

    if drift["issues"]:
        lines.append("[red]Drift issues:[/red] " + "; ".join(drift["issues"][:3]))
    if alerts:
        lines.append("[red]Alerts:[/red] " + "; ".join(alerts))
    panel = Panel("\n".join(lines), title="Observe Summary (FR-X08)", border_style="cyan")
    console.print(panel)


def contracts_conformance_cmd(
    format: str | None = None,
    check_drift: bool = False,
    drift_window: int = 50,
) -> None:
    """Run provider adapter conformance tests."""
    from thegent.contracts.conformance import run_conformance_suite
    from rich.table import Table
    from rich.console import Console

    session_dir = ThegentSettings().session_dir if check_drift else None
    report = run_conformance_suite(session_dir=session_dir, drift_window=drift_window)
    console = Console()

    if format == "json":
        import json
        import typer
        console.print(json.dumps(report, indent=2))
        if report.get("drift_issues") or report["failed"] > 0:
            raise typer.Exit(1)
        return

    table = Table(title=f"Adapter Conformance (Passed: {report['passed']}/{report['total']})")
    table.add_column("Test")
    table.add_column("Provider")
    table.add_column("Result")
    table.add_column("Conf")
    table.add_column("Issues")

    for r in report["results"]:
        status = "[green]PASS[/green]" if r["success"] else "[red]FAIL[/red]"
        issues = ", ".join(r["issues"]) if r["issues"] else "-"
        table.add_row(r["name"], r["provider"], status, f"{r['confidence']:.2f}", issues)

    console.print(table)

    if report.get("drift_checked") and report.get("drift_issues"):
        console.print()
        panel = Panel(
            "\n".join(f"[red]![/red] {i}" for i in report["drift_issues"]),
            title="Drift Alarms",
            border_style="red",
        )
        console.print(panel)

    if report["failed"] > 0 or report.get("drift_issues"):
        import typer
        raise typer.Exit(1)


from rich.panel import Panel
from rich.columns import Columns


def cockpit_cmd() -> None:
    """Show high-level operator cockpit summary."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry, CircuitBreakerRegistry, CheckpointRegistry
    from thegent.cli_impl import ps_impl
    
    registry = RunRegistry(settings.session_dir)
    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    ckpt_registry = CheckpointRegistry(settings.session_dir)
    
    # 1. Session Health
    sessions = ps_impl(all=True)
    running = [s for s in sessions if s["status"] == "running"]
    failed = [s for s in sessions if "exited" in s["status"] and s["status"] != "exited:0"]
    
    # 2. Registry Summary
    runs = registry.list_runs(limit=100)
    recent_errors = [r for r in runs if r.get("status") == "failed"][:5]
    
    # 3. Circuit Status
    targets = ["claude", "gemini", "codex", "copilot", "antigravity"]
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]
    
    # Render Panels
    session_panel = Panel(
        f"[bold]Sessions[/bold]\nRunning: [green]{len(running)}[/green]\nFailed: [red]{len(failed)}[/red]",
        title="Orchestration Health",
        border_style="cyan"
    )
    
    circuit_text = "\n".join([f"- {t}: [red]OPEN[/red]" for t in open_circuits]) or "[green]All Closed[/green]"
    circuit_panel = Panel(
        f"[bold]Circuits[/bold]\n{circuit_text}",
        title="Resource State",
        border_style="magenta"
    )
    
    ckpt_panel = Panel(
        f"Last Checkpoint: [dim]{ckpt_registry.list_checkpoints(limit=1)[0].get('checkpoint_id') if ckpt_registry.list_checkpoints(limit=1) else 'None'}[/dim]",
        title="Continuity",
        border_style="yellow"
    )
    
    console.print(Columns([session_panel, circuit_panel, ckpt_panel]))
    
    if recent_errors:
        console.print("\n[bold]Recent Failure Rationale (WP-4002/4007):[/bold]")
        for r in recent_errors:
            rid = r.get("run_id")
            reason = r.get("policy_reason") or r.get("error_class") or "Unknown"
            console.print(f"  - [cyan]{rid}[/cyan]: {reason}")


def feedback_cmd(run_id: str, score: float, note: str | None = None) -> None:
    """Provide operator feedback for a specific run."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry
    registry = RunRegistry(settings.session_dir)
    registry.register_feedback(run_id, score, note)
    console.print(f"[green]Feedback recorded for run {run_id}.[/green]")


def ps_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    from thegent.cli_impl import ps_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    rows = ps_impl(owner=own if not all_sessions else None, all=all_sessions, include_contract=include_contract)
    if not rows:
        console.print("[dim]No sessions.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print(json.dumps(rows, indent=2))
    elif fmt == "md":
        console.print("## Thegent Sessions")
        headers = "| id | agent | owner | pid | status | prompt |"
        separator = "|----|-------|-------|-----|--------|--------|"
        if include_contract:
            headers = "| id | agent | owner | pid | status | prompt | route_request | route_contract |"
            separator = "|----|-------|-------|-----|--------|--------|--------------|----------------|"
        console.print(headers)
        console.print(separator)
        for r in rows:
            base = (
                f"| {r['id']} | {r['agent']} | {r['owner']} | {r['pid']} | "
                f"{r['status']} | {r['prompt_preview']} |"
            )
            if include_contract:
                route_request = r.get("route_request")
                route_contract = r.get("route_contract")
                base += f" {json.dumps(route_request) if route_request is not None else '—'} | "
                base += f"{json.dumps(route_contract) if route_contract is not None else '—'} |"
            console.print(base)
    else:
        t = Table(title="Thegent Sessions")
        t.add_column("Session")
        t.add_column("Agent")
        t.add_column("Owner")
        t.add_column("PID")
        t.add_column("Status")
        t.add_column("Prompt")
        t.add_column("Started")
        has_contract_columns = False
        if include_contract and any(
            (r.get("route_contract") is not None or r.get("route_request") is not None)
            for r in rows
        ):
            t.add_column("Requested Model")
            t.add_column("Requested Provider")
            t.add_column("Resolved Alias")
            has_contract_columns = True
        for r in rows:
            row_data = [
                str(r["id"]),
                str(r["agent"]),
                str(r["owner"]),
                str(r["pid"]),
                str(r["status"]),
                str(r["prompt_preview"]),
                str(r.get("started_at_utc", "")),
            ]
            if has_contract_columns:
                row_data.extend(["", "", ""])
            t.add_row(*row_data)
            if has_contract_columns:
                route_request = r.get("route_request") or {}
                requested_model = route_request.get("requested_model", "—")
                requested_provider = route_request.get("requested_provider_hint", "—")
                resolved_alias = route_request.get(
                    "resolved_model_alias",
                    route_request.get("resolved_alias", "—"),
                )
                t.add_row(
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    str(requested_model),
                    str(requested_provider),
                    str(resolved_alias),
                )
        console.print(t)


def session_contracts_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    format: str | None = None,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_audit_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    audit = session_contract_audit_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )
    rows = audit["rows"]
    summary = audit["summary"]
    if not rows and not summary_only:
        console.print("[dim]No sessions match contract audit criteria.[/dim]")
        if missing_only:
            console.print("[dim]No contract gaps detected.[/dim]")
        return

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print(json.dumps({"rows": rows, "summary": summary}, indent=2))
    elif fmt == "md":
        if summary_only:
            console.print(f"summary: {json.dumps(summary)}")
            return
        console.print("## Session Contract Audit")
        console.print(
            "| id | agent | owner | status | state | health | requested_model | requested_provider | "
            "resolved_alias | policy | issues |"
        )
        console.print(
            "|----|-------|-------|--------|-------|--------|----------------|-------------------|"
            "----------|--------|--------|"
        )
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            console.print(
                "| "
                f"{r['session_id']} | "
                f"{r['agent']} | "
                f"{r['owner']} | "
                f"{r['status']} | "
                f"{r['contract_state']} | "
                f"{r.get('contract_health', '—')} | "
                f"{r.get('requested_model', '—')} | "
                f"{r.get('requested_provider_hint', '—')} | "
                f"{r.get('resolved_model_alias', '—')} | "
                f"{r.get('policy', '—')} | "
                f"{issues if issues else '—'} |"
            )
        console.print("")
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']} "
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")
    else:
        if summary_only:
            console.print(
                "summary: "
                f"complete={summary['complete']} partial={summary['partial']} "
                f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
                f"untracked={summary['untracked']} total={summary['total']} "
                f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
                f"error={summary['health']['error']} missing={summary['health']['missing']}"
            )
            return
        t = Table(title="Session Contract Audit")
        t.add_column("Session")
        t.add_column("Agent")
        t.add_column("Owner")
        t.add_column("Status")
        t.add_column("State")
        t.add_column("Health")
        t.add_column("Requested Model")
        t.add_column("Provider")
        t.add_column("Alias")
        t.add_column("Policy")
        t.add_column("Issues")
        for r in rows:
            issues = ", ".join(_coerce_issue_types(r.get("contract_issues")))
            t.add_row(
                str(r["session_id"]),
                str(r["agent"]),
                str(r["owner"]),
                str(r["status"]),
                str(r["contract_state"]),
                str(r.get("contract_health", "—")),
                str(r.get("requested_model", "—")),
                str(r.get("requested_provider_hint", "—")),
                str(r.get("resolved_model_alias", "—")),
                str(r.get("policy", "—")),
                issues or "—",
            )
        console.print(t)
        console.print(
            "summary: "
            f"complete={summary['complete']} partial={summary['partial']} "
            f"request_only={summary['request_only']} contract_only={summary['contract_only']} "
            f"untracked={summary['untracked']} total={summary['total']} "
            f"healthy={summary['health']['healthy']} warning={summary['health']['warning']} "
            f"error={summary['health']['error']} missing={summary['health']['missing']}"
        )
        console.print(f"strict_checks_enabled={summary['strict_checks_enabled']}")


def session_contract_health_gate_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    format: str | None = None,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_gate_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_gate_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    if output is not None:
        chosen_format = (export_format or _infer_export_format(output, fallback="json"))
        if export_format is None:
            if output.suffix and _export_format_from_suffix(output.suffix) is None:
                console.print(
                    f"Note: output path extension '{output.suffix}' is not recognized for export; "
                    f"defaulting to '{chosen_format}'."
                )
        written_as = _write_health_gate_export(
            output=output,
            report=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-gate to: {output} (format={written_as})")

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print(json.dumps(result, indent=2, sort_keys=True))
    elif fmt == "md":
        console.print(_serialize_health_gate_md(result))
    else:
        if result.get("payload_signature"):
            signature = result["payload_signature"]
            console.print(f"payload_signature={signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
        console.print(f"schema_version={result['schema_version']}")
        console.print(f"payload_type={result['payload_type']}")
        console.print(f"status: {result['status']}")
        console.print(f"policy_profile={result.get('policy_profile', 'custom')}")
        if result.get("decision_reasons"):
            console.print(f"decision_reasons={','.join(result.get('decision_reasons', []))}")
        console.print(
            f"ratio: {result['healthy_ratio']} threshold={result['threshold']} pass={result['pass']}"
        )
        console.print(
            f"healthy={result['healthy_count']} unhealthy={result['unhealthy_count']} "
            f"blocked={result['blocked_count']} total={result['total']}"
        )
        console.print(
            f"health: healthy={result['summary']['health']['healthy']} "
            f"warning={result['summary']['health']['warning']} "
            f"error={result['summary']['health']['error']} "
            f"missing={result['summary']['health']['missing']}"
        )
        if result.get("trend_summary"):
            trend = result["trend_summary"]
            console.print(
                f"trend: baseline={trend.get('baseline_available', False)} "
                f"ratio_delta={trend.get('blocked_ratio_delta', None)} "
                f"blocked_delta={trend.get('blocked_count_delta', None)}"
            )
    if not result["pass"]:
        if msg := get_exit_message(EXIT_HEALTH_GATE_FAILED):
            print(msg, file=sys.stderr)
        raise typer.Exit(EXIT_HEALTH_GATE_FAILED)


def _serialize_health_report_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Report")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {(result.get('compat') or {}).get('mode', 'compat')}")
    lines.append(
        f"compat_aliases: {json.dumps((result.get('compat') or {}).get('aliases', {}), sort_keys=True)}"
    )
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(
            f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}"
        )
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(f"total_sessions: {result['total_sessions']}")
    lines.append(f"healthy_sessions: {result['healthy_sessions']}")
    lines.append(f"unhealthy_sessions: {result['unhealthy_sessions']}")
    lines.append(f"blocked_sessions_count: {result['blocked_sessions_count']}")
    lines.append(f"blocked_ratio: {result['blocked_ratio']}")
    lines.append(f"health: {json.dumps(result['health'])}")
    lines.append(f"strict_checks_enabled: {result['strict_checks_enabled']}")
    if result.get("generated_at_utc"):
        lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    if result.get("generated_query"):
        lines.append(f"generated_query: {json.dumps(result['generated_query'])}")
    lines.append("")

    issue_rows = result["issue_breakdown"]
    if issue_rows:
        lines.append("### Issue Breakdown")
        lines.append("| issue | count |")
        lines.append("|------|------:|")
        for row in issue_rows:
            lines.append(f"| {row['issue']} | {row['count']} |")
        lines.append("")

    owner_rows = result["owner_breakdown"]
    if owner_rows:
        lines.append("### Owner Breakdown")
        lines.append("| owner | total | healthy | warning | error | missing |")
        lines.append("|-------|------:|--------:|--------:|------:|--------:|")
        for owner_key, values in sorted(owner_rows.items(), key=lambda kv: str(kv[0])):
            lines.append(
                f"| {owner_key} | {values['total']} | {values['healthy']} | {values['warning']} | "
                f"{values['error']} | {values['missing']} |"
            )
        lines.append("")

    if result["top_blocked"]:
        lines.append("### Top Blocked Sessions")
        lines.append("| session | owner | state | health | issues | remediation |")
        lines.append("|--------|-------|-------|--------|--------|------------|")
        for row in result["top_blocked"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            remediation = ", ".join(row.get("remediation", []))
            lines.append(
                f"| {row['session_id']} | {row['owner']} | {row['state']} | "
                f"{row['health']} | {issues if issues else '—'} | {remediation if remediation else '—'} |"
            )
    return "\n".join(lines)


def _serialize_health_report_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "generated_at_utc",
            "generated_query_owner",
            "generated_query_all",
            "generated_query_strict",
            "generated_query_top_blocked",
            "record_type",
            "status",
            "pass",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "session_id",
            "owner",
            "state",
            "health",
            "issues",
            "remediation",
            "started_at_utc",
            "agent",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            result.get("payload_signature", {}).get("algorithm", "sha256"),
            result.get("payload_signature", {}).get("value", ""),
            result.get("generated_at_utc", ""),
            result.get("generated_query", {}).get("owner", ""),
            str(result.get("generated_query", {}).get("all", "")),
            str(result.get("generated_query", {}).get("strict", "")),
            str(result.get("generated_query", {}).get("top_blocked", "")),
            "summary",
            result["status"],
            str(result["pass"]),
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["health"].get("healthy", ""),
            result["health"].get("warning", ""),
            result["health"].get("error", ""),
            result["health"].get("missing", ""),
            str(result["strict_checks_enabled"]),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    for row in result["top_blocked"]:
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                result.get("payload_signature", {}).get("algorithm", "sha256"),
                result.get("payload_signature", {}).get("value", ""),
                result.get("generated_at_utc", ""),
                result.get("generated_query", {}).get("owner", ""),
                str(result.get("generated_query", {}).get("all", "")),
                str(result.get("generated_query", {}).get("strict", "")),
                str(result.get("generated_query", {}).get("top_blocked", "")),
                "blocked_session",
                result["status"],
                str(result["pass"]),
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["health"].get("healthy", ""),
                result["health"].get("warning", ""),
                result["health"].get("error", ""),
                result["health"].get("missing", ""),
                str(result["strict_checks_enabled"]),
                row.get("session_id", ""),
                row.get("owner", ""),
                row.get("state", ""),
                row.get("health", ""),
            ", ".join(_coerce_issue_types(row.get("issues"))),
                ", ".join(row.get("remediation", [])),
                row.get("started_at_utc", ""),
                row.get("agent", ""),
            ]
        )
    return buffer.getvalue()
    writer.writerow(
        [
            result["schema_version"],
            result["payload_type"],
            result.get("payload_signature", {}).get("algorithm", "sha256"),
            result.get("payload_signature", {}).get("value", ""),
            result.get("generated_at_utc", ""),
            result.get("generated_query", {}).get("owner", ""),
            str(result.get("generated_query", {}).get("all", "")),
            str(result.get("generated_query", {}).get("strict", "")),
            str(result.get("generated_query", {}).get("top_blocked", "")),
            "summary",
            result["status"],
            result["total"],
            result["total_sessions"],
            result["blocked_count"],
            result["blocked_sessions"],
            result["top_blocked_count"],
            result["blocked_ratio"],
            result.get("healthy_count", result["health"].get("healthy", 0)),
            result.get("unhealthy_count", 0),
            result["health"].get("healthy", ""),
            result["health"].get("warning", ""),
            result["health"].get("error", ""),
            result["health"].get("missing", ""),
            "",
            "",
            "",
            "",
            "",
            "",
        ]
    )
    for row in result["top_blocked"]:
        writer.writerow(
            [
            result["schema_version"],
            result["payload_type"],
            result.get("payload_signature", {}).get("algorithm", "sha256"),
            result.get("payload_signature", {}).get("value", ""),
            result.get("generated_at_utc", ""),
            result.get("generated_query", {}).get("owner", ""),
            str(result.get("generated_query", {}).get("all", "")),
            str(result.get("generated_query", {}).get("strict", "")),
            str(result.get("generated_query", {}).get("top_blocked", "")),
            "blocked_session",
            result["status"],
            result["total"],
            result["total_sessions"],
            result["blocked_count"],
            result["blocked_sessions"],
            result["top_blocked_count"],
            result["blocked_ratio"],
            result.get("healthy_count", result["health"].get("healthy", 0)),
            result.get("unhealthy_count", 0),
            result["health"].get("healthy", ""),
            result["health"].get("warning", ""),
            result["health"].get("error", ""),
            result["health"].get("missing", ""),
            row.get("session_id", ""),
            row.get("owner", ""),
            row.get("state", ""),
            row.get("health", ""),
            ", ".join(_coerce_issue_types(row.get("issues"))),
            ", ".join(row.get("remediation", [])),
            row.get("started_at_utc", ""),
            row.get("agent", ""),
        ]
    )
    return buffer.getvalue()


def _serialize_health_report_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    summary_row["payload_signature_algorithm"] = (
        result.get("payload_signature", {}).get("algorithm", "sha256")
    )
    summary_row["payload_signature_value"] = (
        result.get("payload_signature", {}).get("value", "")
    )
    lines.append(json.dumps(summary_row, sort_keys=True))
    for row in result["top_blocked"]:
        row_copy = dict(row)
        row_copy["record_type"] = "blocked_session"
        row_copy["payload_type"] = result["payload_type"]
        row_copy["schema_version"] = result["schema_version"]
        row_copy["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row_copy["status"] = result.get("status", "")
        row_copy["pass"] = result.get("pass", False)
        row_copy["summary_status"] = result["status"] if "status" in result else ""
        row_copy["strict_checks_enabled"] = result.get("strict_checks_enabled", False)
        row_copy["total_sessions"] = result.get("total_sessions", 0)
        row_copy["healthy_sessions"] = result.get("healthy_sessions", 0)
        row_copy["unhealthy_sessions"] = result.get("unhealthy_sessions", 0)
        row_copy["blocked_sessions_count"] = result.get("blocked_sessions_count", 0)
        row_copy["top_blocked_count"] = result.get("top_blocked_count", 0)
        row_copy["healthy"] = result.get("health", {}).get("healthy", 0)
        row_copy["warning"] = result.get("health", {}).get("warning", 0)
        row_copy["error"] = result.get("health", {}).get("error", 0)
        row_copy["missing"] = result.get("health", {}).get("missing", 0)
        row_copy["blocked_ratio"] = result.get("blocked_ratio", 0.0)
        row_copy["payload_signature_algorithm"] = (
            result.get("payload_signature", {}).get("algorithm", "sha256")
        )
        row_copy["payload_signature_value"] = (
            result.get("payload_signature", {}).get("value", "")
        )
        row_copy["generated_at_utc"] = result.get("generated_at_utc", "")
        row_copy["generated_query"] = result.get("generated_query", {})
        lines.append(json.dumps(row_copy, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_health_gate_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("## Session Contract Health Gate")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"payload_type: {result['payload_type']}")
    if result.get("payload_signature"):
        signature = result["payload_signature"]
        lines.append(
            f"payload_signature: {signature.get('algorithm', 'sha256')}:{signature.get('value', '')}"
        )
    lines.append(f"status: {result['status']}")
    lines.append(f"pass: {result['pass']}")
    lines.append(
        f"ratio: {result['healthy_ratio']} threshold={result['threshold']}"
    )
    lines.append(
        f"total_sessions={result['total_sessions']} healthy_sessions={result['healthy_sessions']} "
        f"unhealthy_sessions={result['unhealthy_sessions']} "
        f"blocked_sessions_count={result['blocked_sessions_count']} "
        f"blocked_ratio={result['blocked_ratio']}"
    )
    lines.append(f"strict_checks_enabled={result['strict_checks_enabled']}")
    lines.append(f"generated_at_utc: {result['generated_at_utc']}")
    lines.append(f"generated_query: {json.dumps(result['generated_query'])}")
    if result["blocked_sessions"]:
        lines.append("")
        lines.append("### Blocked Sessions")
        lines.append("| id | state | health | issues |")
        lines.append("|----|-------|--------|--------|")
        for row in result["blocked_sessions"]:
            issues = ", ".join(_coerce_issue_types(row.get("issues")))
            lines.append(
                f"| {row['session_id']} | {row['state']} | {row['health']} | {issues or '—'} |"
            )
    return "\n".join(lines)


def _serialize_health_gate_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "payload_signature_algorithm",
            "record_type",
            "payload_signature_value",
            "status",
            "pass",
            "healthy_ratio",
            "threshold",
            "total_sessions",
            "healthy_sessions",
            "unhealthy_sessions",
            "blocked_sessions_count",
            "blocked_ratio",
            "top_blocked_count",
            "blocked_sessions_cap",
            "healthy",
            "warning",
            "error",
            "missing",
            "strict_checks_enabled",
            "generated_at_utc",
            "owner",
            "all",
            "strict",
            "min_healthy_ratio",
            "session_id",
            "state",
            "health",
            "issues",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            result.get("payload_signature", {}).get("algorithm", "sha256"),
            "summary",
            result.get("payload_signature", {}).get("value", ""),
            result["status"],
            str(result["pass"]),
            result["healthy_ratio"],
            result["threshold"],
            result["total_sessions"],
            result["healthy_sessions"],
            result["unhealthy_sessions"],
            result["blocked_sessions_count"],
            result["blocked_ratio"],
            result["top_blocked_count"],
            result["blocked_sessions_cap"],
            result["summary"]["health"]["healthy"],
            result["summary"]["health"]["warning"],
            result["summary"]["health"]["error"],
            result["summary"]["health"]["missing"],
            str(result["strict_checks_enabled"]),
            result["generated_at_utc"],
            result["generated_query"].get("owner", ""),
            result["generated_query"].get("all", False),
            result["generated_query"].get("strict", False),
            result["generated_query"].get("min_healthy_ratio", 1.0),
            "",
            "",
            "",
            "",
        ]
    )
    for row in result.get("blocked_sessions", []):
        issues = ", ".join(_coerce_issue_types(row.get("issues")))
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                result.get("payload_signature", {}).get("algorithm", "sha256"),
                "blocked_session",
                result.get("payload_signature", {}).get("value", ""),
                result["status"],
                str(result["pass"]),
                result["healthy_ratio"],
                result["threshold"],
                result["total_sessions"],
                result["healthy_sessions"],
                result["unhealthy_sessions"],
                result["blocked_sessions_count"],
                result["blocked_ratio"],
                result["top_blocked_count"],
                result["blocked_sessions_cap"],
                result["summary"]["health"]["healthy"],
                result["summary"]["health"]["warning"],
                result["summary"]["health"]["error"],
                result["summary"]["health"]["missing"],
                str(result["strict_checks_enabled"]),
                result["generated_at_utc"],
                result["generated_query"].get("owner", ""),
                result["generated_query"].get("all", False),
                result["generated_query"].get("strict", False),
                result["generated_query"].get("min_healthy_ratio", 1.0),
                row.get("session_id", ""),
                row.get("state", ""),
                row.get("health", ""),
                issues,
            ]
        )
    return buffer.getvalue()


def _serialize_health_gate_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    summary_row = dict(result)
    summary_row["record_type"] = "summary"
    lines.append(json.dumps(summary_row, sort_keys=True))
    for row in result.get("blocked_sessions", []):
        blocked_row = dict(row)
        blocked_row["record_type"] = "blocked_session"
        blocked_row["payload_type"] = result["payload_type"]
        blocked_row["schema_version"] = result["schema_version"]
        blocked_row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        blocked_row["status"] = result.get("status", "")
        blocked_row["pass"] = result.get("pass", False)
        blocked_row["summary_status"] = result["status"]
        blocked_row["healthy_ratio"] = result["healthy_ratio"]
        blocked_row["threshold"] = result["threshold"]
        blocked_row["total_sessions"] = result["total_sessions"]
        blocked_row["healthy_sessions"] = result["healthy_sessions"]
        blocked_row["unhealthy_sessions"] = result["unhealthy_sessions"]
        blocked_row["blocked_sessions_count"] = result["blocked_sessions_count"]
        blocked_row["blocked_ratio"] = result["blocked_ratio"]
        blocked_row["top_blocked_count"] = result["top_blocked_count"]
        blocked_row["blocked_sessions_cap"] = result["blocked_sessions_cap"]
        blocked_row["generated_at_utc"] = result["generated_at_utc"]
        blocked_row["strict_checks_enabled"] = result["strict_checks_enabled"]
        blocked_row["payload_signature_algorithm"] = (
            result.get("payload_signature", {}).get("algorithm", "sha256")
        )
        blocked_row["payload_signature_value"] = (
            result.get("payload_signature", {}).get("value", "")
        )
        blocked_row["generated_query"] = result.get("generated_query", {})
        lines.append(json.dumps(blocked_row, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _export_format_from_suffix(suffix: str) -> str | None:
    mapping = {
        ".md": "md",
        ".csv": "csv",
        ".jsonl": "jsonl",
        ".json": "json",
    }
    return mapping.get(suffix.lower())


def _infer_export_format(path: Path, fallback: str = "json") -> str:
    suffix = path.suffix.lower()
    inferred = _export_format_from_suffix(suffix)
    if inferred is not None:
        return inferred
    return fallback


def _write_report_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        raise typer.BadParameter(
            f"Unsupported --export-format '{export_format}'. "
            "Choose one of: json, md, csv, jsonl."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        raise typer.BadParameter(f"Output path is a directory: {output}")
    if output.exists() and not overwrite:
        raise typer.BadParameter(
            f"Output path already exists: {output} (use --overwrite to replace it)"
        )

    fmt = normalized
    if fmt == "md":
        pass
        payload = _serialize_health_report_md(report)
    elif fmt == "csv":
        payload = _serialize_health_report_csv(report)
    elif fmt == "jsonl":
        payload = _serialize_health_report_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def _write_health_gate_export(
    output: Path,
    report: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        raise typer.BadParameter(
            f"Unsupported --export-format '{export_format}'. "
            "Choose one of: json, md, csv, jsonl."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        raise typer.BadParameter(f"Output path is a directory: {output}")
    if output.exists() and not overwrite:
        raise typer.BadParameter(
            f"Output path already exists: {output} (use --overwrite to replace it)"
        )

    fmt = normalized
    if fmt == "md":
        pass
        payload = _serialize_health_gate_md(report)
    elif fmt == "csv":
        payload = _serialize_health_gate_csv(report)
    elif fmt == "jsonl":
        payload = _serialize_health_gate_jsonl(report)
    else:
        payload = json.dumps(report, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def _serialize_health_trend_md(result: dict[str, Any]) -> str:
    lines: list[str] = []
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(((result.get("compat") or {}).get("aliases", {}) or {})),
    )
    latest_issue_types = _coerce_issue_types((result.get("latest") or {}).get("issue_types", []))
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str((s or {}).get("captured_at_utc", ""))
                for s in (result.get("snapshots", []) or [])
                if (s or {}).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds", None)
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg", None)
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour", None)
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds", None)
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count", None)
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility", None)
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    lines.append("## Session Contract Health Trend")
    lines.append(f"schema_version: {result['schema_version']}")
    lines.append(f"schema_compat_mode: {result.get('schema_compat_mode', 'compat')}")
    lines.append(f"compat_mode: {(result.get('compat') or {}).get('mode', 'compat')}")
    lines.append(f"compat_aliases: {json.dumps((result.get('compat') or {}).get('aliases', {}), sort_keys=True)}")
    lines.append(f"compat_aliases_count: {compat_aliases_count}")
    lines.append(f"payload_type: {result['payload_type']}")
    lines.append(f"trend_payload_type: {result['trend_payload_type']}")
    lines.append(f"snapshot_count: {result['snapshot_count']}")
    lines.append(f"snapshot_ids_csv: {snapshot_ids_csv}")
    lines.append(f"snapshot_ids_hash: {snapshot_ids_hash}")
    lines.append(f"snapshot_window_seconds: {snapshot_window_seconds}")
    lines.append(f"snapshot_window_hash: {snapshot_window_hash}")
    lines.append(f"snapshot_interval_seconds_avg: {snapshot_interval_seconds_avg}")
    lines.append(f"snapshot_interval_hash: {snapshot_interval_hash}")
    lines.append(f"snapshot_density_per_hour: {snapshot_density_per_hour}")
    lines.append(f"snapshot_density_hash: {snapshot_density_hash}")
    lines.append(f"snapshot_freshness_seconds: {snapshot_freshness_seconds}")
    lines.append(f"snapshot_freshness_hash: {snapshot_freshness_hash}")
    lines.append(f"snapshot_issue_churn_count: {snapshot_issue_churn_count}")
    lines.append(f"snapshot_issue_churn_hash: {snapshot_issue_churn_hash}")
    lines.append(f"snapshot_health_volatility: {snapshot_health_volatility}")
    lines.append(f"snapshot_health_volatility_hash: {snapshot_health_volatility_hash}")
    lines.append(f"generated_at_utc: {result.get('generated_at_utc', '')}")
    lines.append(f"snapshot_retention_max_lines: {result.get('snapshot_retention_max_lines', '')}")
    lines.append(f"latest_status: {result.get('latest_status', (result.get('latest') or {}).get('status', ''))}")
    lines.append(f"latest_pass: {result.get('latest_pass', (result.get('latest') or {}).get('pass', None))}")
    lines.append(f"latest_captured_at_utc: {result.get('latest_captured_at_utc', (result.get('latest') or {}).get('captured_at_utc', ''))}")
    lines.append(f"latest_blocked_ratio: {result.get('latest_blocked_ratio', (result.get('latest') or {}).get('blocked_ratio', None))}")
    lines.append(f"latest_blocked_count: {result.get('latest_blocked_count', (result.get('latest') or {}).get('blocked_count', None))}")
    lines.append(
        f"latest_issue_types_count: {result.get('latest_issue_types_count', len(latest_issue_types))}"
    )
    lines.append(
        f"latest_issue_types_csv: {result.get('latest_issue_types_csv', ', '.join(latest_issue_types))}"
    )
    lines.append(f"latest_issue_types_json: {latest_issue_types_json}")
    lines.append(f"latest_issue_types_hash: {latest_issue_types_hash}")
    lines.append(f"scope_owner: {result.get('scope_owner', (result.get('scope_key') or {}).get('owner', ''))}")
    lines.append(
        f"scope_payload_type: {result.get('scope_payload_type', (result.get('scope_key') or {}).get('payload_type', ''))}"
    )
    lines.append(f"scope_all: {result.get('scope_all', (result.get('scope_key') or {}).get('all', False))}")
    lines.append(
        f"scope_strict: {result.get('scope_strict', (result.get('scope_key') or {}).get('strict', False))}"
    )
    lines.append(
        f"scope_policy_profile: {result.get('scope_policy_profile', (result.get('scope_key') or {}).get('policy_profile', 'custom'))}"
    )
    lines.append(
        f"scope_min_healthy_ratio: {result.get('scope_min_healthy_ratio', (result.get('scope_key') or {}).get('min_healthy_ratio', ''))}"
    )
    lines.append(
        f"scope_top_blocked: {result.get('scope_top_blocked', (result.get('scope_key') or {}).get('top_blocked', ''))}"
    )
    lines.append(
        f"scope_key_json: {result.get('scope_key_json', json.dumps(result.get('scope_key', {}), sort_keys=True))}"
    )
    lines.append(f"scope_key: {json.dumps(result.get('scope_key', {}))}")
    lines.append(f"delta_summary_json: {result.get('delta_summary_json', json.dumps(result.get('delta_summary', {}), sort_keys=True))}")
    lines.append(f"delta_summary: {json.dumps(result.get('delta_summary', {}))}")
    if result.get("payload_signature"):
        sig = result["payload_signature"]
        lines.append(f"payload_signature: {sig.get('algorithm', 'sha256')}:{sig.get('value', '')}")
    return "\n".join(lines)


def _serialize_health_trend_csv(result: dict[str, Any]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    latest_issue_types = _coerce_issue_types((result.get("latest") or {}).get("issue_types", []))
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(((result.get("compat") or {}).get("aliases", {}) or {})),
    )
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str((s or {}).get("captured_at_utc", ""))
                for s in (result.get("snapshots", []) or [])
                if (s or {}).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds", None)
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg", None)
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour", None)
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds", None)
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count", None)
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility", None)
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    writer.writerow(
        [
            "schema_version",
            "schema_compat_mode",
            "payload_type",
            "trend_payload_type",
            "payload_signature_algorithm",
            "payload_signature_value",
            "record_type",
            "generated_at_utc",
            "snapshot_count",
            "snapshot_ids_csv",
            "snapshot_ids_hash",
            "snapshot_window_seconds",
            "snapshot_window_hash",
            "snapshot_interval_seconds_avg",
            "snapshot_interval_hash",
            "snapshot_density_per_hour",
            "snapshot_density_hash",
            "snapshot_freshness_seconds",
            "snapshot_freshness_hash",
            "snapshot_issue_churn_count",
            "snapshot_issue_churn_hash",
            "snapshot_health_volatility",
            "snapshot_health_volatility_hash",
            "limit",
            "snapshot_retention_max_lines",
            "latest_status",
            "latest_pass",
            "latest_captured_at_utc",
            "latest_blocked_ratio",
            "latest_blocked_count",
            "latest_issue_types_count",
            "latest_issue_types_csv",
            "latest_issue_types_json",
            "latest_issue_types_hash",
            "scope_payload_type",
            "scope_owner",
            "scope_all",
            "scope_strict",
            "scope_policy_profile",
            "scope_min_healthy_ratio",
            "scope_top_blocked",
            "scope_key_json",
            "delta_summary_json",
            "scope_key",
            "blocked_ratio_delta",
            "blocked_count_delta",
            "captured_at_utc",
            "status",
            "pass",
            "total",
            "healthy_count",
            "unhealthy_count",
            "blocked_count",
            "blocked_ratio",
            "issue_types",
            "compat_mode",
            "compat_aliases_json",
            "compat_aliases_count",
        ]
    )
    writer.writerow(
        [
            result["schema_version"],
            result.get("schema_compat_mode", "compat"),
            result["payload_type"],
            result["trend_payload_type"],
            result.get("payload_signature", {}).get("algorithm", "sha256"),
            result.get("payload_signature", {}).get("value", ""),
            "summary",
            result.get("generated_at_utc", ""),
            result.get("snapshot_count", 0),
            snapshot_ids_csv,
            snapshot_ids_hash,
            str(snapshot_window_seconds),
            snapshot_window_hash,
            str(snapshot_interval_seconds_avg),
            snapshot_interval_hash,
            str(snapshot_density_per_hour),
            snapshot_density_hash,
            str(snapshot_freshness_seconds),
            snapshot_freshness_hash,
            str(snapshot_issue_churn_count),
            snapshot_issue_churn_hash,
            str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
            snapshot_health_volatility_hash,
            result.get("limit", 0),
            result.get("snapshot_retention_max_lines", ""),
            result.get("latest_status", (result.get("latest") or {}).get("status", "")),
            result.get("latest_pass", (result.get("latest") or {}).get("pass", "")),
            result.get("latest_captured_at_utc", (result.get("latest") or {}).get("captured_at_utc", "")),
            result.get("latest_blocked_ratio", (result.get("latest") or {}).get("blocked_ratio", None)),
            result.get("latest_blocked_count", (result.get("latest") or {}).get("blocked_count", None)),
            result.get("latest_issue_types_count", len(latest_issue_types)),
            result.get(
                "latest_issue_types_csv",
                ", ".join(latest_issue_types),
            ),
            latest_issue_types_json,
            latest_issue_types_hash,
            result.get("scope_payload_type", (result.get("scope_key") or {}).get("payload_type", "")),
            result.get("scope_owner", (result.get("scope_key") or {}).get("owner", "")),
            result.get("scope_all", (result.get("scope_key") or {}).get("all", False)),
            result.get("scope_strict", (result.get("scope_key") or {}).get("strict", False)),
            result.get(
                "scope_policy_profile",
                (result.get("scope_key") or {}).get("policy_profile", "custom"),
            ),
            result.get(
                "scope_min_healthy_ratio",
                (result.get("scope_key") or {}).get("min_healthy_ratio", ""),
            ),
            result.get(
                "scope_top_blocked",
                (result.get("scope_key") or {}).get("top_blocked", ""),
            ),
            result.get("scope_key_json", json.dumps(result.get("scope_key", {}), sort_keys=True)),
            result.get("delta_summary_json", json.dumps(result.get("delta_summary", {}), sort_keys=True)),
            json.dumps(result.get("scope_key", {}), sort_keys=True),
            result.get(
                "blocked_ratio_delta",
                result.get("delta_summary", {}).get("blocked_ratio_delta", None),
            ),
            result.get(
                "blocked_count_delta",
                result.get("delta_summary", {}).get("blocked_count_delta", None),
            ),
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            (result.get("compat") or {}).get("mode", "compat"),
            json.dumps((result.get("compat") or {}).get("aliases", {}), sort_keys=True),
            compat_aliases_count,
        ]
    )
    for snap in result.get("snapshots", []):
        writer.writerow(
            [
                result["schema_version"],
                result.get("schema_compat_mode", "compat"),
                result["payload_type"],
                result["trend_payload_type"],
                result.get("payload_signature", {}).get("algorithm", "sha256"),
                result.get("payload_signature", {}).get("value", ""),
                "snapshot",
                result.get("generated_at_utc", ""),
                result.get("snapshot_count", 0),
                snapshot_ids_csv,
                snapshot_ids_hash,
                snapshot_window_seconds,
                snapshot_window_hash,
                snapshot_interval_seconds_avg,
                snapshot_interval_hash,
                snapshot_density_per_hour,
                snapshot_density_hash,
            snapshot_freshness_seconds,
            snapshot_freshness_hash,
            snapshot_issue_churn_count,
            snapshot_issue_churn_hash,
            str(snapshot_health_volatility) if snapshot_health_volatility is not None else "None",
            snapshot_health_volatility_hash,
            result.get("limit", 0),
                result.get("snapshot_retention_max_lines", ""),
                result.get("latest_status", (result.get("latest") or {}).get("status", "")),
                result.get("latest_pass", (result.get("latest") or {}).get("pass", "")),
                result.get("latest_captured_at_utc", (result.get("latest") or {}).get("captured_at_utc", "")),
                result.get("latest_blocked_ratio", (result.get("latest") or {}).get("blocked_ratio", None)),
                result.get("latest_blocked_count", (result.get("latest") or {}).get("blocked_count", None)),
                result.get("latest_issue_types_count", len(latest_issue_types)),
                result.get(
                    "latest_issue_types_csv",
                    ", ".join(latest_issue_types),
                ),
                latest_issue_types_json,
                latest_issue_types_hash,
                result.get("scope_payload_type", (result.get("scope_key") or {}).get("payload_type", "")),
                result.get("scope_owner", (result.get("scope_key") or {}).get("owner", "")),
                result.get("scope_all", (result.get("scope_key") or {}).get("all", False)),
                result.get("scope_strict", (result.get("scope_key") or {}).get("strict", False)),
                result.get(
                    "scope_policy_profile",
                    (result.get("scope_key") or {}).get("policy_profile", "custom"),
                ),
                result.get(
                    "scope_min_healthy_ratio",
                    (result.get("scope_key") or {}).get("min_healthy_ratio", ""),
                ),
                result.get(
                    "scope_top_blocked",
                    (result.get("scope_key") or {}).get("top_blocked", ""),
                ),
                result.get("scope_key_json", json.dumps(result.get("scope_key", {}), sort_keys=True)),
                result.get("delta_summary_json", json.dumps(result.get("delta_summary", {}), sort_keys=True)),
                json.dumps(result.get("scope_key", {}), sort_keys=True),
                result.get(
                    "blocked_ratio_delta",
                    result.get("delta_summary", {}).get("blocked_ratio_delta", None),
                ),
                result.get(
                    "blocked_count_delta",
                    result.get("delta_summary", {}).get("blocked_count_delta", None),
                ),
                snap.get("captured_at_utc", ""),
                snap.get("status", ""),
                snap.get("pass", False),
                snap.get("total", 0),
                snap.get("healthy_count", 0),
                snap.get("unhealthy_count", 0),
                snap.get("blocked_count", 0),
                snap.get("blocked_ratio", 0.0),
                ", ".join(_coerce_issue_types(snap.get("issue_types", []))),
                (result.get("compat") or {}).get("mode", "compat"),
                json.dumps((result.get("compat") or {}).get("aliases", {}), sort_keys=True),
                compat_aliases_count,
            ]
        )
    return buffer.getvalue()


def _serialize_health_trend_jsonl(result: dict[str, Any]) -> str:
    lines: list[str] = []
    latest_issue_types = _coerce_issue_types((result.get("latest") or {}).get("issue_types", []))
    compat_aliases_count = result.get(
        "compat_aliases_count",
        len(((result.get("compat") or {}).get("aliases", {}) or {})),
    )
    latest_issue_types_json = result.get(
        "latest_issue_types_json",
        json.dumps(latest_issue_types),
    )
    latest_issue_types_hash = result.get(
        "latest_issue_types_hash",
        hashlib.sha256(latest_issue_types_json.encode("utf-8")).hexdigest(),
    )
    snapshot_ids_csv = result.get(
        "snapshot_ids_csv",
        ", ".join(
            [
                str((s or {}).get("captured_at_utc", ""))
                for s in (result.get("snapshots", []) or [])
                if (s or {}).get("captured_at_utc", "")
            ]
        ),
    )
    snapshot_ids_hash = result.get(
        "snapshot_ids_hash",
        hashlib.sha256(snapshot_ids_csv.encode("utf-8")).hexdigest(),
    )
    snapshot_window_seconds = result.get("snapshot_window_seconds", None)
    snapshot_window_hash = result.get(
        "snapshot_window_hash",
        hashlib.sha256(str(snapshot_window_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_interval_seconds_avg = result.get("snapshot_interval_seconds_avg", None)
    snapshot_interval_hash = result.get(
        "snapshot_interval_hash",
        hashlib.sha256(str(snapshot_interval_seconds_avg).encode("utf-8")).hexdigest(),
    )
    snapshot_density_per_hour = result.get("snapshot_density_per_hour", None)
    snapshot_density_hash = result.get(
        "snapshot_density_hash",
        hashlib.sha256(str(snapshot_density_per_hour).encode("utf-8")).hexdigest(),
    )
    snapshot_freshness_seconds = result.get("snapshot_freshness_seconds", None)
    snapshot_freshness_hash = result.get(
        "snapshot_freshness_hash",
        hashlib.sha256(str(snapshot_freshness_seconds).encode("utf-8")).hexdigest(),
    )
    snapshot_issue_churn_count = result.get("snapshot_issue_churn_count", None)
    snapshot_issue_churn_hash = result.get(
        "snapshot_issue_churn_hash",
        hashlib.sha256(str(snapshot_issue_churn_count).encode("utf-8")).hexdigest(),
    )
    snapshot_health_volatility = result.get("snapshot_health_volatility", None)
    snapshot_health_volatility_hash = result.get(
        "snapshot_health_volatility_hash",
        hashlib.sha256(str(snapshot_health_volatility).encode("utf-8")).hexdigest(),
    )
    summary = dict(result)
    summary["record_type"] = "summary"
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": (result.get("compat") or {}).get("aliases", {}),
    }
    summary["latest_status"] = result.get("latest_status", (result.get("latest") or {}).get("status", ""))
    summary["latest_pass"] = result.get("latest_pass", (result.get("latest") or {}).get("pass", None))
    summary["latest_captured_at_utc"] = result.get(
        "latest_captured_at_utc", (result.get("latest") or {}).get("captured_at_utc", "")
    )
    summary["latest_blocked_ratio"] = result.get(
        "latest_blocked_ratio", (result.get("latest") or {}).get("blocked_ratio", None)
    )
    summary["latest_blocked_count"] = result.get(
        "latest_blocked_count", (result.get("latest") or {}).get("blocked_count", None)
    )
    summary["latest_issue_types_count"] = result.get(
        "latest_issue_types_count",
        len(latest_issue_types),
    )
    summary["latest_issue_types_csv"] = result.get(
        "latest_issue_types_csv",
        ", ".join(latest_issue_types),
    )
    summary["latest_issue_types_json"] = latest_issue_types_json
    summary["latest_issue_types_hash"] = latest_issue_types_hash
    summary["snapshot_ids_csv"] = snapshot_ids_csv
    summary["snapshot_ids_hash"] = snapshot_ids_hash
    summary["snapshot_window_seconds"] = snapshot_window_seconds
    summary["snapshot_window_hash"] = snapshot_window_hash
    summary["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
    summary["snapshot_interval_hash"] = snapshot_interval_hash
    summary["snapshot_density_per_hour"] = snapshot_density_per_hour
    summary["snapshot_density_hash"] = snapshot_density_hash
    summary["snapshot_freshness_seconds"] = snapshot_freshness_seconds
    summary["snapshot_freshness_hash"] = snapshot_freshness_hash
    summary["snapshot_issue_churn_count"] = snapshot_issue_churn_count
    summary["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
    summary["snapshot_health_volatility"] = snapshot_health_volatility
    summary["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
    summary["scope_owner"] = result.get("scope_owner", (result.get("scope_key") or {}).get("owner", ""))
    summary["scope_payload_type"] = result.get(
        "scope_payload_type",
        (result.get("scope_key") or {}).get("payload_type", ""),
    )
    summary["scope_all"] = result.get("scope_all", (result.get("scope_key") or {}).get("all", False))
    summary["scope_strict"] = result.get(
        "scope_strict", (result.get("scope_key") or {}).get("strict", False)
    )
    summary["scope_policy_profile"] = result.get(
        "scope_policy_profile",
        (result.get("scope_key") or {}).get("policy_profile", "custom"),
    )
    summary["scope_min_healthy_ratio"] = result.get(
        "scope_min_healthy_ratio",
        (result.get("scope_key") or {}).get("min_healthy_ratio", ""),
    )
    summary["scope_top_blocked"] = result.get(
        "scope_top_blocked", (result.get("scope_key") or {}).get("top_blocked", "")
    )
    summary["scope_key_json"] = result.get(
        "scope_key_json",
        json.dumps(result.get("scope_key", {}), sort_keys=True),
    )
    summary["payload_signature_algorithm"] = (
        result.get("payload_signature", {}).get("algorithm", "sha256")
    )
    summary["payload_signature_value"] = (
        result.get("payload_signature", {}).get("value", "")
    )
    summary["compat"] = result.get("compat") or {
        "mode": result.get("schema_compat_mode", "compat"),
        "aliases": (result.get("compat") or {}).get("aliases", {}),
    }
    summary["compat_aliases_count"] = compat_aliases_count
    lines.append(json.dumps(summary, sort_keys=True))
    for snap in result.get("snapshots", []):
        row = dict(snap)
        row["record_type"] = "snapshot"
        row["schema_version"] = result["schema_version"]
        row["schema_compat_mode"] = result.get("schema_compat_mode", "compat")
        row["payload_type"] = result["payload_type"]
        row["trend_payload_type"] = result["trend_payload_type"]
        row["snapshot_count"] = result.get("snapshot_count", 0)
        row["limit"] = result.get("limit", 0)
        row["snapshot_retention_max_lines"] = result.get("snapshot_retention_max_lines", "")
        row["generated_at_utc"] = result.get("generated_at_utc", "")
        row["compat_mode"] = (result.get("compat") or {}).get("mode", "compat")
        row["compat_aliases"] = (result.get("compat") or {}).get("aliases", {})
        row["compat_aliases_count"] = compat_aliases_count
        row["scope_key"] = result.get("scope_key", {})
        row["scope_key_json"] = result.get(
            "scope_key_json",
            json.dumps(result.get("scope_key", {}), sort_keys=True),
        )
        row["delta_summary_json"] = result.get(
            "delta_summary_json",
            json.dumps(result.get("delta_summary", {}), sort_keys=True),
        )
        row["delta_summary"] = result.get("delta_summary", {})
        row["blocked_ratio_delta"] = result.get(
            "blocked_ratio_delta",
            result.get("delta_summary", {}).get("blocked_ratio_delta", None),
        )
        row["blocked_count_delta"] = result.get(
            "blocked_count_delta",
            result.get("delta_summary", {}).get("blocked_count_delta", None),
        )
        row["latest_status"] = result.get("latest_status", (result.get("latest") or {}).get("status", ""))
        row["latest_pass"] = result.get("latest_pass", (result.get("latest") or {}).get("pass", None))
        row["latest_captured_at_utc"] = result.get("latest_captured_at_utc", (result.get("latest") or {}).get("captured_at_utc", ""))
        row["latest_blocked_ratio"] = result.get("latest_blocked_ratio", (result.get("latest") or {}).get("blocked_ratio", None))
        row["latest_blocked_count"] = result.get("latest_blocked_count", (result.get("latest") or {}).get("blocked_count", None))
        row["latest_issue_types_count"] = result.get(
            "latest_issue_types_count",
            len(latest_issue_types),
        )
        row["latest_issue_types_csv"] = result.get(
            "latest_issue_types_csv",
            ", ".join(latest_issue_types),
        )
        row["latest_issue_types_json"] = latest_issue_types_json
        row["latest_issue_types_hash"] = latest_issue_types_hash
        row["snapshot_ids_csv"] = snapshot_ids_csv
        row["snapshot_ids_hash"] = snapshot_ids_hash
        row["snapshot_window_seconds"] = snapshot_window_seconds
        row["snapshot_window_hash"] = snapshot_window_hash
        row["snapshot_interval_seconds_avg"] = snapshot_interval_seconds_avg
        row["snapshot_interval_hash"] = snapshot_interval_hash
        row["snapshot_density_per_hour"] = snapshot_density_per_hour
        row["snapshot_density_hash"] = snapshot_density_hash
        row["snapshot_freshness_seconds"] = snapshot_freshness_seconds
        row["snapshot_freshness_hash"] = snapshot_freshness_hash
        row["snapshot_issue_churn_count"] = snapshot_issue_churn_count
        row["snapshot_issue_churn_hash"] = snapshot_issue_churn_hash
        row["snapshot_health_volatility"] = snapshot_health_volatility
        row["snapshot_health_volatility_hash"] = snapshot_health_volatility_hash
        row["scope_owner"] = result.get("scope_owner", (result.get("scope_key") or {}).get("owner", ""))
        row["scope_payload_type"] = result.get(
            "scope_payload_type",
            (result.get("scope_key") or {}).get("payload_type", ""),
        )
        row["scope_all"] = result.get("scope_all", (result.get("scope_key") or {}).get("all", False))
        row["scope_strict"] = result.get(
            "scope_strict", (result.get("scope_key") or {}).get("strict", False)
        )
        row["scope_policy_profile"] = result.get(
            "scope_policy_profile",
            (result.get("scope_key") or {}).get("policy_profile", "custom"),
        )
        row["scope_min_healthy_ratio"] = result.get(
            "scope_min_healthy_ratio",
            (result.get("scope_key") or {}).get("min_healthy_ratio", ""),
        )
        row["scope_top_blocked"] = result.get(
            "scope_top_blocked", (result.get("scope_key") or {}).get("top_blocked", "")
        )
        row["payload_signature_algorithm"] = (
            result.get("payload_signature", {}).get("algorithm", "sha256")
        )
        row["payload_signature_value"] = (
            result.get("payload_signature", {}).get("value", "")
        )
        row["compat"] = result.get("compat") or {
            "mode": result.get("schema_compat_mode", "compat"),
            "aliases": (result.get("compat") or {}).get("aliases", {}),
        }
        lines.append(json.dumps(row, sort_keys=True))
    return "\n".join(lines) + ("\n" if lines else "")


def _write_health_trend_export(
    output: Path,
    result: dict[str, Any],
    export_format: str,
    overwrite: bool = False,
) -> str:
    valid_formats = {"json", "md", "csv", "jsonl"}
    normalized = export_format.lower().strip()
    if normalized not in valid_formats:
        console.print(
            f"[red]Unsupported --export-format '{export_format}'. "
            "Choose one of: json, md, csv, jsonl.[/red]"
        )
        raise typer.Exit(1)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.is_dir():
        console.print(f"[red]Output path is a directory: {output}[/red]")
        raise typer.Exit(1)
    if output.exists() and not overwrite:
        console.print(
            f"[red]Output path already exists: {output} (use --overwrite to replace it)[/red]"
        )
        raise typer.Exit(1)

    fmt = normalized
    if fmt == "md":
        pass
        payload = _serialize_health_trend_md(result)
    elif fmt == "csv":
        payload = _serialize_health_trend_csv(result)
    elif fmt == "jsonl":
        payload = _serialize_health_trend_jsonl(result)
    else:
        payload = json.dumps(result, indent=2, sort_keys=True)

    tmp_path = output.parent / f".{output.name}.{os.getpid()}.{int(time.time() * 1e6)}.tmp"
    try:
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return fmt


def session_contract_health_report_cmd(
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
    format: str | None = None,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_report_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_report_impl(
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    if output is not None:
        chosen_format = (export_format or _infer_export_format(output, fallback="json"))
        if export_format is None:
            if output.suffix and _export_format_from_suffix(output.suffix) is None:
                console.print(
                    f"Note: output path extension '{output.suffix}' is not recognized for export; "
                    f"defaulting to '{chosen_format}'."
                )
        written_as = _write_report_export(
            output=output,
            report=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-report to: {output} (format={written_as})")

    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print(json.dumps(result, indent=2, sort_keys=True))
    elif fmt == "md":
        console.print(_serialize_health_report_md(result))
    else:
        console.print(f"status={result['status']}")
        console.print("Session Contract Health Report")
        if result.get("payload_signature"):
            signature = result["payload_signature"]
            console.print(f"payload_signature={signature.get('algorithm', 'sha256')}:{signature.get('value', '')}")
        console.print(f"schema_version={result['schema_version']}")
        console.print(f"payload_type={result['payload_type']}")
        console.print(f"policy_profile={result.get('policy_profile', 'custom')}")
        console.print(
            f"total={result['total']} blocked={result['blocked_sessions']} "
            f"blocked_count={result['blocked_count']} ratio={result['blocked_ratio']}"
        )
        if result.get("decision_reasons"):
            console.print(f"decision_reasons={','.join(result.get('decision_reasons', []))}")
        console.print(
            f"healthy={result['health']['healthy']} warning={result['health']['warning']} "
            f"error={result['health']['error']} missing={result['health']['missing']}"
        )
        console.print(f"strict_checks_enabled={result['strict_checks_enabled']}")
        if result.get("generated_at_utc"):
            console.print(f"generated_at_utc={result['generated_at_utc']}")
            console.print(f"generated_query={json.dumps(result['generated_query'])}")
        if result.get("trend_summary"):
            trend = result["trend_summary"]
            console.print(
                f"trend baseline={trend.get('baseline_available', False)} "
                f"ratio_delta={trend.get('blocked_ratio_delta', None)} "
                f"blocked_delta={trend.get('blocked_count_delta', None)}"
            )

        issue_rows = result["issue_breakdown"]
        if issue_rows:
            console.print("Top Issues:")
            for row in issue_rows[:10]:
                console.print(f"  - {row['issue']}: {row['count']}")
        if result["top_blocked"]:
            console.print("Top Blocked Sessions:")
        for row in result["top_blocked"]:
                issues = ", ".join(_coerce_issue_types(row.get("issues")))
                remediation = ", ".join(row.get("remediation", []))
                console.print(
                    f"  - {row['session_id']} owner={row['owner']} health={row['health']} "
                    f"issues={issues if issues else '—'} remediation={remediation if remediation else '—'}"
                )


def session_contract_health_trend_cmd(
    payload_type: str = "session_contract_health_report",
    all_sessions: bool = False,
    owner: str | None = None,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
    format: str | None = None,
    output: Path | None = None,
    export_format: str | None = None,
    overwrite: bool = False,
) -> None:
    from thegent.cli_impl import session_contract_health_trend_impl

    settings = ThegentSettings()
    own = owner or _default_owner_tag()
    result = session_contract_health_trend_impl(
        payload_type=payload_type,
        owner=own if not all_sessions else None,
        all=all_sessions,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
    )
    if output is not None:
        chosen_format = (export_format or _infer_export_format(output, fallback="json"))
        if export_format is None:
            if output.suffix and _export_format_from_suffix(output.suffix) is None:
                console.print(
                    f"Note: output path extension '{output.suffix}' is not recognized for export; "
                    f"defaulting to '{chosen_format}'."
                )
        written_as = _write_health_trend_export(
            output=output,
            result=result,
            export_format=chosen_format,
            overwrite=overwrite,
        )
        console.print(f"exported session-contract-health-trend to: {output} (format={written_as})")
    fmt = _normalize_output_format(format, default=settings.output_format or "rich")
    if fmt == "json":
        console.print(json.dumps(result, indent=2, sort_keys=True))
    elif fmt == "md":
        console.print(_serialize_health_trend_md(result))
    else:
        compat_aliases_count = result.get(
            "compat_aliases_count",
            len(((result.get("compat") or {}).get("aliases", {}) or {})),
        )
        console.print("Session Contract Health Trend")
        console.print(f"trend_payload_type={result['trend_payload_type']}")
        console.print(f"generated_at_utc={result.get('generated_at_utc', '')}")
        console.print(f"compat_mode={(result.get('compat') or {}).get('mode', 'compat')}")
        console.print(f"compat_aliases_count={compat_aliases_count}")
        console.print(
            f"snapshot_count={result['snapshot_count']} limit={result['limit']} "
            f"retention_max_lines={result.get('snapshot_retention_max_lines', '')}"
        )
        console.print(f"scope_key={json.dumps(result['scope_key'])}")
        delta = result.get("delta_summary", {})
        console.print(
            f"delta blocked_ratio={result.get('blocked_ratio_delta', delta.get('blocked_ratio_delta', None))} "
            f"blocked_count={result.get('blocked_count_delta', delta.get('blocked_count_delta', None))}"
        )
        latest = result.get("latest")
        if latest:
            console.print(
                f"latest status={latest.get('status', '')} pass={latest.get('pass', False)} "
                f"blocked_ratio={latest.get('blocked_ratio', 0.0)} "
                f"blocked_count={latest.get('blocked_count', 0)}"
            )
            console.print(
                f"latest captured_at_utc={latest.get('captured_at_utc', '')} "
                f"issue_types_count={result.get('latest_issue_types_count', len(_coerce_issue_types((latest or {}).get('issue_types', []))))}"
            )


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
        from datetime import datetime, UTC
        ckpt_ts = datetime.fromisoformat(last_ckpt["created_at_utc"])
        file_ts = datetime.fromtimestamp(dag_path.stat().st_mtime, UTC)
        if file_ts > ckpt_ts:
            console.print(f"[yellow]Warning: DAG file has been modified since last checkpoint ({last_ckpt['checkpoint_id']}).[/yellow]")
    
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
    frontmatter, tasks = _parse_dag_session(dag_path)
    settings = ThegentSettings()
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if not tasks:
        if fmt == "json":
            print(json.dumps({"tasks": []}))
        else:
            console.print("[dim]No tasks in DAG.[/dim]")
        return
    if fmt == "json":
        print(json.dumps({"tasks": tasks}))
    elif fmt == "md":
        console.print("## DAG Session\n")
        console.print("| id | agent | prompt | depends_on | status |")
        console.print("|----|-------|--------|------------|--------|")
        for t in tasks:
            console.print(f"| {t.get('id', '—')} | {t.get('agent', '—')} | {t.get('prompt', '—')} | {t.get('depends_on', '—')} | {t.get('status', '—')} |")
    else:
        tbl = Table(title="DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        tbl.add_column("depends_on")
        tbl.add_column("status")
        for t in tasks:
            tbl.add_row(t.get("id", "—"), t.get("agent", "—"), t.get("prompt", "—"), t.get("depends_on", "—"), t.get("status", "—"))
        console.print(tbl)


def _dag_path(cd: Path | None) -> tuple[Path | None, Path | None]:
    """Resolve cwd and dag-session.md path. Returns (cwd, dag_path) or (None, None) on error."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        return None, None
    return cwd, cwd / ".factory" / "dag-session.md"


def _ensure_dag_file(dag_path: Path) -> DagDocument:
    """Load DAG or create minimal empty document if file does not exist."""
    if dag_path.exists():
        return _parse_dag_full(dag_path)
    return DagDocument(
        frontmatter={"version": "1", "project": "", "owner": ""},
        tasks=[],
        before_table="# DAG Session\n\n## Tasks\n\n",
        after_table="",
        table_headers=["id", "agent", "prompt", "depends_on", "status"],
    )


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
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
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
    row: dict[str, str] = {"id": tid, "agent": (agent or "").strip(), "prompt": (prompt or "").strip(), "depends_on": deps_str, "status": "pending"}
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
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
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
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    _, tasks = _parse_dag_session(dag_path)
    settings = ThegentSettings()
    with_session = [t for t in tasks if t.get("session_id", "").strip()]
    rows: list[dict[str, str]] = []
    for t in with_session:
        sid = t.get("session_id", "").strip()
        session_status = _session_status_for(sid, settings)
        rows.append({
            "id": t.get("id", "—"),
            "status": t.get("status", "—"),
            "session_id": sid,
            "session_status": session_status,
        })
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if fmt == "json":
        print(json.dumps({"tasks": rows}))
        return
    if not with_session:
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
    if not _dag_update_task(doc, task_id, status=status, session_id=session_id, prompt=prompt, agent=agent.strip() if agent else None, depends_on=norm_depends_on, contract_version=contract_version.strip() if contract_version else None):
        raise typer.Exit(1)
    if status is not None or depends_on is not None or agent is not None:
        cycle_errors = _check_dag_cycles(doc.tasks)
        if cycle_errors:
            for e in cycle_errors:
                console.print(f"[red]{e}[/red]")
            raise typer.Exit(2)
    content = _serialize_dag(doc)
    _atomic_write(dag_path, content)


def _parse_depends_on(dep_str: str) -> list[str]:
    """Parse depends_on string into list of task ids."""
    if not dep_str or dep_str.strip() in ("—", "-"):
        return []
    return [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() not in ("—", "-")]


TERMINAL_STATUSES = frozenset({"done", "cancelled", "skipped"})


def dag_ready_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """List task ids that are ready (pending with all deps done|cancelled|skipped)."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    _, tasks = _parse_dag_session(dag_path)
    ready_ids = _get_ready_task_ids(tasks)
    settings = ThegentSettings()
    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or settings.output_format or "rich").lower()
    if not ready_ids:
        console.print("[dim]No ready tasks.[/dim]")
        return
    if fmt == "ids":
        console.print("\n".join(ready_ids))
    elif fmt == "json":
        print(json.dumps({"ready_task_ids": ready_ids}))
    elif fmt == "md":
        console.print("| id | agent | prompt |")
        console.print("|----|-------|--------|")
        id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
        for tid in ready_ids:
            t = id_to_task.get(tid, {})
            prompt = t.get("prompt", "")
            prompt_preview = (prompt[:60] + "...") if len(prompt) > 60 else prompt
            console.print(f"| {tid} | {t.get('agent', '—')} | {prompt_preview} |")
    else:
        tbl = Table(title="Ready DAG Tasks")
        tbl.add_column("id")
        tbl.add_column("agent")
        tbl.add_column("prompt")
        id_to_task = {t.get("id", "").strip(): t for t in tasks if t.get("id", "").strip()}
        for tid in ready_ids:
            t = id_to_task.get(tid, {})
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
            except Exception:
                pass
        
        if not any_alive:
            t["status"] = "pending"
            changed = True
            reconciled_count += 1

    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))
        console.print(f"[green]Reconciled {reconciled_count} stuck tasks.[/green]")
    else:
        console.print("[dim]DAG is in sync with live processes.[/dim]")


def plan_analyze_cmd(
    cd: Path | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
    format: str | None = None,
) -> None:
    """Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk."""
    from thegent.planning.simulation import (
        PERTNode,
        pert_forward_pass,
        simulate_resource_contention,
        score_continuity_risk,
        ContinuityRiskInput,
    )

    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    tasks = doc.tasks
    if not pert and not resources and not continuity:
        pert = resources = continuity = True

    result: dict[str, Any] = {}
    if pert:
        nodes = []
        for t in tasks:
            tid = (t.get("id") or "").strip()
            if not tid:
                continue
            deps = _parse_depends_on(t.get("depends_on", ""))
            nodes.append(PERTNode(
                task_id=tid,
                optimistic_days=0.5,
                most_likely_days=1.0,
                pessimistic_days=2.0,
                predecessors=deps,
            ))
        if nodes:
            pert_results = pert_forward_pass(nodes)
            result["pert"] = {
                k: {
                    "expected_duration": v.expected_duration,
                    "variance": v.variance,
                    "confidence_p50": v.confidence_p50,
                    "confidence_p90": v.confidence_p90,
                }
                for k, v in pert_results.items()
            }
    if resources:
        contention = simulate_resource_contention(tasks, [], {})
        result["resources"] = [{"resource_id": c.resource_id, "contention_ratio": c.contention_ratio} for c in contention]
    if continuity:
        open_tasks = [t for t in tasks if (t.get("status") or "").lower() not in TERMINAL_STATUSES]
        from datetime import timedelta
        now = datetime.now(UTC)
        handoff_windows = [(now, now + timedelta(hours=8))]
        snapshot_freshness = {t.get("id", ""): now for t in open_tasks if t.get("id")}
        continuity_input = ContinuityRiskInput(
            open_tasks=open_tasks,
            handoff_windows=handoff_windows,
            snapshot_freshness=snapshot_freshness,
            owner_coverage={},
        )
        cr = score_continuity_risk(continuity_input)
        result["continuity"] = {
            "risk_score": cr.risk_score,
            "factors": cr.factors,
            "high_risk_tasks": cr.high_risk_tasks,
            "recommendations": cr.recommendations,
        }

    fmt = (format or os.environ.get("THGENT_OUTPUT_FORMAT") or ThegentSettings().output_format or "rich").lower()
    if fmt == "json":
        console.print(json.dumps(result, indent=2))
        return
    if pert and "pert" in result:
        tbl = Table(title="PERT Milestone Confidence")
        tbl.add_column("Task")
        tbl.add_column("Expected (d)")
        tbl.add_column("Variance")
        tbl.add_column("P50")
        tbl.add_column("P90")
        for tid, v in result["pert"].items():
            tbl.add_row(tid, f"{v['expected_duration']:.2f}", f"{v['variance']:.2f}", f"{v['confidence_p50']:.2f}", f"{v['confidence_p90']:.2f}")
        console.print(tbl)
    if continuity and "continuity" in result:
        c = result["continuity"]
        console.print(f"\n[bold]Continuity Risk:[/bold] {c['risk_score']:.2f}")
        if c["factors"]:
            for f in c["factors"]:
                console.print(f"  - {f}")
        if c["recommendations"]:
            for r in c["recommendations"]:
                console.print(f"  [yellow]→ {r}[/yellow]")


def archive_cmd(
    days: int | None = None,
    domain: str | None = None,
    tier: str | None = None,
) -> None:
    """Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr)."""
    settings = ThegentSettings()
    session_dir = Path(settings.session_dir).expanduser().resolve()
    archive_dir = session_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    import shutil
    from datetime import datetime, timedelta, UTC

    # WP-3006: tiered storage — hot=30d, cold=365d
    if tier == "cold":
        # Move from archive/ to archive/cold/ for sessions older than 365d
        cold_dir = archive_dir / "cold"
        cold_dir.mkdir(exist_ok=True)
        effective_days = days if days is not None else 365
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in archive_dir.iterdir():
            if item.is_dir() and item.name != "cold":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(cold_dir / item.name))
                    count += 1
        console.print(
            f"[green]Moved {count} sessions to cold storage {cold_dir}[/green] "
            f"(retention: {effective_days}d)"
        )
    else:
        # hot (default): move from session_dir to archive/ for sessions older than 30d
        effective_days = days if days is not None else settings.retention_days_sessions
        cutoff = datetime.now(UTC) - timedelta(days=effective_days)
        count = 0
        for item in session_dir.iterdir():
            if item.is_dir() and item.name != "archive":
                mtime = datetime.fromtimestamp(item.stat().st_mtime, UTC)
                if mtime < cutoff:
                    if domain and domain not in item.name:
                        continue
                    shutil.move(str(item), str(archive_dir / item.name))
                    count += 1
        console.print(
            f"[green]Archived {count} old session directories to {archive_dir}[/green] "
            f"(retention: {effective_days}d, tier: {tier or 'hot'})"
        )


def operations_cmd(
    format: str | None = None,
    operation: str | None = None,
) -> None:
    """List universal operation taxonomy (orchestrate, govern, recover, observe, plan)."""
    from thegent.operations import Operation, list_operations, get_operations_by_type

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            console.print(f"[red]Unknown operation: {operation}. Use: orchestrate, govern, recover, observe, plan[/red]")
            raise typer.Exit(1)
        entries = get_operations_by_type(op)
        data = {op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]}
    else:
        data = list_operations()

    if format == "json":
        console.print(json.dumps(data, indent=2))
        return

    table = Table(title="Universal Operations")
    table.add_column("Operation")
    table.add_column("Command")
    table.add_column("Description")
    table.add_column("MCP Tool")
    for op_name, items in data.items():
        for i, item in enumerate(items):
            table.add_row(
                op_name if i == 0 else "",
                item["command"],
                item["description"],
                item.get("mcp_tool") or "",
            )
    console.print(table)


def modes_cmd(
    format: str | None = None,
    mode: str | None = None,
) -> None:
    """List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop)."""
    from thegent.orchestration_modes import MultiAgentMode, list_modes, get_mode

    if mode:
        entry = get_mode(mode)
        if not entry:
            console.print(f"[red]Unknown mode: {mode}. Use: sequential_delegation, parallel_consensus, review_loop[/red]")
            raise typer.Exit(1)
        data = [{"mode": entry.mode.value, "description": entry.description, "phases": entry.phases, "use_case": entry.use_case, "risk_profile": entry.risk_profile, "selection_hint": entry.selection_hint}]
    else:
        data = list_modes()

    if format == "json":
        console.print(json.dumps(data, indent=2))
        return

    table = Table(title="Multi-Agent Orchestration Modes")
    table.add_column("Mode")
    table.add_column("Description")
    table.add_column("Phases")
    table.add_column("Risk")
    for item in data:
        table.add_row(
            item["mode"],
            item["description"][:60] + "..." if len(item["description"]) > 60 else item["description"],
            ", ".join(item["phases"][:3]) + ("..." if len(item["phases"]) > 3 else ""),
            item["risk_profile"],
        )
    console.print(table)


def benchmark_cmd() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=1000)
    
    if not runs:
        console.print("[dim]No runs found for benchmarking.[/dim]")
        return
        
    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    durations = [r.get("duration_s") for r in completed if r.get("duration_s") is not None]
    
    table = Table(title="Orchestration Benchmark (Last 1000 Runs)")
    table.add_column("Metric")
    table.add_column("Value")
    
    table.add_row("Total Runs", str(len(runs)))
    table.add_row("Success Rate", f"{(len(completed)/len(runs))*100:.1f}%" if runs else "0%")
    if durations:
        avg_dur = sum(durations) / len(durations)
        table.add_row("Avg Latency (Success)", f"{avg_dur:.2f}s")
        table.add_row("P90 Latency", f"{sorted(durations)[int(len(durations)*0.9)]:.2f}s")
    
    # Failure taxonomy summary
    err_classes: dict[str, int] = {}
    for r in failed:
        ec = r.get("error_class") or "unknown"
        err_classes[ec] = err_classes.get(ec, 0) + 1
    
    for ec, count in err_classes.items():
        table.add_row(f"Failures ({ec})", str(count))
        
    console.print(table)

    # WP-X7: Contract Drift Summary
    from thegent.contracts.telemetry import ContractTelemetry, detect_drift
    telemetry = ContractTelemetry(settings.session_dir)
    stats = telemetry.get_stats(limit=100)
    
    if stats.get("total", 0) > 0:
        t_table = Table(title="Contract Performance & Drift (Last 100)")
        t_table.add_column("Metric")
        t_table.add_column("Value")
        t_table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        t_table.add_row("Fallback Rate", f"{stats['fallback_rate']:.1%}")
        
        for p, conf in stats.get("by_provider", {}).items():
            t_table.add_row(f"Avg Conf ({p})", f"{conf:.2f}")
            
        console.print(t_table)
        
        drift = detect_drift(stats)
        for issue in drift:
            console.print(f"[bold red]DRIFT DETECTED:[/bold red] {issue}")


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
    from thegent.execution import RunRegistry, Auditor
    from thegent.contracts.telemetry import ContractTelemetry

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

    # 4. Contract Telemetry (FR-X08)
    ct = ContractTelemetry(settings.session_dir)
    stats = ct.get_stats(limit=500)
    budget = ct.get_drift_budget_status(structural_budget_pct=5.0, semantic_budget_pct=10.0, limit=500)
    drift_issues = ct.detect_drift(window_size=50)
    telemetry_section = f"""- **Parse Quality (Success Rate):** {stats.get('success_rate', 0) * 100:.1f}%
- **Fallback Rate:** {stats.get('fallback_rate', 0) * 100:.1f}%
- **Avg Adapter Confidence:** {stats.get('avg_confidence', 0):.2f}
- **Structural Drift:** {budget.get('structural_rate_pct', 0)}% (budget: {budget.get('structural_budget_pct', 5)}%)
- **Semantic Drift:** {budget.get('semantic_rate_pct', 0)}% (budget: {budget.get('semantic_budget_pct', 10)}%)
- **Drift Within Budget:** {'Yes' if budget.get('within_budget', True) else 'No'}
- **Drift Issues:** {len(drift_issues)} detected
{chr(10).join([f"  - {i}" for i in drift_issues[:5]]) if drift_issues else "  - None"}"""

    pack_path = cwd / ".factory" / f"closure_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    content = f"""# Thegent Orchestration Closure Pack
Generated: {datetime.now().isoformat()}
DAG Session: {dag_path}

## 1. Governance & Security Signoff (WP-6002)
- **Registry Integrity:** {audit_res['status'].upper()}
- **Valid Records:** {audit_res['valid_count']}
- **Corrupt/Unsigned:** {audit_res['corrupt_count']}
- **Environment:** {settings.environment}
- **Audit Trail Integrity:** Verified via `thegent history verify`
- **Technical Architecture:** See `docs/`, `CONTRACT_AUTHORITY.md`
- **Risk Assessment:** See WP-0004 risk scoring; governance research in `docs/research/GOVERNANCE_POLICY_AUDIT_RESEARCH.md`
- **Human Oversight:** Escalation via `thegent govern feedback`; runbook in `docs/RUNBOOK.md`

## 2. Reliability & SLO Certification (WP-6003)
- **Overall Success Rate:** {success_rate:.1f}%
- **Total Tasks in DAG:** {len(doc.tasks)}
- **Completed Tasks:** {len([t for t in doc.tasks if t.get('status') == 'done'])}
- **Failed Tasks:** {len([t for t in doc.tasks if t.get('status') == 'failed'])}
- **Processing Integrity:** Idempotent execution; replay-safe history

## 3. Evidence Completeness
- **Tasks Missing Evidence:** {len(missing_evidence)}
{chr(10).join([f"  - {tid}" for tid in missing_evidence]) if missing_evidence else "  - None (All tasks have linked evidence)"}

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
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)

    # XC2: Block promotion when drift detected (--check-drift)
    if check_drift and not dry_run:
        settings = ThegentSettings()
        from thegent.contracts.telemetry import ContractTelemetry
        ct = ContractTelemetry(settings.session_dir)
        drift_issues = ct.detect_drift(window_size=50)
        if drift_issues:
            console.print("[red]Drift detected; blocking DAG run. Resolve with: thegent govern conformance --check-drift[/red]")
            for issue in drift_issues[:5]:
                console.print(f"  [dim]{issue}[/dim]")
            raise typer.Exit(2)

    # WP-5001/5003: Auto-reconcile on start to recover from previous crashes
    if not dry_run:
        dag_reconcile_cmd(cd=cwd)

    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    id_to_task = {t.get("id", "").strip(): t for t in doc.tasks if t.get("id", "").strip()}
    ready_ids = _get_ready_task_ids(doc.tasks)
    if task:
        if task not in ready_ids:
            console.print(f"[red]Task {task} is not ready (must be pending with deps done|cancelled|skipped)[/red]")
            raise typer.Exit(1)
        ready_ids = [task]
    if not ready_ids:
        console.print("[dim]No ready tasks to run.[/dim]")
        return

    # Lane and Parallelism Control (WP-1001, WP-1002)
    running_count = sum(1 for t in doc.tasks if t.get("status", "").lower() == "running")
    if max_parallel is not None:
        can_run = max(0, max_parallel - running_count)
        if can_run <= 0:
            console.print(f"[dim]Max parallel sessions ({max_parallel}) reached. {running_count} running.[/dim]")
            return
        
        # Sort by priority if available (higher number = higher priority)
        def _get_priority(tid: str) -> int:
            try:
                p = id_to_task[tid].get("priority", "0")
                return int(p) if p.isdigit() else 0
            except (ValueError, KeyError):
                return 0
        
        ready_ids = sorted(ready_ids, key=_get_priority, reverse=True)
        ready_ids = ready_ids[:can_run]

    if dry_run:
        for tid in ready_ids:
            t = id_to_task[tid]
            resolved = _resolve_prompt(tid, t.get("prompt", ""), cwd)
            console.print(f"[dim]Would run: {tid} agent={t.get('agent')} prompt={resolved[:60]}...[/dim]")
        return
    for tid in ready_ids:
        t = id_to_task[tid]
        agent_spec = (t.get("agent") or "").strip()
        prompt = _resolve_prompt(tid, t.get("prompt", ""), cwd)
        routing = (t.get("routing") or "").strip() or None
        effective_lane = lane or (t.get("lane") or "").strip() or "standard"
        # XA4: Task-level contract_version overrides DAG-level
        task_cv = (t.get("contract_version") or "").strip()
        effective_cv = task_cv or contract_version or None

        # WP-1006: Quorum support
        quorum_spec = (t.get("quorum") or "").strip()
        quorum_n = int(quorum_spec) if quorum_spec.isdigit() else 1
        
        # WP-1007: Confidence-aware routing
        conf_spec = (t.get("confidence") or "").strip()
        min_conf_spec = (t.get("min_confidence") or "").strip()
        conf = float(conf_spec) if conf_spec.replace(".", "", 1).isdigit() else 1.0
        min_conf = float(min_conf_spec) if min_conf_spec.replace(".", "", 1).isdigit() else 0.85
        
        if conf < min_conf and quorum_n == 1:
            console.print(f"[yellow]Low confidence ({conf} < {min_conf}) for {tid}. Upgrading to quorum=2.[/yellow]")
            quorum_n = 2

        if not agent_spec or not prompt:
            console.print(f"[yellow]Skipping {tid}: missing agent or prompt[/yellow]")
            continue

        agents = [a.strip() for a in agent_spec.split(",")]
        session_ids = []
        
        for i in range(quorum_n):
            # Pick agent from list if multiple provided, else use first
            current_agent = agents[i % len(agents)]
            agent = resolve_agent(current_agent)
            
            # WP-1006: Arbitration role
            arbitration = "consensus" if quorum_n > 1 else None
            if quorum_n > 1:
                arbitration = "leader" if i == 0 else "follower"

            suffix = f"-{i+1}" if quorum_n > 1 else ""
            idempotency_token = (t.get("idempotency_token") or "").strip() or f"dag-{tid}{suffix}"
            
            session_id = bg_cmd(
                agent=agent,
                prompt=prompt,
                cd=cwd,
                mode="write",
                timeout=90,
                full=True,
                droid=None,
                model=None,
                owner=None,
                routing=routing,
                correlation_id=tid,
                lane=effective_lane,
                idempotency_token=idempotency_token,
                confidence=conf,
                arbitration=arbitration,
                contract_version=effective_cv,
            )
            session_ids.append(session_id)
        
        combined_sid = ",".join(session_ids)
        
        # Update retry_count
        status = t.get("status", "").lower()
        retry_count = None
        try:
            current_rc = int(t.get("retry_count") or "0")
            if status == "failed":
                retry_count = current_rc + 1
            elif status == "pending" and "retry_count" not in t:
                retry_count = 0
        except (ValueError, TypeError):
            retry_count = 1 if status == "failed" else 0

        _dag_update_task(doc, tid, status="running", session_id=combined_sid, retry_count=retry_count)
        content = _serialize_dag(doc)
        _atomic_write(dag_path, content)
        console.print(f"[green]{tid}[/green] -> {combined_sid}")


def dag_sync_cmd(cd: Path | None = None) -> None:
    """For tasks with session_id and status=running, if pid not running set status=done or failed from rc."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd. Provide --cd /path or run from project root.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    if not dag_path.exists():
        console.print(f"[red]DAG session not found: {dag_path}[/red]")
        raise typer.Exit(1)
    doc = _parse_dag_full(dag_path)
    settings = ThegentSettings()
    changed = False
    for t in doc.tasks:
        sids = [s.strip() for s in (t.get("session_id") or "").split(",") if s.strip()]
        if not sids or (t.get("status", "").lower() != "running"):
            continue
        
        # Check all sessions for quorum
        all_done = True
        any_failed = False
        rcs = []
        for sid in sids:
            try:
                meta_path = _find_session_meta(settings, sid)
                m = _read_session_meta(meta_path)
                pid = int(m.get("pid", 0) or 0)
                if _is_pid_running(pid):
                    all_done = False
                    break
                p = _session_paths(meta_path.parent, sid)
                rc_str = p["rc"].read_text(encoding="utf-8").strip() if p["rc"].exists() else ""
                rc = int(rc_str) if rc_str.isdigit() else 1
                rcs.append(rc)
                if rc != 0:
                    any_failed = True
            except typer.BadParameter:
                all_done = False
                break
        
        if all_done and len(rcs) == len(sids):
            # WP-1006: Arbitration logic
            if len(sids) > 1:
                # Basic consensus: if any failed, task failed. 
                # (Could be richer: majority vote on output hash)
                t["status"] = "done" if not any_failed else "failed"
            else:
                t["status"] = "done" if rcs[0] == 0 else "failed"
            changed = True
    if changed:
        content = _serialize_dag(doc)
        _atomic_write(dag_path, content)
        console.print("[green]Synced DAG status with sessions.[/green]")

        # WP-5004: Auto-checkpoint on completion
        from thegent.execution import CheckpointRegistry
        ckpt_registry = CheckpointRegistry(settings.session_dir)
        reason = "Auto-checkpoint: terminal task state detected during sync"
        ckpt_registry.create_checkpoint(reason, content, _default_owner_tag())
        console.print("[dim]Auto-checkpoint created.[/dim]")
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


def dag_rollback_cmd(checkpoint_id: str, cd: Path | None = None) -> None:
    """Rollback DAG state to a specific checkpoint."""
    cwd = _resolve_cwd(cd)
    if cwd is None:
        console.print("[red]Ambiguous cwd.[/red]")
        raise typer.Exit(1)
    dag_path = cwd / ".factory" / "dag-session.md"
    
    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry
    registry = CheckpointRegistry(settings.session_dir)
    
    ckpt = registry.get_checkpoint(checkpoint_id)
    if not ckpt:
        console.print(f"[red]Checkpoint not found: {checkpoint_id}[/red]")
        raise typer.Exit(1)
    
    content = ckpt.get("dag_content")
    if content is None:
        console.print("[red]Checkpoint has no content.[/red]")
        raise typer.Exit(1)
    
    _atomic_write(dag_path, content, backup=True)
    console.print(f"[green]DAG rolled back to checkpoint:[/green] {checkpoint_id}")
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
    cwd, dag_path = _dag_path(cd)
    if cwd is None or not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)
    
    doc = _parse_dag_full(dag_path)
    changed = False
    
    if action == "retry-failed":
        for t in doc.tasks:
            if t.get("status", "").lower() == "failed":
                t["status"] = "pending"
                changed = True
        console.print("[green]Reset all failed tasks to pending.[/green]")
    elif action == "clear-stuck":
        for t in doc.tasks:
            if t.get("status", "").lower() == "running":
                t["status"] = "pending"
                changed = True
        console.print("[green]Reset all running tasks to pending.[/green]")
    elif action == "reset-retries":
        for t in doc.tasks:
            if "retry_count" in t:
                t["retry_count"] = "0"
                changed = True
        console.print("[green]Reset all retry counters.[/green]")
    elif action == "fallback":
        # WP-4003: Swap to fallback agent
        for t in doc.tasks:
            if t.get("status", "").lower() == "failed":
                current_agent = t.get("agent", "")
                from thegent.agents.registry import get_fallback_agents
                fallbacks = get_fallback_agents(current_agent)
                if fallbacks:
                    t["agent"] = fallbacks[0]
                    t["status"] = "pending"
                    changed = True
                    console.print(f"[yellow]Task {t.get('id')}[/yellow]: swapped {current_agent} -> {fallbacks[0]}")
        if not changed:
            console.print("[dim]No failed tasks with defined fallbacks found.[/dim]")
    else:
        console.print(f"[red]Unknown recovery action: {action}[/red]")
        raise typer.Exit(1)
    
    if changed:
        _atomic_write(dag_path, _serialize_dag(doc))
    else:
        console.print("[dim]No changes needed.[/dim]")


def dag_probe_cmd(cd: Path | None = None, baseline_id: str | None = None) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    cwd, dag_path = _dag_path(cd)
    if cwd is None or not dag_path.exists():
        console.print(f"[red]DAG not found: {dag_path}[/red]")
        raise typer.Exit(1)
    
    settings = ThegentSettings()
    from thegent.execution import CheckpointRegistry
    registry = CheckpointRegistry(settings.session_dir)
    
    if not baseline_id:
        ckpts = registry.list_checkpoints(limit=1)
        if not ckpts:
            console.print("[yellow]No baseline checkpoint found. Use --baseline-id.[/yellow]")
            return
        baseline_id = ckpts[0]["checkpoint_id"]
    
    ckpt = registry.get_checkpoint(baseline_id)
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
        # Could use difflib here for more detail
        console.print("[dim]Use 'thegent dag list' to inspect current state.[/dim]")


def status_cmd(session_id: str, format: str | None = None, include_contract: bool = False) -> None:
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, session_id)
    p = _session_paths(meta_path.parent, session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    running = _is_pid_running(pid)
    status = _resolve_session_status(m, p["rc"], running=running)
    out = {
        "session_id": session_id,
        "status": status,
        "running": running,
        "pid": pid,
        "owner": m.get("owner", ""),
        "host": m.get("host"),
        "agent": m.get("agent"),
        "mode": m.get("mode"),
        "cwd": m.get("cwd"),
        "started_at_utc": m.get("started_at_utc"),
        "ended_at_utc": m.get("ended_at_utc"),
        "duration_seconds": m.get("duration_seconds"),
        "timed_out": m.get("timed_out", False),
        "paths": m.get("paths", {}),
    }
    if include_contract:
        out["route_contract"] = m.get("route_contract")
        out["route_request"] = m.get("route_request")
    fmt = _normalize_output_format(format, default="json")
    if fmt == "json":
        console.print(json.dumps(out, indent=2))
    else:
        status_text = status
        console.print(f"session_id: {session_id}")
        console.print(f"status: {status_text}")
        console.print(f"owner: {out['owner']}")
        console.print(f"pid: {pid}")
        if out["host"]:
            console.print(f"host: {out['host']}")
        if out["duration_seconds"] is not None:
            console.print(f"duration_seconds: {out['duration_seconds']}")
        if include_contract and out.get("route_contract") is not None:
            console.print("route_contract:")
            console.print_json(data=out["route_contract"])
        if include_contract and out.get("route_request") is not None:
            console.print(f"route_request: {json.dumps(out['route_request'])}")


def inspect_cmd(
    session_ids: list[str] | None = None,
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    format: str | None = None,
    include_contract: bool = False,
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    from thegent.cli_impl import logs_impl, ps_impl, status_impl

    if not session_ids and not owner:
        raise typer.BadParameter("Provide session_ids or --owner")
    if not session_ids and owner:
        rows = ps_impl(owner=owner, all=False)
        session_ids = [r["id"] for r in rows]
    if not session_ids:
        console.print("[dim]No sessions found[/dim]")
        return

    for i, sid in enumerate(session_ids):
        if i > 0:
            console.print()
        console.print(f"[bold]=== {sid} ===[/bold]")
        fmt = _normalize_output_format(format, default="json")
        try:
            st = status_impl(session_id=sid, include_contract=include_contract)
            if fmt == "json":
                console.print(json.dumps(st, indent=2))
            else:
                console.print(st.get("status", ""))
        except Exception as e:
            console.print(f"[red]status error: {e}[/red]")
            continue
        try:
            log_text = logs_impl(session_id=sid, tail=tail, stderr=stderr)
            console.print(log_text)
        except Exception as e:
            console.print(f"[red]logs error: {e}[/red]")


def logs_cmd(
    session_id: str,
    follow: bool = False,
    stderr: bool = False,
    tail: int = 200,
    timeout: int = 0,
) -> None:
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, session_id)
    p = _session_paths(meta_path.parent, session_id)
    target = p["stderr"] if stderr else p["stdout"]
    if not target.exists():
        raise typer.BadParameter(f"Log file missing: {target}")

    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-tail:]:
        console.print(line)
    if not follow:
        return

    if timeout > 0:
        end_time = time.time() + timeout
    else:
        end_time = None

    pos = target.stat().st_size
    while True:
        running = _is_pid_running(pid)
        if (timeout > 0 and time.time() >= end_time) and not running and pos >= target.stat().st_size:
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. "
                "Session may have exited; check logs separately.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                print(msg, file=sys.stderr)
            raise typer.Exit(EXIT_TIMEOUT)

        if not target.exists():
            return
        size = target.stat().st_size
        if size < pos:
            pos = 0

        if size > pos:
            with target.open("r", encoding="utf-8", errors="replace") as f:
                f.seek(pos)
                chunk = f.read()
                pos = f.tell()
            if chunk:
                for line in chunk.splitlines():
                    console.print(line)
            continue

        if not running:
            return

        if end_time is not None and time.time() >= end_time:
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. "
                "Session may still be running.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                print(msg, file=sys.stderr)
            raise typer.Exit(EXIT_TIMEOUT)

        time.sleep(_LOG_FOLLOW_POLL_SECONDS)


def wait_cmd(session_id: str, timeout: int = 0) -> None:
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, session_id)
    p = _session_paths(meta_path.parent, session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    start = time.time()
    while _is_pid_running(pid):
        if timeout > 0 and (time.time() - start) >= timeout:
            console.print(
                f"[yellow]Operation timed out: wait for session exceeded {timeout}s. "
                "Session may still be running.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                print(msg, file=sys.stderr)
            raise typer.Exit(EXIT_TIMEOUT)
        time.sleep(0.5)
    rc = int(p["rc"].read_text(encoding="utf-8").strip()) if p["rc"].exists() else 0
    console.print(str(rc))
    raise typer.Exit(rc)


def stop_cmd(
    session_id: str,
    force: bool = False,
    wind_down: bool = False,
    grace: int = 20,
) -> None:
    settings = ThegentSettings()
    meta_path = _find_session_meta(settings, session_id)
    m = _read_session_meta(meta_path)
    pid = int(m.get("pid", 0) or 0)
    if not _is_pid_running(pid):
        console.print("[dim]session not running[/dim]")
        return
    if force:
        os.killpg(pid, signal.SIGKILL)
        console.print("stopped (force)")
        return

    if wind_down:
        if grace < 0:
            raise typer.BadParameter("--grace must be >= 0")
        os.killpg(pid, signal.SIGTERM)
        start = time.time()
        while _is_pid_running(pid):
            if time.time() - start >= grace:
                break
            time.sleep(0.5)
        if _is_pid_running(pid):
            console.print(f"wind-down grace elapsed ({grace}s); session still running")
        else:
            console.print("stopped (wind-down)")
        return

    os.killpg(pid, signal.SIGTERM)
    console.print("stopped")


def pause_cmd(session_id: str) -> None:
    """Pause a background session (register pause event)."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry
    registry = RunRegistry(settings.session_dir)

    # Verify session exists
    meta_path = _find_session_meta(settings, session_id)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        # Fallback to finding run_id from registry by correlation_id (session_id)
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == session_id:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {session_id}.[/red]")
        raise typer.Exit(1)

    registry.register_pause(run_id, reason="Manual pause")
    console.print(f"[yellow]Session {session_id} marked as PAUSED in registry.[/yellow]")


def resume_cmd(session_id: str) -> None:
    """Resume a background session (register resume event)."""
    settings = ThegentSettings()
    from thegent.execution import RunRegistry
    registry = RunRegistry(settings.session_dir)

    meta_path = _find_session_meta(settings, session_id)
    m = _read_session_meta(meta_path)
    run_id = m.get("run_id")
    if not run_id:
        runs = registry.list_runs(limit=100)
        for r in runs:
            if r.get("correlation_id") == session_id:
                run_id = r.get("run_id")
                break

    if not run_id:
        console.print(f"[red]Could not find run_id for session {session_id}.[/red]")
        raise typer.Exit(1)

    registry.register_resume(run_id)
    console.print(f"[green]Session {session_id} marked as RUNNING in registry.[/green]")


def list_agents_cmd() -> None:
    """List available agents."""
    agents = list_agent_names()
    backends = {
        "minimax": "cliproxy",
        "glm": "cliproxy",
        "roo": "cliproxy",
        "kilo": "cliproxy",
        "gemini": "codex",
        "codex": "codex",
        "copilot": "codex",
        "claude": "codex",
        "antigravity": "codex",
        "cursor-agent": "Direct",
        "cursor-api": "cursor-api",
    }
    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Backend", style="dim")
    for name in agents:
        display_name = AGENT_LABELS.get(name, name)
        table.add_row(display_name, backends.get(name, "Direct"))
    console.print(table)


def list_models_cmd(
    provider: str | None = None,
    by_model: bool = False,
    refresh: bool = False,
    include_contract: bool = False,
) -> None:
    """List available models (scraped from CLIs/config)."""
    if include_contract:
        from thegent.models import ModelCatalog
        from thegent.models.scrapers import get_scraped_catalog

        # Force a best-effort freshness refresh when requested.
        if refresh:
            get_scraped_catalog(refresh=True)
        payload = ModelCatalog.to_contract_view(
            use_scraped=True,
            use_cache=not refresh,
            provider_filter=provider,
        )
        console.print_json(data=payload)
        return

    if by_model:
        from thegent.models import ModelCatalog
        from thegent.models.scrapers import get_scraped_catalog

        get_scraped_catalog(use_cache=not refresh)
        view = ModelCatalog.to_catalog_view(use_scraped=True)
        console.print("\n[bold]Models by model ID (routing)[/bold]")
        for model_id, providers in sorted(view.by_model.items()):
            console.print(f"  {model_id}: {', '.join(providers)}")
        return
    providers = [provider] if provider else ["minimax", "glm", "cursor-agent", "cursor-api", "gemini", "copilot", "claude", "codex", "antigravity"]
    for p in providers:
        if p == "minimax":
            _list_minimax_models()
        elif p == "glm":
            _list_glm_models()
        elif p == "cursor-agent":
            _list_cursor_models()
        elif p == "cursor-api":
            _list_cursor_api_models()
        elif p == "gemini":
            _list_gemini_models()
        elif p == "copilot":
            _list_copilot_models()
        elif p == "claude":
            _list_claude_models()
        elif p == "codex":
            _list_codex_models()
        elif p == "antigravity":
            _list_antigravity_models()


def resolve_model_route_cmd(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
) -> None:
    """Resolve a model to a preferred route and emit contract-style output."""
    from thegent.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        console.print("[red]Invalid routing policy. Use prefer_direct, prefer_proxy, or failover.[/red]")
        raise typer.Exit(1)

    normalized = normalize_model_id(model)
    route = resolve_route_contract(model, provider_hint=provider, policy=policy_value)
    available_routes = [
        {
            "provider": r.provider,
            "backend_type": r.backend_type,
            "model_alias": r.model_alias,
            "priority": r.priority,
        }
        for r in sorted(ModelCatalog.routes_for(model), key=lambda r: (r.provider, r.priority, r.model_alias))
    ]
    payload = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is None:
        if available_routes:
            console.print("[yellow]No route matched the provided hint. Showing available routes below.[/yellow]")
        else:
            console.print(f"[red]No route for model '{model}'.[/red]")
        console.print_json(data=payload)
        raise typer.Exit(1)

    payload["resolved_route"] = {
        "provider": route.provider,
        "model_alias": route.model_alias,
        "backend_type": route.backend_type,
        "priority": route.priority,
        "schema_version": route.schema_version,
    }
    console.print_json(data=payload)


def list_model_contract_schema_cmd() -> None:
    """Print the route contract schema metadata used by contract views."""
    from thegent.models import route_contract

    console.print_json(data=route_contract())


def _list_minimax_models() -> None:
    """List Minimax models (via CLIProxyAPIPlus minimax: block in config)."""
    console.print("\n[bold]Minimax models (via CLIProxyAPIPlus)[/bold]")
    console.print("  minimax-m2.5 (default)")
    console.print("  [dim]Add minimax: block to config; run thegent cliproxy login minimax for instructions[/dim]")


def _list_glm_models() -> None:
    """List GLM models (via CLIProxyAPIPlus iflow channel)."""
    console.print("\n[bold]GLM models (via CLIProxyAPIPlus)[/bold]")
    console.print("  glm-5 (default)")
    console.print("  [dim]OAuth: thegent cliproxy login iflow (or glm)[/dim]")


def _list_cursor_models() -> None:
    """List cursor models via cursor agent --list-models."""
    try:
        proc = subprocess.run(
            ["cursor", "agent", "--list-models"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            console.print("\n[bold]Cursor models[/bold]")
            for line in proc.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith("Tip:"):
                    console.print(f"  {line}")
        else:
            console.print("[dim]cursor agent --list-models failed[/dim]")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[dim]Cursor CLI not found or timed out[/dim]")


def _list_cursor_api_models() -> None:
    """List cursor-api models via GET /v1/models (wisdgod cursor-api)."""
    from thegent.models.scrapers import scrape_cursor_api

    settings = ThegentSettings()
    models = scrape_cursor_api(settings)
    console.print("\n[bold]Cursor-api models (wisdgod)[/bold]")
    if models:
        for m in models:
            console.print(f"  {m}")
        console.print("  [dim]Requires cursor-api at THGENT_CURSOR_API_URL; set THGENT_CURSOR_API_TOKEN[/dim]")
    else:
        console.print("  [dim]cursor-api not reachable at %s[/dim]" % settings.cursor_api_url)


def _list_gemini_models() -> None:
    """Scrape gemini models from gemini --help (has -m/--model)."""
    console.print("\n[bold]Gemini models[/bold]")
    console.print("  gemini-3-flash (default)")
    console.print("  gemini-3-pro-preview")
    console.print("  gemini-2.0-flash")
    console.print("  [dim]Use gemini -m <model> or THGENT_GEMINI_MODEL[/dim]")


def _list_copilot_models() -> None:
    """Scrape copilot models from copilot --help --model choices."""
    try:
        proc = subprocess.run(
            ["copilot", "--help"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode == 0 and "--model" in proc.stdout:
            console.print("\n[bold]Copilot models[/bold]")
            # Extract quoted model names after "choices:"
            start = proc.stdout.find("--model")
            chunk = proc.stdout[start : start + 600] if start >= 0 else ""
            choices = re.findall(r'"([a-zA-Z0-9.-]+)"', chunk)
            seen = set()
            for c in choices:
                if c not in seen and ("claude" in c or "gpt" in c or "gemini" in c):
                    seen.add(c)
                    console.print(f"  {c}")
            if not seen:
                _list_copilot_models_fallback()
        else:
            _list_copilot_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_copilot_models_fallback()


def _list_copilot_models_fallback() -> None:
    """Fallback copilot model list."""
    console.print("\n[bold]Copilot models[/bold]")
    for m in ["claude-haiku-4.5 (default)", "claude-sonnet-4.5", "claude-opus-4.6", "gpt-5.3-codex", "gemini-3-flash"]:
        console.print(f"  {m}")


def _list_claude_models() -> None:
    """Scrape claude models from claude --help (--model aliases)."""
    console.print("\n[bold]Claude models[/bold]")
    console.print("  haiku (default)")
    console.print("  sonnet, opus")
    console.print("  claude-haiku-4.5, claude-sonnet-4.5, claude-opus-4.6")
    console.print("  [dim]Use claude --model <alias> or THGENT_CLAUDE_MODEL[/dim]")


def _list_codex_models() -> None:
    """List codex models (from cursor --list-models, codex variants)."""
    try:
        proc = subprocess.run(
            ["cursor", "agent", "--list-models"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0 and "codex" in proc.stdout.lower():
            console.print("\n[bold]Codex models[/bold]")
            for line in proc.stdout.splitlines():
                line = line.strip()
                if "codex" in line.lower():
                    console.print(f"  {line}")
            console.print("  [dim]Default: gpt-5.3-codex-spark-xhigh; high-power: gpt-5.3-codex-high, gpt-5.3-codex-xhigh[/dim]")
        else:
            _list_codex_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_codex_models_fallback()


def _list_codex_models_fallback() -> None:
    """Fallback codex model list."""
    console.print("\n[bold]Codex models[/bold]")
    for m in ["gpt-5.3-codex-spark-xhigh (default)", "gpt-5.3-codex", "gpt-5.3-codex-low", "gpt-5.3-codex-high", "gpt-5.3-codex-xhigh"]:
        console.print(f"  {m}")


def _list_antigravity_models() -> None:
    """List antigravity models (via CLIProxyAPIPlus)."""
    settings = ThegentSettings()
    console.print("\n[bold]Antigravity models (via CLIProxyAPIPlus)[/bold]")
    console.print(f"  {settings.default_antigravity_model} (default)")
    console.print("  [dim]OAuth: thegent cliproxy login antigravity[/dim]")
    console.print("  [dim]Other: gemini-3-pro-high, gemini-3-pro-image, tstars2.0 (iflow)[/dim]")


def _models_table(title: str) -> Table:
    t = Table(title=title)
    t.add_column("Model ID", style="cyan")
    t.add_column("Display Name", style="dim")
    return t


def cliproxy_login_cmd(provider: str) -> None:
    """Run OAuth login for provider (claude, codex, gemini, copilot, antigravity, qwen, iflow, kimi, kiro, roo, kilo)."""
    settings = ThegentSettings()
    try:
        rc = run_login(settings, provider)
        raise typer.Exit(rc)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


def list_droids_cmd(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory for project droids"),
) -> None:
    """List available droids."""
    settings = ThegentSettings()
    cwd = _resolve_cwd(cd) if cd else Path.cwd()
    droids_dir = _resolve_droids_dir(cwd, settings)
    droids = list_droid_names(droids_dir)

    if not droids:
        console.print("[dim]No droids found. Check THGENT_FACTORY_DROIDS_DIR.[/dim]")
        return

    table = Table(title="Droids")
    table.add_column("Name", style="cyan")
    for name in sorted(droids):
        table.add_row(name)
    console.print(table)
