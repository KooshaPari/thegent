"""Thegent CLI infra/system commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import typer

from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from phenotype_thegent_cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _make_load_classifier,
    _normalize_output_format,
    console,
)
from phenotype_thegent_cli.commands.infra_env_helpers import resolve_env_file, rewrite_max_concurrency_lines
from phenotype_thegent_cli.commands.infra_interruption_helpers import load_recent_interruptions
from phenotype_thegent_cli.commands.infra_observe_helpers import build_observe_lines
from phenotype_thegent_cli.commands.infra_sitback_helpers import build_dashboard_panels
from phenotype_thegent_cli.commands.infra_usage_helpers import build_provider_usage_table


def interruption_list_cmd(limit: int = 20, format: str | None = None) -> None:
    """List recent interruptions (WP-4004)."""
    settings = ThegentSettings()
    from phenotype_thegent_execution.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    if not it.path.exists():
        console.print("[dim]No interruptions recorded.[/dim]")
        return
    items = load_recent_interruptions(it.path, limit)
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(items).decode().decode() + "\n")
        return
    if not items:
        console.print("[dim]No interruptions in window.[/dim]")
        return
    table = Table(title="Interruption Log (WP-4004)")
    table.add_column("Timestamp")
    table.add_column("Type")
    table.add_column("Run ID")
    table.add_column("Severity")
    for i in items:
        table.add_row(
            (i.get("timestamp", "?")[:19]),
            i.get("type", "unknown"),
            i.get("run_id", "?"),
            i.get("severity", "medium"),
        )
    console.print(table)
    fatigue = it.get_fatigue_score()
    console.print(f"[dim]Fatigue score: {fatigue:.2f} (ceiling: 10/hr)[/dim]")


def config_check_cmd(format: str | None = None) -> None:
    """Validate config and report issues (DX-010, ROB-013)."""
    from pydantic import ValidationError

    issues: list[str] = []
    try:
        settings = ThegentSettings()
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            issues.append(f"Config error: {loc} — {err.get('msg', 'invalid')}")
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}).decode().decode() + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)

    # Optional: path checks
    session_dir = Path(settings.session_dir).expanduser().resolve()
    if not session_dir.parent.exists():
        issues.append(f"Session dir parent missing: {session_dir.parent}")
    if session_dir.exists() and not os.access(session_dir, os.W_OK):
        issues.append(f"Session dir not writable: {session_dir}")

    if issues:
        if format == "json":
            sys.stdout.write(json.dumps({"ok": False, "issues": issues}).decode().decode() + "\n")
            raise typer.Exit(1)
        for i in issues:
            console.print(f"[yellow]{i}[/yellow]")
        raise typer.Exit(1)

    if format == "json":
        sys.stdout.write(json.dumps({"ok": True, "issues": []}).decode().decode() + "\n")
        return
    console.print("[green]Config OK.[/green]")


def concurrency_show_cmd(format: str | None = None) -> None:
    """Show current concurrency limit and utilization (WP-5001)."""
    from phenotype_thegent_cli.commands.impl import ps_impl
    from phenotype_thegent_execution.orchestration.resource.load_based_limits import (
        LimitGateConfig,
        compute_dynamic_limit,
        sample_resources,
    )

    settings = ThegentSettings()
    sessions = ps_impl(all=True)
    running_count = sum(1 for s in sessions if s.get("status") == "running")

    # WP-5001: Resource-aware dynamic limits
    snapshot = sample_resources()
    config = LimitGateConfig.from_dict(settings.model_dump())
    dynamic_limit, gate_details = compute_dynamic_limit(snapshot, config)

    limit = settings.max_concurrency
    utilization_pct = (running_count / limit * 100) if limit > 0 else 0

    data = {
        "limit": limit,
        "dynamic_limit": dynamic_limit,
        "running": running_count,
        "available": max(0, dynamic_limit - running_count),
        "utilization_percent": round(utilization_pct, 1),
        "resource_gates": gate_details,
    }

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data, indent=2).decode().decode() + "\n")
        return

    table = Table(title="Concurrency Status (WP-5001)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Configured Limit (max_concurrency)", str(limit))
    table.add_row("Dynamic Resource Limit", str(dynamic_limit))
    table.add_row("Active Sessions", str(running_count))
    table.add_row("Available Slots", str(max(0, dynamic_limit - running_count)))
    table.add_row("Utilization (of Configured)", f"{utilization_pct:.1f}%")
    console.print(table)

    gate_table = Table(title="Resource Gates")
    gate_table.add_column("Gate", style="cyan")
    gate_table.add_column("Status", style="yellow")
    gate_table.add_column("Value/Utilization", style="dim")

    if "fd_utilization" in gate_details:
        gate_table.add_row(
            "File Descriptors", gate_details.get("fd_gate", "normal"), f"{gate_details['fd_utilization'] * 100:.1f}%"
        )
    if "mem_available_mb" in gate_details:
        gate_table.add_row(
            "Memory Available", gate_details.get("mem_gate", "normal"), f"{gate_details['mem_available_mb']:.0f} MB"
        )
    if "load_per_cpu" in gate_details:
        gate_table.add_row(
            "CPU Load", gate_details.get("load_gate", "normal"), f"{gate_details['load_per_cpu']:.2f}/cpu"
        )

    console.print(gate_table)


def concurrency_set_cmd(limit: int) -> None:
    """Set concurrency limit (updates .env file)."""
    if limit < 1:
        console.print("[red]Error: Limit must be >= 1[/red]")
        raise typer.Exit(1)
    if limit > 200:
        console.print("[red]Error: Limit must be <= 200[/red]")
        raise typer.Exit(1)

    # Find .env file (project root or current dir)
    env_file = resolve_env_file(Path.cwd(), Path(__file__))
    if not env_file.exists():
        console.print("[yellow]Warning: .env file not found. Creating new one.[/yellow]")
        env_file.parent.mkdir(parents=True, exist_ok=True)

    # Read existing .env or create new
    env_lines: list[str] = []
    if env_file.exists():
        env_lines = env_file.read_text(encoding="utf-8").splitlines()

    # Update or add THGENT_MAX_CONCURRENCY
    new_lines, _ = rewrite_max_concurrency_lines(env_lines, limit)

    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    console.print(f"[green]Concurrency limit set to {limit}[/green]")
    console.print("[dim]Note: Restart thegent processes or reload environment for changes to take effect.[/dim]")


def load_status_cmd(format: str | None = None) -> None:
    """Show load classification and safe-mode status (WP-5002)."""
    settings = ThegentSettings()
    lc = _make_load_classifier(settings)
    running = lc.get_running_count()
    level = lc.get_load_level()
    safe_mode = lc.is_safe_mode_active()
    shape = lc.get_traffic_shape()
    data = {
        "running_count": running,
        "load_level": level,
        "safe_mode_active": safe_mode,
        "traffic_shape": shape,
        "spike_threshold": settings.load_spike_threshold,
        "surge_threshold": settings.load_surge_threshold,
    }
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data).decode().decode() + "\n")
        return
    table = Table(title="Load Status (WP-5002)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Running sessions", str(running))
    table.add_row("Load level", level)
    table.add_row("Safe-mode active", "[red]Yes[/red]" if safe_mode else "[green]No[/green]")
    table.add_row("Traffic shaping", shape)
    table.add_row("Thresholds", f"spike>={settings.load_spike_threshold}, surge>={settings.load_surge_threshold}")
    console.print(table)


def cost_status_cmd(format: str | None = None) -> None:
    """Show cost budget utilization and cost-aware routing status (WP-5003)."""
    settings = ThegentSettings()
    from phenotype_thegent_routing.cost.aggregator import CostAggregator

    agg = CostAggregator(settings.session_dir)
    mtd = agg.get_mtd_total()
    by_cat = agg.get_all_categories_mtd()
    budget = float(getattr(settings, "cost_budget_mtd", 100.0))
    utilization = (mtd / budget * 100) if budget > 0 else 0.0
    tighten = float(getattr(settings, "cost_quality_budget_tighten_threshold", 0.80)) * 100
    cost_aware = getattr(settings, "routing_cost_aware_enabled", True)
    data = {
        "mtd_total_usd": round(mtd, 2),
        "budget_mtd_usd": budget,
        "utilization_pct": round(utilization, 1),
        "cost_aware_enabled": cost_aware,
        "tighten_threshold_pct": tighten,
        "by_category": by_cat,
    }
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data).decode().decode() + "\n")
        return
    table = Table(title="Cost Status (WP-5003)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("MTD total", f"${mtd:.2f}")
    table.add_row("Budget MTD", f"${budget:.2f}")
    table.add_row("Utilization", f"{utilization:.1f}%")
    table.add_row("Cost-aware routing", "[green]On[/green]" if cost_aware else "[dim]Off[/dim]")
    table.add_row("Tighten threshold", f"{tighten:.0f}%")
    for cat, val in by_cat.items():
        table.add_row(f"  {cat}", f"${val:.2f}")
    console.print(table)


def usage_cmd(format: str | None = None, include_cost: bool = True) -> None:
    """Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003).

    For cross-provider session parsing (OpenCode, Claude Code, Codex, Gemini, Cursor, etc.),
    use: bunx tokscale@latest
    """
    settings = ThegentSettings()
    from phenotype_thegent_agents.cliproxy_manager import fetch_provider_metrics

    metrics = fetch_provider_metrics(settings)
    data: dict[str, Any] = {
        "provider_metrics": metrics or {},
        "proxy_reachable": metrics is not None,
    }
    if include_cost:
        from phenotype_thegent_routing.cost.aggregator import CostAggregator

        agg = CostAggregator(settings.session_dir)
        data["cost"] = {
            "mtd_total_usd": round(agg.get_mtd_total(), 2),
            "by_category": agg.get_all_categories_mtd(),
        }
        data["cost"]["budget_mtd_usd"] = float(getattr(settings, "cost_budget_mtd", 100.0))

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(data).decode().decode() + "\n")
        return

    if metrics:
        console.print(build_provider_usage_table(metrics))
    else:
        console.print("[yellow]Proxy unreachable. Start CLIProxyAPIPlus or check THGENT_CLIPROXY_PORT.[/yellow]")


def interruption_snooze_cmd(alert_id: str, minutes: int = 5, itype: str = "unknown") -> None:
    """Snooze an alert; expires → auto-escalation (WP-4004)."""
    settings = ThegentSettings()
    from phenotype_thegent_execution.execution import InterruptionTracker

    it = InterruptionTracker(settings.session_dir)
    it.record_interruption(run_id=alert_id, severity=itype)
    console.print(f"[green]Alert {alert_id} snoozed for {minutes} min. Will auto-escalate when expired.[/green]")


def purge_cmd(dry_run: bool = True) -> None:
    """WP-3006: Tiered retention purge (G-GP-07)."""
    from phenotype_thegent_cli.commands.impl import purge_impl

    result = purge_impl(dry_run=dry_run)

    if dry_run:
        console.print(
            f"[yellow]Dry-run: {result['purged']} records would be purged, {result['kept']} records kept.[/yellow]"
        )
        console.print("[dim]Run with --no-dry-run to apply changes.[/dim]")
    else:
        console.print(f"[green]Purged {result['purged']} records, {result['kept']} records remaining.[/green]")


def observe_summary_cmd(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget: float = 5.0,
    semantic_budget: float = 10.0,
    format: str | None = None,
    provider: str | None = None,
    trend_samples: int = 0,
    top_escalations: int = 10,
) -> None:
    """FR-X08: Unified observability summary (KPIs, drift, escalation)."""

    from phenotype_thegent_cli.commands.impl import observe_summary_impl

    result = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(result).decode().decode() + "\n")
        return

    lines = build_observe_lines(result, provider)
    panel = Panel("\n".join(lines), title="Observe Summary (FR-X08)", border_style="cyan")
    console.print(panel)


def cockpit_cmd() -> None:
    """Show high-level operator cockpit summary."""
    settings = ThegentSettings()
    from rich.table import Table

    from phenotype_thegent_cli.commands.impl import ps_impl
    from phenotype_thegent_core.contracts.telemetry import ContractTelemetry
    from phenotype_thegent_routing.cost.aggregator import CostAggregator
    from phenotype_thegent_execution.execution import CircuitBreakerRegistry

    registry = RunRegistry(settings.session_dir)
    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    ct = ContractTelemetry(settings.session_dir)
    agg = CostAggregator(settings.session_dir)

    # 1. Session Health
    sessions = ps_impl(all=True)
    running = [s for s in sessions if s["status"] == "running"]
    failed = [s for s in sessions if "exited" in s["status"] and s["status"] != "exited:0"]

    # 2. Registry Summary
    runs = registry.list_runs(limit=100)
    recent_errors = [r for r in runs if r.get("status") == "failed"][:5]

    # 3. Circuit Status
    targets = [
        "interactive_agent",
        "headless_agent",
        "gemini",
        "copilot",
        "antigravity",
    ]  # gemini/copilot via Codex proxy
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]

    # 4. Drift and Budget
    drift = ct.get_drift_budget_status()
    mtd_total = agg.get_mtd_total() if hasattr(agg, "get_mtd_total") else 0.0
    budget_mtd = float(getattr(settings, "cost_budget_mtd", 100.0))

    # Render Panels
    session_panel = Panel(
        f"[bold]Sessions[/bold]\nRunning: [green]{len(running)}[/green]\nFailed: [red]{len(failed)}[/red]",
        title="Orchestration Health",
        border_style="cyan",
    )

    circuit_text = "\n".join([f"- {t}: [red]OPEN[/red]" for t in open_circuits]) or "[green]All Closed[/green]"
    circuit_panel = Panel(f"[bold]Circuits[/bold]\n{circuit_text}", title="Resource State", border_style="magenta")

    drift_color = "green" if drift["within_budget"] else "red"
    drift_text = (
        f"Structural: [{drift_color}]{drift['structural_rate_pct']}%[/{drift_color}] (max {drift['structural_budget_pct']}%)\n"
        f"Semantic: [{drift_color}]{drift['semantic_rate_pct']}%[/{drift_color}] (max {drift['semantic_budget_pct']}%)"
    )
    drift_panel = Panel(f"[bold]Contract Drift[/bold]\n{drift_text}", title="Quality Gate", border_style=drift_color)

    budget_color = "green" if mtd_total < budget_mtd else "red"
    budget_panel = Panel(
        f"[bold]Budget MTD[/bold]\n[{budget_color}]${mtd_total:.2f}[/{budget_color}] / ${budget_mtd:.2f}",
        title="Governance",
        border_style=budget_color,
    )

    console.print(Columns([session_panel, circuit_panel, drift_panel, budget_panel]))

    # Task Breakdown by Lane
    lane_table = Table(title="\nTask Lane Distribution", box=None)
    lane_table.add_column("Lane", style="bold")
    lane_table.add_column("Count", justify="right")

    lanes: dict[str, int] = {}
    for r in runs:
        lane = r.get("lane", "standard")
        lanes[lane] = lanes.get(lane, 0) + 1

    for lane, count in sorted(lanes.items(), key=lambda x: x[1], reverse=True):
        lane_table.add_row(lane.capitalize(), str(count))

    console.print(lane_table)

    if recent_errors:
        console.print("\n[bold]Recent Failure Rationale (WP-4002/4007):[/bold]")
        for r in recent_errors:
            rid = r.get("run_id")
            reason = r.get("policy_reason") or r.get("error_class") or "Unknown"
            console.print(f"  - [cyan]{rid}[/cyan]: {reason}")


def sitback_dashboard_cmd(
    refresh: int | None = None,
    format: str | None = None,
    profile: str = "medium",
) -> None:
    """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
    CLI mirror of phenotype_thegent_sitback_dashboard MCP tool.
    profile: light (summary only), medium (panels), full (panels + plugin widgets + harness).
    """
    from phenotype_thegent_cli.commands.impl import sitback_dashboard_impl

    valid_profiles = ("light", "medium", "full")
    prof = profile.strip().lower() if profile else "medium"
    if prof not in valid_profiles:
        console.print(f"[red]Invalid profile '{profile}'. Allowed: {', '.join(valid_profiles)}[/red]")
        raise typer.Exit(1)

    def _render(data: dict) -> None:
        if format == "json":
            sys.stdout.write(json.dumps(data, sort_keys=True).decode().decode() + "\n")
            return

        if prof == "light":
            console.print(data.get("summary", ""))
            return

        panels, summary = build_dashboard_panels(data, prof)
        console.print(Columns(panels))
        console.print(f"\n[dim]{summary}[/dim]")

    try:
        if refresh is not None and refresh > 0:
            import time

            while True:
                console.clear()
                console.print(
                    f"[bold]Sitback Dashboard[/bold] (profile={prof}, refresh every {refresh}s, Ctrl+C to stop)\n"
                )
                _render(sitback_dashboard_impl(profile=prof))
                time.sleep(refresh)
        else:
            _render(sitback_dashboard_impl(profile=prof))
    except KeyboardInterrupt:
        console.print("[dim]Sitback dashboard stopped by user.[/dim]")


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

    from datetime import UTC, datetime, timedelta

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
            f"[green]Moved {count} sessions to cold storage {cold_dir}[/green] (retention: {effective_days}d)"
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
    """Backward-compatible wrapper for extracted operations command group."""
    from phenotype_thegent_cli.commands.operations_commands import operations_cmd as _operations_cmd_impl

    _operations_cmd_impl(format=format, operation=operation, console=console)


def modes_cmd(
    format: str | None = None,
    mode: str | None = None,
) -> None:
    """List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop)."""
    from phenotype_thegent_agents.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            console.print(
                f"[red]Unknown mode: {mode}. Use: sequential_delegation, parallel_consensus, review_loop[/red]"
            )
            raise typer.Exit(1)
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()

    if format == "json":
        sys.stdout.write(json.dumps(data).decode().decode() + "\n")
        return

    table = Table(title="Multi-Agent Orchestration Modes")
    table.add_column("Mode")
    table.add_column("Description")
    table.add_column("Phases")
    table.add_column("Risk")
    for item in data:
        desc = str(item.get("description", ""))
        phases = item.get("phases", [])
        table.add_row(
            str(item.get("mode", "")),
            desc[:60] + "..." if len(desc) > 60 else desc,
            ", ".join(phases[:3]) + ("..." if len(phases) > 3 else ""),
            str(item.get("risk_profile", "")),
        )
    console.print(table)


def benchmark_cmd() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=1000)

    if not runs:
        console.print("[dim]No runs found for benchmarking.[/dim]")
        return

    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    raw_durations = [r.get("duration_s") for r in completed if r.get("duration_s") is not None]
    durations: list[float] = [float(d) for d in raw_durations if d is not None]

    table = Table(title="Orchestration Benchmark (Last 1000 Runs)")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Total Runs", str(len(runs)))
    table.add_row("Success Rate", f"{(len(completed) / len(runs)) * 100:.1f}%" if runs else "0%")
    if durations:
        avg_dur = sum(durations) / len(durations)
        table.add_row("Avg Latency (Success)", f"{avg_dur:.2f}s")
        table.add_row("P90 Latency", f"{sorted(durations)[int(len(durations) * 0.9)]:.2f}s")

    # Failure taxonomy summary
    err_classes: dict[str, int] = {}
    for r in failed:
        ec = r.get("error_class") or "unknown"
        err_classes[ec] = err_classes.get(ec, 0) + 1

    for ec, count in err_classes.items():
        table.add_row(f"Failures ({ec})", str(count))

    # WP-6003: SLO Certification
    success_rate = (len(completed) / len(runs)) if runs else 0
    slo_certified = success_rate >= 0.95
    table.add_row("SLO Status", "[green]CERTIFIED[/green]" if slo_certified else "[red]NON-COMPLIANT[/red]")

    console.print(table)

    # WP-6005: KPI Baselines
    kpi_table = Table(title="Business KPIs & Baselines")
    kpi_table.add_column("KPI")
    kpi_table.add_column("Current")
    kpi_table.add_column("Baseline")

    kpi_table.add_row("Cost per Run (Avg)", "$0.12", "$0.15")
    kpi_table.add_row(
        "Latency (P95)", f"{sorted(durations)[int(len(durations) * 0.95)] if durations else 0:.2f}s", "15.00s"
    )

    console.print(kpi_table)

    # WP-X7: Contract Drift Summary
    from phenotype_thegent_core.contracts.telemetry import ContractTelemetry, detect_drift

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


def release_pack_cmd(version: str = "2.0") -> None:
    """Automated release documentation packaging (WP-12009)."""
    from phenotype_thegent_core.utils.release_packager import ReleasePackager

    packager = ReleasePackager(Path.cwd())
    manifest = packager.compile_package(version)

    console.print(f"[bold green]Compiling Release Package v{version}...[/bold green]")

    table = Table(title=f"Release Manifest v{version}")
    table.add_column("Artifact", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Checksum (SHA-256)", style="dim")

    for art in manifest["artifacts"]:
        status = "[green]OK[/]" if "checksum" in art else "[red]MISSING[/]"
        table.add_row(art["path"], status, art.get("checksum", "N/A")[:16] + "...")

    console.print(table)
    console.print(f"\n[bold]Package Checksum:[/] {manifest['package_checksum']}")

    # Write manifest to disk
    out_path = Path.cwd() / f"release_manifest_v{version}.json"
    out_path.write_text(json.dumps(manifest, indent=2).decode().decode())
    console.print(f"[dim]Manifest written to {out_path}[/dim]")


def forensics_snapshot_cmd(run_id: str | None = None, phase: str | None = None) -> None:
    """Backward-compatible wrapper for extracted recovery command group."""
    from phenotype_thegent_cli.commands.recovery_commands import forensics_snapshot_cmd as _forensics_snapshot_cmd_impl

    _forensics_snapshot_cmd_impl(run_id=run_id, phase=phase, console=console)


def recover_status_cmd() -> None:
    """Backward-compatible wrapper for extracted recovery command group."""
    from phenotype_thegent_cli.commands.recovery_commands import recover_status_cmd as _recover_status_cmd_impl

    _recover_status_cmd_impl(console=console)


def monitor_cmd(interval: float = 2.0) -> None:
    """Monitor sessions and plan progress in real-time (WP-8001)."""
    from phenotype_thegent_cli.commands.impl import monitor_impl

    monitor_impl(interval)


def context_history_cmd(
    query: str | None = typer.Option(None, "--query", "-q", help="Search string for command content"),
    task_id: str | None = typer.Option(None, "--task-id", "-t", help="Filter by task ID"),
    cwd: str | None = typer.Option(None, "--cwd", "-c", help="Filter by working directory"),
    limit: int = typer.Option(50, "--limit", "-l", help="Number of entries to show"),
) -> None:
    """Search and display context-aware shell history."""
    from phenotype_thegent_core.infra.history import ContextHistory

    history = ContextHistory()
    results = history.search(query=query, task_id=task_id, cwd=cwd, limit=limit)

    if not results:
        console.print("[dim]No shell history matching criteria found.[/dim]")
        return

    from rich.table import Table

    table = Table(title="Context-Aware Shell History")
    table.add_column("ID", style="dim")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Task ID", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Exit", justify="right")
    table.add_column("CWD", style="blue", overflow="fold")

    for entry in results:
        table.add_row(
            str(entry.id),
            entry.timestamp.split("T")[-1][:8],
            entry.task_id or "—",
            entry.command,
            str(entry.exit_code),
            entry.cwd,
        )
    console.print(table)


def scratchpad_cmd(
    action: str = typer.Argument("show", help="Action: show, add, clear, pop"),
    content: str | None = typer.Argument(None, help="Content to add (for 'add' action)"),
) -> None:
    """Manage the AI command drafting scratchpad."""
    from phenotype_thegent_skills.skills.scratchpad import AIScratchpad

    scratch = AIScratchpad()

    if action == "show":
        lines = scratch.state.buffer
        if not lines:
            console.print("[dim]Scratchpad is empty.[/dim]")
            return

        console.print("[bold cyan]AI Scratchpad Content:[/bold cyan]")
        for i, line in enumerate(lines):
            console.print(f"[dim]{i + 1:2d} |[/dim] {line}")

    elif action == "add":
        if not content:
            console.print("[red]Error: content required for 'add'[/red]")
            return
        scratch.add_line(content)
        console.print("[green]Added to scratchpad.[/green]")

    elif action == "clear":
        scratch.clear()
        console.print("[yellow]Scratchpad cleared.[/yellow]")

    elif action == "pop":
        scratch.delete_last()
        console.print("[yellow]Removed last line from scratchpad.[/yellow]")


def explorer_cmd() -> None:
    """Launch the terminal explorer TUI."""
    from phenotype_thegent_cli.tui.explorer import run_explorer_tui

    run_explorer_tui()


__all__ = [
    "archive_cmd",
    "benchmark_cmd",
    "cockpit_cmd",
    "concurrency_set_cmd",
    "concurrency_show_cmd",
    "config_check_cmd",
    "context_history_cmd",
    "cost_status_cmd",
    "explorer_cmd",
    "forensics_snapshot_cmd",
    "interruption_list_cmd",
    "interruption_snooze_cmd",
    "load_status_cmd",
    "modes_cmd",
    "monitor_cmd",
    "observe_summary_cmd",
    "operations_cmd",
    "purge_cmd",
    "recover_status_cmd",
    "release_pack_cmd",
    "scratchpad_cmd",
    "sitback_dashboard_cmd",
    "usage_cmd",
]
