"""Thegent CLI entry point (subcommand-only)."""

import json
import sys
from pathlib import Path

import typer

from thegent.cli import (
    archive_cmd,
    audit_verify_cmd,
    benchmark_cmd,
    bg_cmd,
    cliproxy_login_cmd,
    closure_pack_cmd,
    cockpit_cmd,
    contracts_conformance_cmd,
    contracts_registry_cmd,
    dag_add_cmd,
    dag_cancel_cmd,
    dag_checkpoint_cmd,
    dag_checkpoints_cmd,
    dag_list_cmd,
    dag_probe_cmd,
    dag_ready_cmd,
    dag_reconcile_cmd,
    dag_recover_cmd,
    dag_remove_cmd,
    dag_rollback_cmd,
    dag_run_cmd,
    dag_status_cmd,
    dag_sync_cmd,
    dag_update_cmd,
    dag_validate_cmd,
    data_protection_cmd,
    drift_cmd,
    escalate_add_cmd,
    escalate_approve_cmd,
    escalate_list_cmd,
    escalate_resolve_cmd,
    feedback_cmd,
    history_cmd,
    inspect_cmd,
    list_agents_cmd,
    list_droids_cmd,
    list_models_cmd,
    logs_cmd,
    migration_cmd,
    modes_cmd,
    operations_cmd,
    pause_cmd,
    plan_analyze_cmd,
    policy_show_cmd,
    ps_cmd,
    purge_cmd,
    resolve_model_route_cmd,
    resume_cmd,
    run_cmd,
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
    session_contracts_cmd,
    status_cmd,
    stop_cmd,
    sweep_cmd,
    wait_cmd,
)


def init_cmd(
    url: str = typer.Option(None, "--url", "-u", help="MCP server URL (default: http://127.0.0.1:3847/mcp)"),
    cli: bool = typer.Option(
        False, "--cli", help="Non-interactive, agent-friendly setup (smart mode, all detected targets)"
    ),
) -> None:
    """Initialize thegent: configure MCP clients and background services."""
    from rich.console import Console

    from thegent.install import run_install, run_wizard

    if cli:
        console = Console()
        console.print("[bold cyan]thegent init --cli[/bold cyan] (non-interactive)")
        run_install(
            target="all",
            mode="smart",
            install_service=True,
            verbose=True,
            url=url,
        )
        console.print("\n[bold green]Init complete.[/bold green]")
        return

    # Default to interactive wizard
    run_wizard(url=url)


app = typer.Typer(
    name="thegent",
    help="Unified agent orchestration CLI for Factory skills and droids",
    no_args_is_help=True,
)

app.command("init")(init_cmd)

orchestrate_app = typer.Typer(help="Agent execution and session management")
govern_app = typer.Typer(help="Governance, policy, and compliance")
recover_app = typer.Typer(help="State recovery and self-healing")
observe_app = typer.Typer(help="Observability, telemetry, and performance")
plan_app = typer.Typer(help="Task planning and DAG management")

app.add_typer(orchestrate_app, name="orchestrate")
app.add_typer(govern_app, name="govern")
app.add_typer(recover_app, name="recover")
app.add_typer(observe_app, name="observe")
app.add_typer(plan_app, name="plan")


