"""Thegent CLI observability commands (observe, cockpit, sitback) - extracted from infra_cmds.py."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys

import typer
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _normalize_output_format,
    console,
)
from thegent.cli.commands.infra_observe_helpers import build_observe_lines
from thegent.cli.commands.infra_sitback_helpers import build_dashboard_panels


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
    from thegent.cli.commands.observability_main_impl import observe_summary_impl  # pyright: ignore[reportMissingImports]

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
        sys.stdout.write(json.dumps(result).decode() + "\n")
        return

    lines = build_observe_lines(result, provider)
    panel = Panel("\n".join(lines), title="Observe Summary (FR-X08)", border_style="cyan")
    console.print(panel)


def cockpit_cmd() -> None:
    """Show high-level operator cockpit summary."""
    settings = ThegentSettings()

    from thegent.cli.commands.session_ops_list_impl import ps_impl  # pyright: ignore[reportMissingImports]
    from thegent.contracts.telemetry import ContractTelemetry
    from thegent.cost.aggregator import CostAggregator
    from thegent.execution import CircuitBreakerRegistry

    registry = RunRegistry(settings.session_dir)
    circuit_breaker = CircuitBreakerRegistry(settings.session_dir)
    ct = ContractTelemetry(settings.session_dir)
    agg = CostAggregator(settings.session_dir)

    sessions = ps_impl(all=True)
    running = [s for s in sessions if s["status"] == "running"]
    failed = [s for s in sessions if "exited" in s["status"] and s["status"] != "exited:0"]

    runs = registry.list_runs(limit=100)
    recent_errors = [r for r in runs if r.get("status") == "failed"][:5]

    targets = [
        "interactive_agent",
        "headless_agent",
        "gemini",
        "copilot",
        "antigravity",
    ]
    open_circuits = [t for t in targets if circuit_breaker.is_open(t)]

    drift = ct.get_drift_budget_status()
    mtd_total = agg.get_mtd_total() if hasattr(agg, "get_mtd_total") else 0.0
    budget_mtd = float(getattr(settings, "cost_budget_mtd", 100.0))

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

    lane_table = Table(title="\nTask Lane Distribution", box=None)
    lane_table.add_column("Lane", style="bold")
    lane_table.add_column("Count", justify="right")

    lanes: dict[str, int] = {}
    for r in runs:
        l = r.get("lane", "standard")
        lanes[l] = lanes.get(l, 0) + 1

    for l, count in sorted(lanes.items(), key=lambda x: x[1], reverse=True):
        lane_table.add_row(l.capitalize(), str(count))

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
    """Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals."""
    from thegent.cli.commands.observability_main_impl import sitback_dashboard_impl  # pyright: ignore[reportMissingImports]

    valid_profiles = ("light", "medium", "full")
    prof = profile.strip().lower() if profile else "medium"
    if prof not in valid_profiles:
        console.print(f"[red]Invalid profile '{profile}'. Allowed: {', '.join(valid_profiles)}[/red]")
        raise typer.Exit(1)

    def _render(data: dict) -> None:  # noqa: ANN001
        if format == "json":
            sys.stdout.write(json.dumps(data, option=json.OPT_SORT_KEYS).decode() + "\n")
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


__all__ = [
    "cockpit_cmd",
    "observe_summary_cmd",
    "sitback_dashboard_cmd",
]
