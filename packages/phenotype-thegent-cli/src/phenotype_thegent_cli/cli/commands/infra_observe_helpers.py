"""Helpers for observe summary rendering."""

from __future__ import annotations

import orjson as json
from typing import Any


def build_observe_lines(result: dict[str, Any], provider: str | None) -> list[str]:
    """Build human-readable lines for observe summary panel."""
    kpis = result["kpis"]
    drift = result["drift"]
    escalation = result["escalation"]
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
        f"[bold]Escalation[/bold]: backlog={escalation['backlog_count']} past-sla={escalation['past_sla_count']}",
    ]
    top_rows = escalation.get("top_escalations", [])
    for item in top_rows[:3]:
        if not isinstance(item, dict):
            continue
        owner = item.get("owner") or "—"
        minutes = item.get("minutes_overdue")
        remaining = item.get("minutes_remaining")
        if item.get("past_sla"):
            timing = f"overdue={minutes}m"
        elif remaining is not None:
            timing = f"remaining={remaining}m"
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
    if result.get("trend_summary"):
        trend = result["trend_summary"]
        lines.append(
            "[bold]Trend[/bold]: "
            f"enabled={trend.get('enabled', False)} "
            f"trend_samples_requested={trend.get('trend_samples_requested', 0)} "
            f"trend_effective_samples={trend.get('trend_effective_samples', 0)} "
            f"history={trend.get('history_sample_count', 0)} "
            f"baseline={trend.get('baseline_available', False)} "
            f"health={trend.get('trend_snapshot_health', 'disabled')}"
        )
    if result.get("generated_query"):
        lines.append(f"generated_query={json.dumps(result['generated_query']).decode()}")
    return lines
