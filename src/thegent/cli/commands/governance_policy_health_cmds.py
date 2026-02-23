"""Thegent CLI governance policies, contracts, health, and drift detection commands.

Extracted from governance_cmds.py as part of CLI refactoring (WL-124).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import orjson as json
import typer
from rich.panel import Panel
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    _get_health_targets_path,
    _normalize_output_format,
    _resolve_cwd,
    console,
)

# Health policy profiles matching observability_health_impl.py
HEALTH_POLICY_PROFILES: dict[str, dict[str, Any]] = {
    "strict_ci": {"strict": True, "min_healthy_ratio": 1.0},
    "warn_only": {"strict": False, "min_healthy_ratio": 0.0},
    "prod_release": {"strict": True, "min_healthy_ratio": 0.98},
}


def govern_configure_cmd(cd: Path | None = None, force: bool = False) -> None:
    """Bootstrap governance: create contracts/health-targets.json if missing."""
    project_dir = _resolve_cwd(cd) or Path.cwd()
    contracts_dir = project_dir / "contracts"
    health_targets = contracts_dir / "health-targets.json"
    if health_targets.exists() and not force:
        console.print("[green]Govern already configured.[/green]")
        return
    contracts_dir.mkdir(parents=True, exist_ok=True)
    from thegent.cli.commands._cli_shared import _HEALTH_TARGETS_TEMPLATE

    health_targets.write_text(_HEALTH_TARGETS_TEMPLATE, encoding="utf-8")
    console.print("[green]Govern configured.[/green] Run: thegent govern go health")


def govern_go_health_cmd(cd: Path | None = None, format: str | None = None) -> None:
    """Show current health score (composite 0-100, band, per-dimension breakdown)."""
    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    try:
        health_targets_path = _get_health_targets_path(project_dir)
    except FileNotFoundError:
        fmt = _normalize_output_format(format)
        if fmt == "json":
            sys.stdout.write(json.dumps({"configured": False, "hint": "thegent govern configure"}).decode().decode() + "\n")
        else:
            console.print("[yellow]Govern not configured.[/yellow]")
            console.print("[dim]Run: thegent govern configure[/dim]")
        raise typer.Exit(1)

    health_computer = HealthScoreComputer(health_targets_path)
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)
    scan_result = scanner.scan_all()

    dimension_values: dict[str, float] = {}
    for dim_name, dim_scan in scan_result.dimensions.items():
        dimension_values[dim_name] = dim_scan.current_value

    health = health_computer.compute(dimension_values)

    fmt = _normalize_output_format(format)

    if fmt == "json":
        output = {
            "score": health.score,
            "band": health.band.value if hasattr(health, "band") else get_band(health.score).value,
            "dimensions": {},
        }
        for name, dim in health.dimensions.items():
            output["dimensions"][name] = {
                "raw_value": dim.raw_value,
                "normalized": dim.normalized,
                "target": dim.target,
                "status": dim.status.value if hasattr(dim.status, "value") else str(dim.status),
            }
        sys.stdout.write(json.dumps(output, indent=2).decode().decode() + "\n")
        return

    band = get_band(health.score)
    band_color = {
        "excellent": "green",
        "healthy": "cyan",
        "warning": "yellow",
        "critical": "red",
    }.get(band.value, "white")

    table = Table(title="AgilePlus Health Score")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Composite Score", f"[bold]{health.score:.2f}[/bold]")
    table.add_row("Band", f"[{band_color}]{band.value.upper()}[/{band_color}]")
    console.print(table)

    dim_table = Table(title="Dimension Breakdown")
    dim_table.add_column("Dimension")
    dim_table.add_column("Raw")
    dim_table.add_column("Target")
    dim_table.add_column("Normalized")
    dim_table.add_column("Status")

    for name, dim in health.dimensions.items():
        status_color = {
            "excellent": "green",
            "healthy": "cyan",
            "warning": "yellow",
            "critical": "red",
        }.get(dim.status.value if hasattr(dim.status, "value") else str(dim.status), "white")

        dim_table.add_row(
            name,
            f"{dim.raw_value:.2f}",
            f"{dim.target:.2f}",
            f"{dim.normalized:.2%}",
            f"[{status_color}]{dim.status.value if hasattr(dim.status, 'value') else dim.status}[/{status_color}]",
        )
    console.print(dim_table)


def govern_go_status_cmd(cd: Path | None = None) -> None:
    """Show current governance status (state, cycle_id, shutdown_requested)."""
    from thegent.governance.agileplus import AgilePlusLoop
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    loop = AgilePlusLoop(
        project_dir=project_dir,
        health_targets_path=health_targets_path,
        health_threshold=settings.agileplus_health_threshold,
        max_tasks_per_cycle=settings.agileplus_max_tasks_per_cycle,
        max_rerolls=settings.agileplus_max_rerolls,
    )

    table = Table(title="AgilePlus Status")
    table.add_column("Property")
    table.add_column("Value")
    table.add_row("State", f"[bold]{loop.state.value}[/bold]")
    table.add_row("Cycle ID", loop.cycle_id or "[dim]none[/dim]")
    table.add_row(
        "Shutdown Requested",
        "[red]True[/red]" if loop.shutdown_requested else "[green]False[/green]",
    )
    console.print(table)


def govern_go_cycle_cmd(cd: Path | None = None, force: bool = False, format: str | None = None) -> None:
    """Run a single governance cycle."""
    import uuid
    from datetime import UTC, datetime

    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
    started_at = datetime.now(UTC).isoformat()

    console.print(f"[cyan]Starting AgilePlus cycle {cycle_id} (force={force})...[/cyan]")

    health_computer = HealthScoreComputer(health_targets_path)
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)
    scan_result = scanner.scan_all()

    dimension_values: dict[str, float] = {}
    for dim_name, dim_scan in scan_result.dimensions.items():
        dimension_values[dim_name] = dim_scan.current_value

    health = health_computer.compute(dimension_values)
    completed_at = datetime.now(UTC).isoformat()

    should_run = force or health.score < settings.agileplus_health_threshold

    fmt = _normalize_output_format(format)

    if fmt == "json":
        output = {
            "cycle_id": cycle_id,
            "state": "idle" if not should_run else "completed",
            "health_score": health.score,
            "health_band": health.band.value if hasattr(health, "band") else get_band(health.score).value,
            "findings_count": sum(1 for d in dimension_values.values() if d > 0),
            "tasks_planned": 0,
            "tasks_executed": 0,
            "tasks_verified": 0,
            "started_at": started_at,
            "completed_at": completed_at,
            "error": "",
            "skipped": not should_run,
        }
        sys.stdout.write(json.dumps(output, indent=2).decode().decode() + "\n")
        return

    band = get_band(health.score)

    table = Table(title=f"Cycle Result: {cycle_id}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("State", "skipped (healthy)" if not should_run else "completed")
    table.add_row("Health Score", f"{health.score:.2f}")
    table.add_row("Health Band", band.value)
    table.add_row("Findings", str(sum(1 for d in dimension_values.values() if d > 0)))
    table.add_row("Tasks Planned", "0")
    table.add_row("Tasks Executed", "0")
    table.add_row("Tasks Verified", "0")
    table.add_row("Started", started_at)
    table.add_row("Completed", completed_at)

    if not should_run:
        console.print("[dim]Cycle skipped: health score >= threshold[/dim]")
    console.print(table)


def govern_go_watch_cmd(
    cd: Path | None = None,
    interval: int = 300,
    max_cycles: int | None = None,
) -> None:
    """Run continuous governance mode."""
    import time
    import uuid
    from datetime import UTC, datetime

    from thegent.governance.health_score import HealthScoreComputer, get_band
    from thegent.governance.scanner import CodebaseScanner
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    project_dir = _resolve_cwd(cd) or Path.cwd()
    health_targets_path = _get_health_targets_path(project_dir)

    console.print(f"[cyan]Starting continuous governance (interval={interval}s, max_cycles={max_cycles})...[/cyan]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]")

    health_computer = HealthScoreComputer(health_targets_path)
    scanner = CodebaseScanner(project_dir=project_dir, session_dir=settings.session_dir)

    results = []
    cycles_run = 0
    try:
        while max_cycles is None or cycles_run < max_cycles:
            cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
            started_at = datetime.now(UTC).isoformat()

            scan_result = scanner.scan_all()
            dimension_values = {}
            for dim_name, dim_scan in scan_result.dimensions.items():
                dimension_values[dim_name] = dim_scan.current_value

            health = health_computer.compute(dimension_values)
            completed_at = datetime.now(UTC).isoformat()

            results.append(
                {
                    "cycle_id": cycle_id,
                    "health_score": health.score,
                    "health_band": health.band.value if hasattr(health, "band") else get_band(health.score).value,
                    "started_at": started_at,
                    "completed_at": completed_at,
                }
            )

            cycles_run += 1
            console.print(
                f"Cycle {cycles_run} ({cycle_id}): score={health.score:.2f}, band={health.band.value if hasattr(health, 'band') else get_band(health.score).value}"
            )

            if max_cycles is not None and cycles_run >= max_cycles:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")

    console.print(f"\n[green]Completed {len(results)} cycle(s)[/green]")


def policy_show_cmd() -> None:
    """Show active governance policies and thresholds."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    console.print(f"[bold]Active Governance Policies[/bold] (Environment: [cyan]{settings.environment}[/cyan])")

    table = Table(show_header=True)
    table.add_column("Policy Name")
    table.add_column("Rule / Threshold")
    table.add_column("Status")

    table.add_row("Critical Confidence", ">= 0.9", "[green]Active[/green]")
    table.add_row(
        "Production Trust",
        f">= {settings.trust_score_threshold}",
        "[green]Active[/green]" if settings.environment == "production" else "[dim]Inactive[/dim]",
    )
    table.add_row("Agent Restriction", "Block 'unknown' in Prod/Critical", "[green]Active[/green]")
    table.add_row("Audit Signing", "SHA-256 Run Signatures", "[green]Active[/green]")
    table.add_row("Override TTL (WP-3003)", f"{settings.override_ttl_seconds}s", "[green]Active[/green]")

    console.print(table)


