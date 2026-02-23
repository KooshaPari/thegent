"""WL-136 B90-W2-D2: Tooling-surface CLI commands.

Commands extracted from cli.py that belong to the tooling surface
(dev utilities, research, benchmarking, drift monitoring, roadmap generation)
per the WL-136 two-surface split: core runtime vs tooling/test/research.

These commands are NOT part of the core production runtime path. They serve
development, research, and QA workflows. Importing this module from the core
runtime path is forbidden per the WL-136 surface boundary contract.

# @trace WL-136 B90-W2-D2
"""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers (re-used from cli.py via lazy import pattern)
# ---------------------------------------------------------------------------


def _get_settings() -> Any:
    from thegent.config import ThegentSettings

    return ThegentSettings()


def _get_console() -> Any:
    from rich.console import Console

    return Console()


# ---------------------------------------------------------------------------
# benchmark_cmd — dev performance reporting (WP-6001)
# ---------------------------------------------------------------------------


def benchmark_cmd() -> None:
    """Report orchestration performance metrics (WP-6001).

    Tooling surface: dev utility for assessing run latency and SLO compliance.
    Not part of production runtime path.
    """
    from rich.table import Table
    from thegent.execution import RunRegistry

    console = _get_console()
    settings = _get_settings()
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
    table.add_row(
        "Success Rate",
        f"{(len(completed) / len(runs)) * 100:.1f}%" if runs else "0%",
    )
    if durations:
        avg_dur = sum(durations) / len(durations)
        table.add_row("Avg Latency (Success)", f"{avg_dur:.2f}s")
        table.add_row("P90 Latency", f"{sorted(durations)[int(len(durations) * 0.9)]:.2f}s")

    err_classes: dict[str, int] = {}
    for r in failed:
        ec = r.get("error_class") or "unknown"
        err_classes[ec] = err_classes.get(ec, 0) + 1
    for ec, count in err_classes.items():
        table.add_row(f"Failures ({ec})", str(count))

    success_rate = (len(completed) / len(runs)) if runs else 0
    slo_certified = success_rate >= 0.95
    table.add_row(
        "SLO Status",
        "[green]CERTIFIED[/green]" if slo_certified else "[red]NON-COMPLIANT[/red]",
    )
    console.print(table)


# ---------------------------------------------------------------------------
# deep_research_cmd — research utility (DRP)
# ---------------------------------------------------------------------------


def deep_research_cmd(
    query: str,
    subreddits: str | None = None,
    output: Path | None = None,
) -> None:
    """Perform deep research using the Deep Research Protocol (DRP).

    Tooling surface: research utility. Not part of production runtime path.
    """
    from rich.table import Table
    from thegent.skills.deep_research import perform_deep_research

    console = _get_console()
    console.print("[bold cyan]Deep Research Protocol (DRP) starting...[/bold cyan]")
    console.print(f"Query: [green]{query}[/green]")
    if subreddits:
        console.print(f"Subreddits: [green]{subreddits}[/green]")

    sub_list = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else None

    with console.status("[bold yellow]Researching...[/bold yellow]"):
        results = perform_deep_research(query, subreddits=sub_list)

    console.print("\n[bold green]Research complete![/bold green]")
    console.print(f"Found [blue]{len(results['ddg_results'])}[/blue] DDG results")
    console.print(f"Found [blue]{len(results['reddit_results'])}[/blue] Reddit results")
    console.print(f"Found [blue]{len(results['arxiv_results'])}[/blue] Arxiv results")
    console.print(f"Found [blue]{len(results['github_results'])}[/blue] GitHub results")

    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\nResults saved to: [bold]{output}[/bold]")
    else:
        table = Table(title="Top Research Results")
        table.add_column("Source", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("URL", style="blue")
        for res in results["ddg_results"][:3]:
            table.add_row("DDG", res["title"][:50] + "...", res["url"])
        for res in results["reddit_results"][:3]:
            table.add_row("Reddit", res["title"][:50] + "...", res["url"])
        for res in results["arxiv_results"][:3]:
            table.add_row("Arxiv", res["title"][:50] + "...", res["url"])
        for res in results["github_results"][:3]:
            table.add_row("GitHub", res["title"][:50] + "...", res["url"])
        console.print(table)


# ---------------------------------------------------------------------------
# drift_monitor_cmd — multi-provider drift detection (WP-3001)
# ---------------------------------------------------------------------------


def drift_monitor_cmd(prompt: str, agents: list[str]) -> None:
    """Monitor drift across multiple providers for the same prompt (WP-3001).

    Tooling surface: dev QA utility for detecting provider divergence.
    Not part of production runtime path.
    """
    from thegent.cli.commands.impl import run_impl

    console = _get_console()
    results: dict[str, str] = {}
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


# ---------------------------------------------------------------------------
# roadmap_cmd — successor roadmap generation (WP-6004)
# ---------------------------------------------------------------------------


def roadmap_cmd() -> None:
    """Successor roadmap generation (WP-6004).

    Tooling surface: dev/PM utility for gap analysis and next-phase planning.
    Not part of production runtime path.
    """
    from rich.markdown import Markdown
    from thegent.execution import RunRegistry

    console = _get_console()
    settings = _get_settings()
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=100)

    errors = [r for r in runs if r.get("status") in ["failed", "timed_out"]]
    top_errors: dict[str, int] = {}
    for e in errors:
        ec = e.get("error_class", "unknown")
        top_errors[ec] = top_errors.get(ec, 0) + 1

    sorted_errors = sorted(top_errors.items(), key=lambda x: x[1], reverse=True)

    roadmap_md = "# Successor Roadmap: Thegent v2.0\n\n## Gap Analysis Summary\n"
    for ec, count in sorted_errors[:3]:
        roadmap_md += f"- **{ec}**: {count} occurrences.\n"

    console.print(Markdown(roadmap_md))


# ---------------------------------------------------------------------------
# audit_verify_cmd — registry integrity check (tooling/QA utility)
# ---------------------------------------------------------------------------


def audit_verify_cmd(format: str | None = None) -> None:
    """Verify the integrity of the execution run registry.

    Tooling surface: QA/dev audit utility.
    Not part of production runtime path.
    """
    from thegent.execution import Auditor, RunRegistry

    console = _get_console()
    settings = _get_settings()
    registry = RunRegistry(settings.session_dir)
    auditor = Auditor(registry.registry_path)
    res = auditor.verify_registry()

    if format == "json":
        sys.stdout.write(json.dumps(res).decode().decode() + "\n")
        return

    if res["status"] == "passed":
        console.print(f"[green]Audit Passed:[/green] {res['valid_count']} records verified.")
    elif res["status"] == "empty":
        console.print("[dim]Registry empty. No records to verify.[/dim]")
    else:
        console.print(f"[red]Audit Failed:[/red] {res['corrupt_count']} issues found.")
        for issue in res.get("issues", []):
            console.print(f"  - {issue}")


__all__ = [
    "audit_verify_cmd",
    "benchmark_cmd",
    "deep_research_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
]
