"""Thegent CLI resource management commands (concurrency, load, cost) - extracted from infra_cmds.py."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import sys
from pathlib import Path
from typing import Any

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _make_load_classifier,
    _normalize_output_format,
    console,
)
from thegent.cli.commands.infra_env_helpers import resolve_env_file, rewrite_max_concurrency_lines


def concurrency_show_cmd(format: str | None = None) -> None:
    """Show current concurrency limit and utilization (WP-5001)."""
    from rich.table import Table

    from thegent.cli.commands.session_ops_list_impl import ps_impl  # pyright: ignore[reportMissingImports]
    from thegent.orchestration.resource.load_based_limits import (
        LimitGateConfig,
        compute_dynamic_limit,
        sample_resources,
    )

    settings = ThegentSettings()
    sessions = ps_impl(all=True)
    running_count = sum(1 for s in sessions if s.get("status") == "running")

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
    import typer

    if limit < 1:
        console.print("[red]Error: Limit must be >= 1[/red]")
        raise typer.Exit(1)
    if limit > 200:
        console.print("[red]Error: Limit must be <= 200[/red]")
        raise typer.Exit(1)

    env_file = resolve_env_file(Path.cwd(), Path(__file__))
    if not env_file.exists():
        console.print("[yellow]Warning: .env file not found. Creating new one.[/yellow]")
        env_file.parent.mkdir(parents=True, exist_ok=True)

    env_lines: list[str] = []
    if env_file.exists():
        env_lines = env_file.read_text(encoding="utf-8").splitlines()

    new_lines, _ = rewrite_max_concurrency_lines(env_lines, limit)

    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    console.print(f"[green]Concurrency limit set to {limit}[/green]")
    console.print("[dim]Note: Restart thegent processes or reload environment for changes to take effect.[/dim]")


def load_status_cmd(format: str | None = None) -> None:
    """Show load classification and safe-mode status (WP-5002)."""
    from rich.table import Table

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
    from rich.table import Table

    settings = ThegentSettings()
    from thegent.cost.aggregator import CostAggregator

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
    """Show plan usage: provider metrics from CLIProxyAPIPlus and cost status (WP-5003)."""
    settings = ThegentSettings()
    from thegent.agents.cliproxy_manager import fetch_provider_metrics
    from thegent.cli.commands.infra_usage_helpers import build_provider_usage_table

    metrics = fetch_provider_metrics(settings)
    data: dict[str, Any] = {
        "provider_metrics": metrics or {},
        "proxy_reachable": metrics is not None,
    }
    if include_cost:
        from thegent.cost.aggregator import CostAggregator

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


__all__ = [
    "concurrency_set_cmd",
    "concurrency_show_cmd",
    "cost_status_cmd",
    "load_status_cmd",
    "usage_cmd",
]