def policy_purge_cmd(dry_run: bool = True) -> None:
    """Purge expired history based on tiered retention (WP-3006)."""
    from thegent.execution import RunRegistry
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    res = registry.purge_expired(
        default_days=settings.retention_default_days,
        by_domain=settings.retention_by_domain,
        dry_run=dry_run,
    )
    if dry_run:
        console.print(f"[yellow]Dry run: would purge {res['purged']} records (kept {res['kept']}).[/yellow]")
    else:
        console.print(f"[green]Purged {res['purged']} records (kept {res['kept']}).[/green]")


def policy_check_cmd(agent: str, model: str | None = None, lane: str = "standard", confidence: float = 1.0) -> None:
    """Evaluate a hypothetical run against governance policies (WP-3001)."""
    import uuid
    from pathlib import Path

    from thegent.execution import PolicyEngine, RunMeta, RunRegistry
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    engine = PolicyEngine()
    registry = RunRegistry(settings.session_dir)

    run = RunMeta(
        run_id="policy-check-" + str(uuid.uuid4())[:8],
        correlation_id="check",
        agent=agent,
        model=model or "default",
        mode="write",
        prompt="test prompt",
        cwd=Path.cwd(),
        owner="operator",
        lane=lane,
        confidence=confidence,
    )

    result, reason = engine.evaluate(run, registry=registry)

    color = "green" if result == "allow" else "yellow" if result == "warn" else "red"
    console.print(f"Policy Result: [{color}]{result.upper()}[/{color}]")
    console.print(f"Reason: {reason}")


