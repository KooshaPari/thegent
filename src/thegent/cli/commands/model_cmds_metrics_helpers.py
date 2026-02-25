"""Metrics/cost rendering helpers for model_cmds."""

from __future__ import annotations

import orjson as json
import sys
from typing import Any

from rich.table import Table


def build_index_data(indices: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """Normalize and round index data for stable output."""
    data: dict[str, dict[str, float]] = {}
    for model_id, prov_indices in sorted(indices.items()):
        data[model_id] = {prov: round(idx, 4) for prov, idx in sorted(prov_indices.items())}
    return data


def emit_index_output(
    *,
    data: dict[str, dict[str, float]],
    fmt: str,
    title: str,
    value_label: str,
    console: Any,
) -> None:
    """Emit index output as JSON or rich table."""
    if fmt == "json":
        sys.stdout.write(json.dumps(data).decode() + "\n")
        return

    table = Table(title=title)
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column(value_label)
    for model_id, prov_indices in sorted(data.items()):
        for prov, idx in sorted(prov_indices.items()):
            table.add_row(model_id, prov, f"{idx:.4f}")
    console.print(table)


def collect_metrics_rows(
    *,
    costs: dict[str, dict[str, tuple[float, float]]],
    speed: dict[str, dict[str, float]],
    quality: dict[str, dict[str, float]],
    limit: int,
) -> list[tuple[str, str, str, str, str]]:
    """Collect bounded metrics rows across cost/speed/quality sources."""
    rows: list[tuple[str, str, str, str, str]] = []
    for model_id in sorted(costs.keys()):
        for prov in sorted(costs[model_id].keys()):
            if len(rows) >= limit:
                break
            inp, out = costs[model_id][prov]
            cost_str = f"${inp:.4f}/{out:.4f}"
            sp = speed.get(model_id, {}).get(prov, 0.5)
            ql = quality.get(model_id, {}).get(prov, 0.5)
            rows.append((model_id, prov, cost_str, f"{sp:.3f}", f"{ql:.3f}"))
            if len(rows) >= limit:
                break
        if len(rows) >= limit:
            break
    return rows


def emit_metrics_output(
    *,
    rows: list[tuple[str, str, str, str, str]],
    limit: int,
    fmt: str,
    console: Any,
) -> None:
    """Emit unified metrics output as JSON or rich table."""
    if fmt == "json":
        data: dict[str, Any] = {}
        for model_id, prov, cost_str, sp, ql in rows:
            if model_id not in data:
                data[model_id] = {}
            data[model_id][prov] = {
                "cost_per_1k": cost_str,
                "speed_index": float(sp),
                "quality_index": float(ql),
            }
        sys.stdout.write(json.dumps(data).decode() + "\n")
        return

    table = Table(title="Model-Provider Metrics (cost + speed + quality)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Cost $/1k")
    table.add_column("Speed")
    table.add_column("Quality")
    for model_id, prov, cost_str, sp, ql in rows:
        table.add_row(model_id, prov, cost_str, sp, ql)
    if len(rows) >= limit:
        table.caption = f"Showing first {limit} rows. Use --limit to change."
    console.print(table)


def flatten_cost_values(costs: dict[str, dict[str, tuple[float, float]]]) -> dict[str, dict[str, dict[str, float]]]:
    """Flatten cost tuple format to printable dict structure."""
    data: dict[str, dict[str, dict[str, float]]] = {}
    for model_id, prov_costs in sorted(costs.items()):
        data[model_id] = {
            prov: {"input_per_1k_usd": round(inp, 6), "output_per_1k_usd": round(out, 6)}
            for prov, (inp, out) in sorted(prov_costs.items())
        }
    return data


def emit_cost_values_output(*, data: dict[str, dict[str, dict[str, float]]], fmt: str, console: Any) -> None:
    """Emit cost values as JSON or rich table."""
    if fmt == "json":
        sys.stdout.write(json.dumps(data).decode() + "\n")
        return

    table = Table(title="Model-Provider Cost Values ($/1k tokens)")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Input $/1k")
    table.add_column("Output $/1k")
    for model_id, prov_costs in sorted(data.items()):
        for prov, vals in sorted(prov_costs.items()):
            table.add_row(model_id, prov, f"${vals['input_per_1k_usd']:.6f}", f"${vals['output_per_1k_usd']:.6f}")
    console.print(table)
