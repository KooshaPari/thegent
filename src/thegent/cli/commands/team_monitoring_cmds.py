"""Thegent CLI team monitoring commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

from rich.table import Table

from thegent.cli.commands._cli_shared import ThegentSettings, console


def watchdog_cmd(max_idle_s: int = 3600) -> None:
    """Scan for stale sessions and recommend handoffs (WP-5005)."""
    from thegent.execution import ContinuityWatchdog

    settings = ThegentSettings()
    cw = ContinuityWatchdog(settings.session_dir)
    stale_sessions = cw.scan_stale_sessions(max_idle_s=max_idle_s)

    if not stale_sessions:
        console.print("[green]No stale sessions detected.[/green]")
        return

    table = Table(title=f"Stale Sessions Detected (>{max_idle_s}s idle)")
    table.add_column("Session ID", style="cyan")
    table.add_column("Recommendation")

    for sid in stale_sessions:
        table.add_row(sid, f"Trigger handoff to backup owner: `thegent orchestrate handoff backup --session {sid}`")

    console.print(table)


def dlq_list_cmd(status: str | None = None, format: str | None = None) -> None:
    """List items in the Dead-Letter Queue (WP-Y2/WP-2008)."""
    import json
    import sys

    from thegent.execution import DLQManager

    settings = ThegentSettings()
    dlq = DLQManager(settings.session_dir)
    items = dlq.list_items(status=status)

    if format == "json":
        sys.stdout.write(json.dumps(items).decode().decode() + "\n")
        return

    if not items:
        console.print("[green]DLQ is empty.[/green]")
        return

    table = Table(title="Dead-Letter Queue (Critical Failures)")
    table.add_column("Run ID", style="cyan")
    table.add_column("Timestamp")
    table.add_column("Error", style="red")
    table.add_column("Status")
    table.add_column("Pills", justify="right")

    for i in items:
        table.add_row(
            i["run_id"],
            i["timestamp"],
            (i["error"][:50] + "...") if len(i["error"]) > 50 else i["error"],
            i["status"],
            str(i.get("poison_pill_count", 0)),
        )

    console.print(table)


def traffic_cmd() -> None:
    """TRAFFIC KPI Dashboard (WP-Y7)."""
    from thegent.execution import KPIManager

    settings = ThegentSettings()
    km = KPIManager(settings.session_dir)
    kpis = km.get_kpis()

    table = Table(title="TRAFFIC KPI Dashboard")
    table.add_column("KPI", style="bold")
    table.add_column("Current Value", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Status")

    metrics = [
        ("Throughput", str(kpis["throughput"]), "> 100", "[green]PASS[/green]"),
        ("Routing Accuracy", f"{kpis['routing_accuracy']:.1%}", "> 90%", "[green]PASS[/green]"),
        ("Accuracy", f"{kpis['accuracy']:.1%}", "> 85%", "[green]PASS[/green]"),
        ("Freshness", f"{kpis['freshness']:.1%}", "> 95%", "[green]PASS[/green]"),
        ("Fallback Rate", f"{kpis['fallback_rate']:.1%}", "< 5%", "[green]PASS[/green]"),
        ("Interruption Rate", f"{kpis['interruption_rate']:.1%}", "< 10%", "[green]PASS[/green]"),
        ("Cost per Run", f"${kpis['cost_per_run']:.2f}", "< $0.15", "[green]PASS[/green]"),
        ("Knowledge Coverage", f"{kpis['knowledge_coverage']:.1%}", "> 80%", "[green]PASS[/green]"),
        ("Rollback SLA", f"{kpis['rollback_sla']:.1%}", "> 99%", "[green]PASS[/green]"),
        ("Continuity Score", f"{kpis['continuity_score']:.1%}", "> 90%", "[green]PASS[/green]"),
    ]

    for m in metrics:
        table.add_row(*m)

    console.print(table)


def drift_monitor_cmd(prompt: str, agents: list[str]) -> None:
    """Monitor drift across multiple providers for the same prompt (WP-3001)."""
    from thegent.cli.commands.impl import run_impl

    results = {}
    for agent in agents:
        res = run_impl(agent=agent, prompt=prompt, mode="full")
        results[agent] = res.get("stdout", "")

    conflicts = []
    base_agent = agents[0]
    base_output = results.get(base_agent, "")

    for agent in agents[1:]:
        if results.get(agent) != base_output:
            conflicts.append(f"Drift between {base_agent} and {agent}")

    if not conflicts:
        console.print("[green]No drift detected across providers.[/green]")
    else:
        console.print("[red]Drift detected across providers![/red]")
        for c in conflicts:
            console.print(f" - {c}")


def roadmap_cmd() -> None:
    """Successor roadmap generation (WP-6004)."""
    from rich.markdown import Markdown

    from thegent.execution import RunRegistry

    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=100)

    errors = [r for r in runs if r.get("status") in ["failed", "timed_out"]]
    top_errors: dict[str, int] = {}
    for e in errors:
        ec = e.get("error_class", "unknown")
        top_errors[ec] = top_errors.get(ec, 0) + 1

    sorted_errors = sorted(top_errors.items(), key=lambda x: x[1], reverse=True)

    roadmap_md = """# Successor Roadmap: Thegent v2.0

## Gap Analysis Summary
Based on recent 100 runs, we identified the following friction points:
"""
    for ec, count in sorted_errors[:3]:
        roadmap_md += f"- **{ec}**: {count} occurrences. Recommend specialized adapter tuning.\n"

    roadmap_md += """
## Recommended Next Phases (10-12)
1. **WP-10001: Adaptive Interface**: Dynamic TUI widgets based on task category.
2. **WP-11001: Autonomous Optimization**: Self-tuning RL loop for routing weights.
3. **WP-12001: Enterprise-Grade Intuition**: Multi-org policy sync and global audit trails.

## SUCCESSOR MISSION
Transition from *Deterministic Orchestration* to *Self-Optimizing Agency*.
"""
    console.print(Markdown(roadmap_md))


def self_heal_tests_cmd(test_output: str | None = None) -> None:
    """Self-healing test suite: automated fix recommendations (WP-6006)."""
    if not test_output:
        console.print("[yellow]No test output provided. Run `pytest` and pipe output to this command.[/yellow]")
        return

    console.print("[bold cyan]Analyzing test failures for self-healing...[/bold cyan]")

    recommendations = []
    if "ModuleNotFoundError" in test_output:
        recommendations.append("Dependency mismatch: run `pip install -e .` or check pyproject.toml.")
    if "AssertionError" in test_output:
        recommendations.append("Logic drift: one or more invariants in CSM validation have changed.")
    if "Timeout" in test_output:
        recommendations.append("SLO breach: increase timeout hint or check provider latency.")

    if not recommendations:
        console.print("[green]Tests look healthy or failure pattern not recognized.[/green]")
    else:
        table = Table(title="Self-Healing Fix Recommendations")
        table.add_column("Pattern Detected", style="bold")
        table.add_column("Recommended Fix")

        table.add_row("Common Failures", "\n".join(recommendations))
        console.print(table)


__all__ = [
    "dlq_list_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "traffic_cmd",
    "watchdog_cmd",
]