def contracts_registry_cmd(format: str | None = None) -> None:
    """Show the contract registry and compatibility matrix."""
    from thegent.contracts.registry import get_registry

    registry = get_registry()
    versions = registry.list_versions()

    if format == "json":
        data = []
        for v in versions:
            model_dump = getattr(v, "model_dump", None)
            if callable(model_dump):
                data.append(model_dump())
            elif hasattr(v, "__dict__"):
                data.append(v.__dict__)
            else:
                data.append(v)
        sys.stdout.write(json.dumps(data).decode().decode() + "\n")
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


def contracts_conformance_cmd(
    format: str | None = None,
    check_drift: bool = False,
    drift_window: int = 50,
) -> None:
    """Run provider adapter conformance tests."""
    from thegent.contracts.conformance import run_conformance_suite
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    session_dir = settings.session_dir if check_drift else None
    report = run_conformance_suite(session_dir=session_dir, drift_window=drift_window)

    if format == "json":
        sys.stdout.write(json.dumps(report).decode().decode() + "\n")
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
        raise typer.Exit(1)


def migration_cmd(contract_id: str, version: str, format: str | None = None) -> None:
    """Evaluate migration status for a contract version."""
    from thegent.contracts.migration import MigrationController

    mc = MigrationController()
    res = mc.evaluate_version(contract_id, version)

    if format == "json":
        sys.stdout.write(json.dumps(res).decode().decode() + "\n")
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
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    ct = ContractTelemetry(settings.session_dir)
    issues = ct.detect_drift(window_size=window)
    budget = ct.get_drift_budget_status(
        structural_budget_pct=structural_budget,
        semantic_budget_pct=semantic_budget,
    )

    if format == "json":
        out = {"issues": issues, "budget": budget}
        sys.stdout.write(json.dumps(out).decode().decode() + "\n")
        return

    if not issues and budget["within_budget"]:
        console.print("[green]No significant contract drift detected.[/green]")
        return

    parts = []
    if issues:
        issue_str = "\n".join([f"[red]![/red] {i}" for i in issues])
        parts.append(issue_str)
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


