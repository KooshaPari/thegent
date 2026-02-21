"""Helpers for usage command rich output formatting."""

from __future__ import annotations

from typing import Any

from rich.table import Table


def build_provider_usage_table(metrics: dict[str, dict[str, Any]]) -> Table:
    """Build provider usage table from provider metrics payload."""
    table = Table(title="Provider Usage (CLIProxyAPIPlus)")
    table.add_column("Provider")
    table.add_column("Cost/1k")
    table.add_column("Success %")
    table.add_column("TPS 1m")
    table.add_column("Latency p50")
    for provider_name, metric in sorted(metrics.items()):
        cost = metric.get("cost_per_1k_output") or metric.get("cost_per_1k_input") or "-"
        cost_str = f"${cost:.4f}" if isinstance(cost, (int, float)) else str(cost)
        success_rate = metric.get("success_rate")
        success_rate_str = f"{success_rate * 100:.1f}%" if isinstance(success_rate, (int, float)) else "-"
        tps = metric.get("tps_1m", "-")
        latency = metric.get("latency_p50_ms", "-")
        latency_str = f"{latency}ms" if isinstance(latency, (int, float)) else str(latency)
        table.add_row(provider_name, cost_str, success_rate_str, str(tps), latency_str)
    return table