@app.command("run")
@orchestrate_app.command("run")
def run(
    prompt: str = typer.Argument(..., help="Task prompt"),
    agent: str | None = typer.Argument(None, help="Provider (optional when -M/--model given)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout hint in seconds (tool-call budget injection)"),
    full: bool = typer.Option(False, "--full", "-f", help="Show full raw output (default: stream-json, parsed)"),
    live: bool = typer.Option(False, "--live", help="Stream output live to terminal"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override or model-first (when agent omitted)"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Provider override for model-first routing"),
    failover: bool = typer.Option(False, "--failover", help="On failure, try next route (model-first only)"),
    routing: str | None = typer.Option(
        None, "--routing", "-R", help="Routing policy: prefer_direct | prefer_proxy (default from config)"
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Print resolved model route contract metadata in output"
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID for registry correlation"),
    lane: str = typer.Option("standard", "--lane", help="Execution lane: standard, critical, recovery"),
    confidence: float | None = typer.Option(None, "--confidence", help="Task confidence score (0.0-1.0)"),
    override: str | None = typer.Option(None, "--override", help="Policy override reason code"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (default: current)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Domain tag for tiered retention (WP-3006)"),
) -> None:
    """Run a foreground agent invocation. Use -M <model> without agent for model-first routing."""
    run_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        live=live,
        droid=None,
        model=model,
        provider=provider,
        failover=failover,
        routing=routing,
        include_contract=include_contract,
        run_id=run_id,
        lane=lane,
        confidence=confidence,
        override_reason=override,
        contract_version=contract_version,
        domain=domain,
    )


@app.command("bg")
@orchestrate_app.command("bg")
def bg(
    prompt: str = typer.Argument(..., help="Task prompt"),
    agent: str | None = typer.Argument(None, help="Provider (optional when -M/--model given)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Mode: read-only, write, full"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout hint in seconds (tool-call budget injection)"),
    full: bool = typer.Option(False, "--full", help="Use full raw output mode"),
    owner: str | None = typer.Option(None, "--owner", help="Session owner tag (default: <user>:<cwd-name>)"),
    model: str | None = typer.Option(None, "--model", "-M", help="Model override or model-first"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Provider override for model-first routing"),
    routing: str | None = typer.Option(
        None, "--routing", "-R", help="Routing policy: prefer_direct | prefer_proxy (default from config)"
    ),
    failover: bool = typer.Option(False, "--failover", help="On failure, try next route (model-first only)"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md (agent-friendly)",
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in output"
    ),
    continuation: str | None = typer.Option(
        None, "--continuation", "-C", help="Prior session id(s) to continue from (comma-separated)"
    ),
    continuation_stderr: bool = typer.Option(
        False, "--continuation-stderr", help="Include stderr from prior session(s)"
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explicit run ID for registry correlation"),
    lane: str = typer.Option("standard", "--lane", help="Execution lane: standard, critical, recovery"),
    idempotency_token: str | None = typer.Option(
        None, "--idempotency-token", help="Deterministic token to prevent duplicate runs"
    ),
    confidence: float | None = typer.Option(None, "--confidence", help="Task confidence score (0.0-1.0)"),
    arbitration: str | None = typer.Option(
        None, "--arbitration", help="Arbitration role: leader | follower | consensus"
    ),
    override: str | None = typer.Option(None, "--override", help="Policy override reason code"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (default: current)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Domain tag for tiered retention (WP-3006)"),
) -> None:
    """Start a background run and register a session."""
    bg_cmd(
        prompt=prompt,
        agent=agent,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        droid=None,
        model=model,
        provider=provider,
        routing=routing,
        failover=failover,
        owner=owner,
        output_format=format,
        include_contract=include_contract,
        continue_from=continuation,
        continuation_include_stderr=continuation_stderr,
        run_id=run_id,
        lane=lane,
        idempotency_token=idempotency_token,
        confidence=confidence,
        arbitration=arbitration,
        override_reason=override,
        contract_version=contract_version,
        domain=domain,
    )


history_app = typer.Typer(
    help="Execution history and audit commands",
    invoke_without_command=True,
    no_args_is_help=False,
)


@history_app.callback(invoke_without_command=True)
def history_root(
    ctx: typer.Context,
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """Default `history` behavior: list runs when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        history_cmd(limit=limit, format=format)


@history_app.command("list")
@observe_app.command("history")
def history_list(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """List execution run history (sync and background)."""
    history_cmd(limit=limit, format=format)


@history_app.command("events")
def history_events(
    limit: int = typer.Option(100, "--limit", "-l", help="Number of events to show"),
    run_id: str | None = typer.Option(None, "--run-id", help="Filter events by Run ID"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
) -> None:
    """List raw telemetry events."""
    from thegent.cli import events_cmd

    events_cmd(run_id=run_id, limit=limit, format=format)


@history_app.command("verify")
@govern_app.command("verify")
def history_audit_verify(
    format: str | None = typer.Option(None, "--format", help="Output format: json | rich"),
) -> None:
    """Verify the integrity of the execution run registry."""
    audit_verify_cmd(format=format)


app.add_typer(history_app, name="history")


policy_app = typer.Typer(help="Governance and security policy commands")
app.add_typer(policy_app, name="policy")


@policy_app.command("show")
@govern_app.command("show-policy")
def policy_show() -> None:
    """Show active governance policies and thresholds."""
    policy_show_cmd()


escalate_app = typer.Typer(help="Governance escalation queue (WP-3008)")
govern_app.add_typer(escalate_app, name="escalate")


@escalate_app.command("add")
def govern_escalate_add(
    run_id: str = typer.Argument(..., help="Run ID that was blocked"),
    reason: str = typer.Argument(..., help="Block reason (e.g. policy violation)"),
    sla_minutes: int = typer.Option(30, "--sla", "-s", help="SLA in minutes (escalate by)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
    lane: str = typer.Option("standard", "--lane", "-l", help="Execution lane"),
) -> None:
    """Add a blocked run to the escalation queue."""
    escalate_add_cmd(run_id=run_id, reason=reason, sla_minutes=sla_minutes, owner=owner, lane=lane)


@escalate_app.command("list")
def govern_escalate_list(
    past_sla_only: bool = typer.Option(False, "--past-sla", help="Show only items past SLA"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max items to show"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """List governance escalation queue."""
    escalate_list_cmd(past_sla_only=past_sla_only, limit=limit, format=format)


@escalate_app.command("resolve")
def govern_escalate_resolve(
    run_id: str = typer.Argument(..., help="Run ID to resolve"),
    resolution: str = typer.Option("resolved", "--resolution", "-r", help="Resolution status"),
) -> None:
    """Mark an escalation item as resolved."""
    escalate_resolve_cmd(run_id=run_id, resolution=resolution)


@escalate_app.command("approve")
def govern_escalate_approve(
    run_id: str = typer.Argument(..., help="Run ID to approve"),
) -> None:
    """Approve an escalation, recording an override for the owner (G-GP-05)."""
    escalate_approve_cmd(run_id=run_id)


@govern_app.command("calibrate")
def govern_calibrate() -> None:
    """Recalculate trust score calibration factors for all agents (G-GP-09)."""
    from rich.console import Console
    from rich.table import Table

    from thegent.cli_impl import update_calibration_impl

    console = Console()
    results = update_calibration_impl()
    if not results:
        console.print("[dim]No runs with feedback found for calibration.[/dim]")
        return

    table = Table(title="Agent Calibration Factors")
    table.add_column("Agent")
    table.add_column("Factor", justify="right")
    table.add_column("Samples", justify="right")

    for agent, res in sorted(results.items()):
        table.add_row(agent, f"{res['factor']:.3f}", str(res["samples"]))

    console.print(table)
    console.print("[green]Calibration factors persisted.[/green]")


@govern_app.command("sweep")
def govern_sweep(
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Window size for drift detection"),
    include_audit: bool = typer.Option(False, "--audit", "-a", help="Include registry audit in sweep"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """WP-3005: Policy drift sweep - drift detection, budget check, past-SLA escalations (cron-ready)."""
    sweep_cmd(drift_window=drift_window, include_audit=include_audit, format=format)


@govern_app.command("purge")
def govern_purge(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="If true, only show what would be purged"),
) -> None:
    """WP-3006: Tiered retention purge (G-GP-07)."""
    purge_cmd(dry_run=dry_run)


@govern_app.command("data-protection")
def govern_data_protection(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show data protection and privacy controls status (WP-3006)."""
    data_protection_cmd(format=format)


@govern_app.command("contracts")
def govern_contracts(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show the contract registry and compatibility matrix."""
    contracts_registry_cmd(format=format)


@govern_app.command("conformance")
def govern_conformance(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    check_drift: bool = typer.Option(False, "--check-drift", help="Run drift alarm on contract telemetry"),
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Window size for drift detection"),
) -> None:
    """Run provider adapter conformance tests."""
    contracts_conformance_cmd(format=format, check_drift=check_drift, drift_window=drift_window)


@govern_app.command("migration")
def govern_migration(
    contract_id: str = typer.Argument(..., help="Contract ID (e.g. csm)"),
    version: str = typer.Argument(..., help="Version (e.g. csm-v1)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Evaluate migration status for a contract version."""
    migration_cmd(contract_id=contract_id, version=version, format=format)


@observe_app.command("summary")
def observe_summary(
    limit: int = typer.Option(500, "--limit", "-n", help="Events to analyze"),
    drift_window: int = typer.Option(50, "--drift-window", "-w", help="Drift analysis window"),
    structural_budget: float = typer.Option(
        5.0,
        "--structural-budget",
        help="Allowed structural drift percentage before budget alert",
    ),
    semantic_budget: float = typer.Option(
        10.0,
        "--semantic-budget",
        help="Allowed semantic drift percentage before budget alert",
    ),
    provider: str | None = typer.Option(None, "--provider", help="Filter summary to a specific provider"),
    trend_samples: int = typer.Option(
        0,
        "--trend-samples",
        help="Enable historical trend sampling with up to N latest runs (2+ enables trend mode)",
    ),
    top_escalations: int = typer.Option(10, "--top-escalations", help="Escalations to show in panel"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""
    from thegent.cli import observe_summary_cmd

    observe_summary_cmd(
        limit=limit,
        drift_window=drift_window,
        structural_budget=structural_budget,
        semantic_budget=semantic_budget,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
        format=format,
    )


@observe_app.command("kpis")
def observe_kpis(
    limit: int = typer.Option(500, "--limit", "-n", help="Number of events to analyze"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Show fallback KPIs for dashboard/alerting (G-CA-02 B3)."""
    from rich.console import Console
    from rich.table import Table

    from thegent.config import ThegentSettings
    from thegent.contracts.telemetry import ContractTelemetry

    settings = ThegentSettings()
    console = Console()
    ct = ContractTelemetry(settings.session_dir)
    kpis = ct.get_fallback_kpis(limit=limit)

    if format == "json":
        sys.stdout.write(json.dumps(kpis) + "\n")
        return

    table = Table(title=f"Fallback KPIs (last {limit} events)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total Events", str(kpis["total"]))
    table.add_row("Fallback Rate", f"{kpis['fallback_rate']:.1%}")
    table.add_row("Success Rate", f"{kpis['success_rate']:.1%}")
    table.add_row("Avg Confidence", f"{kpis['avg_confidence']:.2f}")
    table.add_row("Structural Drift %", f"{kpis['structural_drift_pct']:.2f}")
    table.add_row("Semantic Drift %", f"{kpis['semantic_drift_pct']:.2f}")
    console.print(table)

    by_provider = kpis.get("by_provider", {})
    if by_provider:
        p_table = Table(title="By Provider")
        p_table.add_column("Provider")
        p_table.add_column("Fallback %")
        p_table.add_column("Success %")
        p_table.add_column("Avg Conf")
        p_table.add_column("Total")
        for p, v in sorted(by_provider.items()):
            p_table.add_row(
                p,
                f"{v['fallback_rate']:.1%}",
                f"{v['success_rate']:.1%}",
                f"{v['avg_confidence']:.2f}",
                str(v["total"]),
            )
        console.print(p_table)


@observe_app.command("drift")
def observe_drift(
    window: int = typer.Option(50, "--window", "-w", help="Analysis window size"),
    structural_budget: float = typer.Option(5.0, "--structural-budget", help="Structural drift alert budget %"),
    semantic_budget: float = typer.Option(10.0, "--semantic-budget", help="Semantic drift alert budget %"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
) -> None:
    """Detect significant drift in contract performance and check alert budgets (G-RV-07)."""
    drift_cmd(window=window, format=format, structural_budget=structural_budget, semantic_budget=semantic_budget)


@observe_app.command("trend")
def observe_trend(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Trend payload type: session_contract_health_report | session_contract_health_gate",
    ),
    all_sessions: bool = typer.Option(False, "--all", help="Trend scope for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Trend scope owner filter"),
    strict: bool = typer.Option(False, "--strict", help="Trend scope strict checks"),
    limit: int = typer.Option(20, "--limit", help="Max snapshots to return"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
) -> None:
    """Read health trend snapshots for a report/gate policy scope."""
    session_contract_health_trend_cmd(
        payload_type=payload_type,
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        limit=limit,
        format=format,
    )


@app.command("cockpit")
@observe_app.command("cockpit")
def cockpit() -> None:
    """Show high-level operator cockpit summary."""
    cockpit_cmd()


@app.command("feedback")
@govern_app.command("feedback")
def feedback(
    run_id: str = typer.Argument(..., help="Run ID to provide feedback for"),
    score: float = typer.Argument(..., help="Confidence score (0.0 to 1.0)"),
    note: str = typer.Option(None, "--note", "-m", help="Optional feedback note"),
) -> None:
    """Provide operator feedback for a specific run."""
    feedback_cmd(run_id, score, note)


@app.command("archive")
@observe_app.command("archive")
def archive(
    days: int | None = typer.Option(
        None, "--days", "-d", help="Override retention days (default: THGENT_RETENTION_DAYS_SESSIONS)"
    ),
    domain: str | None = typer.Option(None, "--domain", help="Filter by domain tag (WP-3006)"),
    tier: str | None = typer.Option(None, "--tier", "-t", help="Storage tier: hot (30d) | cold (365d)"),
) -> None:
    """Archive old sessions (WP-6005). WP-3006: tiered retention (hot 30d, cold 1yr)."""
    archive_cmd(days=days, domain=domain, tier=tier)


@app.command("operations")
def operations(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    operation: str | None = typer.Option(
        None, "--operation", "-o", help="Filter by operation: orchestrate | govern | recover | observe | plan"
    ),
) -> None:
    """List universal operation taxonomy (orchestrate, govern, recover, observe, plan)."""
    operations_cmd(format=format, operation=operation)


@app.command("modes")
def modes(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default)"),
    mode: str | None = typer.Option(
        None, "--mode", "-m", help="Filter by mode: sequential_delegation | parallel_consensus | review_loop"
    ),
) -> None:
    """List multi-agent orchestration modes (G-KD-04)."""
    modes_cmd(format=format, mode=mode)


@app.command("benchmark")
@observe_app.command("benchmark")
def benchmark() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    benchmark_cmd()


@app.command("closure-pack")
@govern_app.command("closure-pack")
def closure_pack(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Generate a formal closure pack for the current DAG session (WP-6002/6008/FR-024)."""
    closure_pack_cmd(cd=cd)


@app.command("history-legacy", hidden=True)
def history_legacy(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: json | rich (default) | md",
    ),
    events: bool = typer.Option(False, "--events", help="Show raw telemetry events"),
    run_id: str | None = typer.Option(None, "--run-id", help="Filter events by Run ID"),
) -> None:
    """List execution run history (sync and background)."""
    if events:
        from thegent.cli import events_cmd

        events_cmd(run_id=run_id, limit=limit, format=format)
    else:
        history_cmd(limit=limit, format=format)


@app.command("ps")
@orchestrate_app.command("ps")
def ps(
    all_sessions: bool = typer.Option(False, "--all", help="Show sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Override owner filter"),
    format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json | rich (default) | md (agent-friendly)",
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in list payload"
    ),
) -> None:
    """List registered background sessions."""
    ps_cmd(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        include_contract=include_contract,
    )


@app.command("status")
@orchestrate_app.command("status")
@observe_app.command("status")
def status(
    session_id: str = typer.Argument(..., help="Session id"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in output"
    ),
) -> None:
    """Show one session status."""
    status_cmd(session_id=session_id, format=format, include_contract=include_contract)


@app.command("inspect")
@orchestrate_app.command("inspect")
@observe_app.command("inspect")
def inspect(
    session_ids: list[str] = typer.Argument(default=[], help="Session ID(s). Use --owner to inspect all for owner."),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Inspect all sessions for this owner"),
    tail: int = typer.Option(50, "--tail", "-n", help="Log lines per session"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr instead of stdout"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in status payload"
    ),
) -> None:
    """Show status and logs for one or more sessions. No shell loop needed."""
    inspect_cmd(
        session_ids=session_ids or [],
        owner=owner,
        tail=tail,
        stderr=stderr,
        format=format,
        include_contract=include_contract,
    )


@app.command("session-contracts")
@govern_app.command("session-contracts")
def session_contracts(
    all_sessions: bool = typer.Option(False, "--all", help="Audit sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    missing_only: bool = typer.Option(
        False, "--missing-only", help="Show only sessions with incomplete/missing contract metadata"
    ),
    summary_only: bool = typer.Option(False, "--summary-only", help="Return summary only"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
) -> None:
    """Audit session routing contract metadata coverage and completeness."""
    session_contracts_cmd(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )


@app.command("session-contract-health-gate")
@govern_app.command("health-gate")
def session_contract_health_gate(
    all_sessions: bool = typer.Option(False, "--all", help="Evaluate sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy", help="Minimum healthy ratio required to pass"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    no_worse_than_baseline: bool = typer.Option(
        False,
        "--no-worse-than-baseline",
        help="Fail if blocked ratio regresses beyond baseline + tolerance.",
    ),
    regression_tolerance: float = typer.Option(
        0.0,
        "--regression-tolerance",
        help="Allowed blocked-ratio regression when baseline checks are enabled.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write gate artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Fail if routing contract health is below threshold."""
    session_contract_health_gate_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-report")
@govern_app.command("health-report")
def session_contract_health_report(
    all_sessions: bool = typer.Option(False, "--all", help="Report sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Filter by owner"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    strict: bool = typer.Option(False, "--strict", help="Enable strict contract/provider/alias alignment checks"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Max blocked sessions to show in reports"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    no_worse_than_baseline: bool = typer.Option(
        False,
        "--no-worse-than-baseline",
        help="Fail report policy if blocked ratio regresses beyond baseline + tolerance.",
    ),
    regression_tolerance: float = typer.Option(
        0.0,
        "--regression-tolerance",
        help="Allowed blocked-ratio regression when baseline checks are enabled.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write report artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Create a policy-friendly session contract health report with issue and owner breakdown."""
    session_contract_health_report_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-trend")
@govern_app.command("health-trend")
def session_contract_health_trend(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Trend payload type: session_contract_health_report | session_contract_health_gate",
    ),
    all_sessions: bool = typer.Option(False, "--all", help="Trend scope for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Trend scope owner filter"),
    strict: bool = typer.Option(False, "--strict", help="Trend scope strict checks"),
    policy_profile: str | None = typer.Option(
        None,
        "--policy-profile",
        help="Policy profile: strict_ci | warn_only | prod_release",
    ),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy", help="Gate trend scope minimum healthy ratio"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Report trend scope top blocked"),
    limit: int = typer.Option(20, "--limit", help="Max snapshots to return"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich (default) | md"),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Write trend artifact to path. If --export-format is not set, file extension "
            "(.json/.md/.csv/.jsonl) controls the format; unknown extension defaults to json."
        ),
    ),
    export_format: str | None = typer.Option(
        None,
        "--export-format",
        help="Export format: json | md | csv | jsonl (defaults from --output extension)",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite output artifact if it already exists"),
) -> None:
    """Read health trend snapshots for a report/gate policy scope."""
    session_contract_health_trend_cmd(
        payload_type=payload_type,
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        format=format,
        output=output,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("logs")
@orchestrate_app.command("logs")
@observe_app.command("logs")
def logs(
    session_id: str = typer.Argument(..., help="Session id"),
    follow: bool = typer.Option(False, "--follow", "-F", help="Follow log output"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr log instead of stdout"),
    tail: int = typer.Option(200, "--tail", help="Initial tail lines"),
    timeout: int = typer.Option(0, "--timeout", help="Max follow timeout seconds (0=unbounded)"),
) -> None:
    """Print session logs."""
    logs_cmd(session_id=session_id, follow=follow, stderr=stderr, tail=tail, timeout=timeout)


@app.command("wait")
@orchestrate_app.command("wait")
@observe_app.command("wait")
def wait(
    session_id: str = typer.Argument(..., help="Session id"),
    timeout: int = typer.Option(0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
) -> None:
    """Wait for session completion and return session exit code."""
    wait_cmd(session_id=session_id, timeout=timeout)


@app.command("stop")
@orchestrate_app.command("stop")
@recover_app.command("stop")
def stop(
    session_id: str = typer.Argument(..., help="Session id"),
    force: bool = typer.Option(False, "--force", help="Use SIGKILL instead of SIGTERM"),
    wind_down: bool = typer.Option(
        False,
        "--wind-down",
        help="Send SIGTERM and wait up to --grace seconds before returning",
    ),
    grace: int = typer.Option(
        20,
        "--grace",
        min=0,
        help="Wind-down grace window in seconds",
    ),
) -> None:
    """Stop a running session."""
    stop_cmd(session_id=session_id, force=force, wind_down=wind_down, grace=grace)


@app.command("pause")
@orchestrate_app.command("pause")
def pause(
    session_id: str = typer.Argument(..., help="Session id to pause"),
) -> None:
    """Mark a session as PAUSED in the registry (HITL)."""
    pause_cmd(session_id=session_id)


@app.command("resume")
@orchestrate_app.command("resume")
def resume(
    session_id: str = typer.Argument(..., help="Session id to resume"),
) -> None:
    """Mark a paused session as RUNNING in the registry (HITL)."""
    resume_cmd(session_id=session_id)


@app.command("list-agents")
def list_agents() -> None:
    """List available providers."""
    list_agents_cmd()


@app.command("list-droids")
def list_droids(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory for project droids"),
) -> None:
    """List available droids."""
    list_droids_cmd(cd=cd)


@app.command("list-models")
def list_models(
    provider: str | None = typer.Argument(None, help="Optional provider filter"),
    by_model: bool = typer.Option(False, "--by-model", help="Unified view: model -> providers (routing)"),
    refresh: bool = typer.Option(False, "--refresh", help="Bypass cache, re-scrape providers"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include structured route contract in output"
    ),
) -> None:
    """List known models (optionally filtered by provider)."""
    list_models_cmd(
        provider=provider,
        by_model=by_model,
        refresh=refresh,
        include_contract=include_contract,
    )


@app.command("resolve-model-route")
def resolve_model_route(
    model: str = typer.Argument(..., help="Model identifier (alias or canonical model ID)"),
    provider: str | None = typer.Option(None, "--provider", "-P", help="Optional provider hint"),
    policy: str = typer.Option(
        "prefer_direct", "--policy", help="Routing policy: prefer_direct, prefer_proxy, failover"
    ),
) -> None:
    """Resolve a model to a concrete provider+alias route."""
    resolve_model_route_cmd(model=model, provider=provider, policy=policy)


models_app = typer.Typer(help="Model catalog and cache commands")
app.add_typer(models_app, name="models")


@models_app.command("refresh")
def models_refresh() -> None:
    """Invalidate models cache. Next list-models or route resolution will re-scrape."""
    from thegent.models import invalidate_models_cache

    if invalidate_models_cache():
        typer.echo("Models cache invalidated.")
    else:
        typer.echo("Models cache was empty or already invalidated.")


@models_app.command("contract")
def models_contract() -> None:
    """Show route contract metadata for model catalog consumers."""
    from thegent.cli import list_model_contract_schema_cmd

    list_model_contract_schema_cmd()


cliproxy_app = typer.Typer(help="CLIProxyAPIPlus OAuth login and config (auth stored in ~/.cli-proxy-api)")
app.add_typer(cliproxy_app, name="cliproxy")


@cliproxy_app.command("ensure-config")
def cliproxy_ensure_config() -> None:
    """Ensure proxy config exists (port, auth-dir). Add provider blocks manually. Restart proxy to apply."""
    from thegent.agents.cliproxy_manager import _ensure_config
    from thegent.config import ThegentSettings

    config_path = _ensure_config(ThegentSettings())
    typer.echo(f"Config ensured: {config_path}")


@cliproxy_app.command("login")
def cliproxy_login(
    provider: str = typer.Argument(
        ...,
        help="Provider: claude, codex, gemini, copilot, antigravity, qwen, iflow, kimi, kiro, kiro-aws, kiro-import, roo, kilo. Minimax: use config (see docs/guides/PROVIDER_SETUP_GUIDE.md)",
    ),
) -> None:
    """Run OAuth login for provider. Tokens in ~/.cli-proxy-api (CLIProxy) or provider paths (roo: ~/.config/roo, kilo: ~/.kilocode)."""
    cliproxy_login_cmd(provider)


@app.command("login")
@orchestrate_app.command("login")
def login(
    provider: str = typer.Argument(
        ...,
        help="Provider: claude, codex, gemini, copilot, antigravity, qwen, iflow, kimi, kiro, roo, kilo. Alias for cliproxy login.",
    ),
) -> None:
    """Run OAuth login for provider. Alias for `thegent cliproxy login`. Native: roo→roo auth login, kilo→kilo auth."""
    cliproxy_login_cmd(provider)


dag_app = typer.Typer(help="DAG session commands (read .factory/dag-session.md)")
app.add_typer(dag_app, name="dag")


@dag_app.command("list")
@plan_app.command("list")
def dag_list(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory (default: cwd)"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """Parse and display DAG session from .factory/dag-session.md."""
    dag_list_cmd(cd=cd, format=format)


@plan_app.command("analyze")
def plan_analyze(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    pert: bool = typer.Option(False, "--pert", help="Run PERT overlay on DAG tasks"),
    resources: bool = typer.Option(False, "--resources", help="Simulate resource contention"),
    continuity: bool = typer.Option(False, "--continuity", help="Score continuity risk for handoff"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json | rich"),
) -> None:
    """Run planning simulation overlays (XD1–XD3): PERT, resources, continuity risk."""
    plan_analyze_cmd(cd=cd, pert=pert, resources=resources, continuity=continuity, format=format)


@dag_app.command("validate")
@plan_app.command("validate")
def dag_validate(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory (default: cwd)"),
) -> None:
    """Validate DAG: cycles, orphans, agent names. Exit 2 on failure."""
    dag_validate_cmd(cd=cd)


@dag_app.command("add")
@plan_app.command("add")
def dag_add(
    task_id: str = typer.Argument(..., help="Task ID (e.g. QA-A4)"),
    agent: str = typer.Argument(..., help="Agent name"),
    prompt: str = typer.Argument(..., help="Task prompt (inline or @.factory/prompts/<id>.md)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    depends_on: str | None = typer.Option(None, "--depends-on", help="Comma-separated task IDs"),
    contract_version: str | None = typer.Option(None, "--contract-version", help="Contract schema version (XA4)"),
) -> None:
    """Add a task to the DAG."""
    dag_add_cmd(
        task_id=task_id, agent=agent, prompt=prompt, cd=cd, depends_on=depends_on, contract_version=contract_version
    )


@dag_app.command("update")
@plan_app.command("update")
def dag_update(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    status: str | None = typer.Option(
        None, "--status", "-s", help="Set status: pending|running|done|failed|cancelled|skipped"
    ),
    prompt: str | None = typer.Option(None, "--prompt", "-p", help="Update prompt"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Update agent"),
    depends_on: str | None = typer.Option(None, "--depends-on", help="Update depends_on (comma-separated)"),
    contract_version: str | None = typer.Option(None, "--contract-version", help="Contract schema version (XA4)"),
) -> None:
    """Update a task in the DAG."""
    dag_update_cmd(
        task_id=task_id,
        cd=cd,
        status=status,
        prompt=prompt,
        agent=agent,
        depends_on=depends_on,
        contract_version=contract_version,
    )


@dag_app.command("remove")
@plan_app.command("remove")
def dag_remove(
    task_id: str = typer.Argument(..., help="Task ID to remove"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Remove a task from the DAG."""
    dag_remove_cmd(task_id=task_id, cd=cd)


@dag_app.command("cancel")
@plan_app.command("cancel")
def dag_cancel(
    task_id: str = typer.Argument(..., help="Task ID to cancel (soft remove)"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Set task status to cancelled."""
    dag_cancel_cmd(task_id=task_id, cd=cd)


@dag_app.command("ready")
@plan_app.command("ready")
def dag_ready(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """List task IDs with satisfied dependencies (ready to run)."""
    dag_ready_cmd(cd=cd, format=format)


@dag_app.command("run")
@plan_app.command("run")
def dag_run(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="List what would run without spawning"),
    task: str | None = typer.Option(None, "--task", "-t", help="Run only this task ID"),
    max_parallel: int | None = typer.Option(None, "--max-parallel", help="Max parallel spawns"),
    lane: str | None = typer.Option(None, "--lane", help="Force all tasks into this lane"),
    check_drift: bool = typer.Option(False, "--check-drift", help="Block run if contract drift detected (XC2)"),
    contract_version: str | None = typer.Option(
        None, "--contract-version", help="Contract schema version (XA4; overrides task-level)"
    ),
) -> None:
    """Spawn thegent bg for each ready task; update status=running and session_id."""
    dag_run_cmd(
        cd=cd,
        dry_run=dry_run,
        task=task,
        max_parallel=max_parallel,
        lane=lane,
        check_drift=check_drift,
        contract_version=contract_version,
    )


@dag_app.command("status")
@plan_app.command("status")
def dag_status(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: rich or md"),
) -> None:
    """Show task + linked session status (running/exited:rc)."""
    dag_status_cmd(cd=cd, format=format)


@dag_app.command("sync")
@plan_app.command("sync")
def dag_sync(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Run in a loop (health check)"),
    interval: int = typer.Option(10, "--interval", "-i", help="Sync interval in seconds"),
) -> None:
    """Update task status from session exit (running -> done/failed)."""
    import time

    while True:
        dag_sync_cmd(cd=cd)
        if not watch:
            break
        time.sleep(interval)


@dag_app.command("reconcile")
@recover_app.command("reconcile")
def dag_reconcile(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Reconcile DAG state with reality (clean up stuck 'running' tasks)."""
    dag_reconcile_cmd(cd=cd)


@dag_app.command("checkpoint")
@plan_app.command("checkpoint")
def dag_checkpoint(
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
    reason: str = typer.Option("Manual checkpoint", "--reason", "-r", help="Reason for checkpoint"),
) -> None:
    """Create a point-in-time checkpoint of the DAG state."""
    dag_checkpoint_cmd(cd=cd, reason=reason)


@dag_app.command("rollback")
@plan_app.command("rollback")
@recover_app.command("rollback")
def dag_rollback(
    checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to rollback to"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Rollback DAG state to a specific checkpoint."""
    dag_rollback_cmd(checkpoint_id=checkpoint_id, cd=cd)


@dag_app.command("checkpoints")
@plan_app.command("checkpoints")
def dag_checkpoints(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of checkpoints to show"),
) -> None:
    """List recent DAG checkpoints."""
    dag_checkpoints_cmd(limit=limit)


@dag_app.command("recover")
@recover_app.command("dag-recover")
def dag_recover(
    action: str = typer.Argument("retry-failed", help="Recovery action: retry-failed | clear-stuck | reset-retries"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Perform recovery playbook actions on the DAG."""
    dag_recover_cmd(cd=cd, action=action)


@dag_app.command("probe")
@plan_app.command("probe")
@observe_app.command("probe")
def dag_probe(
    baseline_id: str | None = typer.Option(None, "--baseline-id", help="Baseline checkpoint ID"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Working directory"),
) -> None:
    """Compare current DAG state with a baseline checkpoint to detect regressions."""
    dag_probe_cmd(cd=cd, baseline_id=baseline_id)


mcp_app = typer.Typer(
    help="MCP config and service: install thegent into Cursor/Claude Code/Codex; manage HTTP server as startup service",
)
app.add_typer(mcp_app, name="mcp")


@mcp_app.command("install")
def mcp_install(
    client: str = typer.Argument(
        ...,
        help="Client: cursor, claude-code, codex, claude-desktop, droid, or all",
    ),
    url: str | None = typer.Option(None, "--url", "-u", help="MCP URL (default: http://127.0.0.1:3847/mcp)"),
    workspace: Path | None = typer.Option(
        None, "--workspace", "-d", help="Workspace dir for cursor (writes .cursor/mcp.json)"
    ),
) -> None:
    """Add thegent to MCP config for Cursor, Claude Code, Codex, or Claude Desktop."""
    from thegent.config import ThegentSettings
    from thegent.mcp_manage import _get_mcp_url, install_to_client

    settings = ThegentSettings()
    mcp_url = url or _get_mcp_url(settings)
    clients = ["cursor", "claude-code", "codex", "claude-desktop", "droid"] if client == "all" else [client]
    from rich.console import Console

    console = Console()
    for c in clients:
        ws = workspace if c == "cursor" else None
        ok, msg = install_to_client(c, mcp_url, workspace=ws)
        if ok:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{c}: {msg}[/red]")


@mcp_app.command("up")
def mcp_up_cmd() -> None:
    """Start MCP + proxy via process-compose (bundled mode)."""
    from rich.console import Console

    from thegent.mcp_manage import mcp_up

    console = Console()
    ok, msg = mcp_up()
    if ok:
        console.print(f"[green]{msg}[/green]")
        console.print("[dim]MCP: http://127.0.0.1:3847/mcp | Proxy: http://127.0.0.1:8317[/dim]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mcp_app.command("down")
def mcp_down_cmd() -> None:
    """Stop MCP + proxy (process-compose)."""
    from rich.console import Console

    from thegent.mcp_manage import mcp_down

    console = Console()
    ok, msg = mcp_down()
    if ok:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@mcp_app.command("service")
def mcp_service(
    action: str = typer.Argument(
        ...,
        help="Action: install, start, stop, restart, status, uninstall",
    ),
) -> None:
    """Manage thegent MCP HTTP server as launchd service (macOS). Start server before clients connect."""
    from rich.console import Console

    from thegent.config import ThegentSettings
    from thegent.mcp_manage import (
        service_install,
        service_start,
        service_status,
        service_stop,
        service_uninstall,
    )

    console = Console()
    settings = ThegentSettings()
    if action == "install":
        ok, msg = service_install()
        console.print(msg)
        if ok:
            console.print("[dim]Then: thegent mcp service start[/dim]")
    elif action == "start":
        ok, msg = service_start()
        console.print(msg)
        if ok:
            console.print(f"[dim]MCP at http://{settings.mcp_host}:{settings.mcp_port}/mcp[/dim]")
    elif action == "stop":
        ok, msg = service_stop()
        console.print(msg)
    elif action == "restart":
        service_stop()
        ok, msg = service_start()
        console.print(msg)
    elif action == "status":
        ok, msg = service_status(settings)
        console.print(msg)
    elif action == "uninstall":
        ok, msg = service_uninstall()
        console.print(msg)
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)
    if not ok and action in ("install", "start", "stop", "restart", "uninstall"):
        raise typer.Exit(1)


@app.command("serve")
def serve(
    host: str | None = typer.Option(None, "--host", "-H", help="Bind address (default: THGENT_MCP_HOST or 127.0.0.1)"),
    port: int | None = typer.Option(None, "--port", "-p", help="HTTP port (default: THGENT_MCP_PORT or 3847)"),
) -> None:
    """Start the MCP server (requires fastmcp: pip install thegent[mcp])."""
    try:
        from thegent.mcp_server import run
    except ImportError:
        from rich.console import Console

        Console().print("[red]fastmcp not installed. Run: pip install thegent[mcp][/red]")
        raise typer.Exit(1)
    run(host=host, port=port)


@app.command("install")
def install_cmd(
    target: str = typer.Option(
        "all", "--target", "-t", help="Target: claude-code|claude-desktop|cursor|codex|droid|all (default: all)"
    ),
    editable: bool = typer.Option(
        False, "--editable", "-e", help="Symlink install instead of copy (bi-directional sync)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite all files (no merge)"),
    undo: bool = typer.Option(False, "--undo", help="Undo previous installation using manifest"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Ask before overwriting files with local changes"
    ),
    wizard: bool = typer.Option(False, "--wizard", "-w", help="Run interactive installation wizard"),
    service: bool = typer.Option(False, "--service", help="Install background MCP service (launchd on macOS)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would happen without making changes"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    url: str = typer.Option(None, "--url", "-u", help="MCP server URL (default: http://127.0.0.1:3847/mcp)"),
) -> None:
    """Managed installation of thegent components and MCP configuration."""
    from rich.console import Console

    from thegent.install import run_install, run_wizard

    if wizard:
        run_wizard(url=url)
        return

    local_console = Console()
    if undo:
        mode = "undo"
    elif interactive:
        mode = "interactive"
    else:
        mode = "editable" if editable else ("force" if force else "smart")

    local_console.print(f"[bold]=== thegent install ({mode}) ===[/bold]")
    if not undo:
        local_console.print(f"Target: {target}")
    if dry_run:
        local_console.print("[yellow]Dry run: no changes will be made[/yellow]")
    local_console.print()

    counts = run_install(
        target=target,
        mode=mode,
        dry_run=dry_run,
        verbose=verbose,
        url=url,
        install_service=service,
    )

    local_console.print()
    local_console.print("[bold]Results:[/bold]")
    if mode == "undo":
        local_console.print(f"  Removed:   {counts.get('removed', 0)}")
        local_console.print(f"  Restored:  {counts.get('restored', 0)}")
        local_console.print(f"  Reverted:  {counts.get('reverted', 0)}")
    else:
        local_console.print(f"  Copied/Linked: {counts['copied']}")
        local_console.print(f"  Skipped:       {counts['skipped']}")
        local_console.print(f"  Conflicts:     {counts['conflicts']}")

    if counts.get("errors", 0) > 0:
        local_console.print(f"  [red]Errors:        {counts['errors']}[/red]")


if __name__ == "__main__":
    app()