def sweep_cmd(
    drift_window: int = 50,
    include_audit: bool = False,
    format: str | None = None,
) -> None:
    """WP-3005: Policy drift sweep - runs drift detection, budget check, past-SLA escalations."""
    from thegent.cli.commands.observability_main_impl import sweep_impl

    result = sweep_impl(
        drift_window=drift_window,
        include_audit=include_audit,
    )
    fmt = _normalize_output_format(format)
    if fmt == "json":
        out = {k: v for k, v in result.items() if k != "audit" or v is not None}
        if result.get("audit"):
            out["audit"] = result["audit"]
        sys.stdout.write(json.dumps(out).decode().decode() + "\n")
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
        parts.append(
            f"[yellow]Past SLA:[/yellow] {result['past_sla_count']} escalation(s). Run `thegent govern escalate list --past-sla`"
        )
    if result.get("audit") and result["audit"].get("status") not in ("passed", "empty"):
        parts.append(f"[red]Audit:[/red] {result['audit'].get('status', 'failed')}")
    if parts:
        console.print(Panel("\n".join(parts), title="Policy Drift Sweep (WP-3005)", border_style="red"))
    raise typer.Exit(1)


def govern_cost_cmd(owner: str | None = None, days: int = 1, format: str | None = None) -> None:
    """Show daily cost aggregation (FR-GOV-002)."""
    from thegent.cost.aggregator import CostAggregator
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    agg = CostAggregator(settings.session_dir)
    total = agg.daily_total(owner=owner, days=days)

    res = {
        "owner": owner or "all",
        "days": days,
        "total_usd": total,
        "currency": "USD",
    }

    fmt = _normalize_output_format(format)
    if fmt == "json":
        sys.stdout.write(json.dumps(res).decode().decode() + "\n")
        return

    console.print("[bold]Daily Cost Aggregation (FR-GOV-002)[/bold]")
    console.print(f"Owner: [cyan]{owner or 'All Owners'}[/cyan]")
    console.print(f"Days:  [cyan]{days}[/cyan]")
    console.print(f"Total: [green]${total:.4f} USD[/green]")


__all__ = [
    "HEALTH_POLICY_PROFILES",
    "contracts_conformance_cmd",
    "contracts_registry_cmd",
    "drift_cmd",
    "govern_configure_cmd",
    "govern_cost_cmd",
    "govern_go_cycle_cmd",
    "govern_go_health_cmd",
    "govern_go_status_cmd",
    "govern_go_watch_cmd",
    "migration_cmd",
    "policy_check_cmd",
    "policy_purge_cmd",
    "policy_show_cmd",
    "sweep_cmd",
]
