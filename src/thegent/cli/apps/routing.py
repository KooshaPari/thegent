"""Logical stream: Routing and LiteLLM control."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="LiteLLM, Pareto, and model-first routing control.")


@app.command("status", help="Show current routing status and LiteLLM stats.")
def routing_status(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
):
    from thegent.routing.cost_tracker import get_cost_tracker

    tracker = get_cost_tracker()
    stats = tracker.get_stats()

    if format == "json":
        console.print_json(data=stats.__dict__)
        return

    table = Table(title="Routing & Cost Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Calls", str(stats.total_calls))
    table.add_row("Total Cost (USD)", f"${stats.total_cost_usd:.4f}")
    table.add_row("Daily Spend (USD)", f"${stats.daily_spend_usd:.4f}")
    table.add_row("Total Tokens", str(stats.total_tokens))
    table.add_row("Avg Latency (ms)", f"{stats.avg_latency_ms:.1f}ms")
    table.add_row("Budget Remaining", f"${stats.budget_remaining:.2f}" if stats.budget_remaining is not None else "N/A")
    table.add_row("Errors", str(stats.errors))
    table.add_row("Fallbacks", str(stats.fallbacks))

    console.print(table)


@app.command("harvest", help="Harvest cost/latency data for a session.")
def routing_harvest(
    session_id: str = typer.Option(..., "--session-id", help="Session ID to harvest for"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output path for JSON metrics"),
):
    from thegent.routing.harvest import harvest_routing_metrics

    metrics = harvest_routing_metrics(session_id=session_id, output_path=output)
    if not output:
        console.print_json(data=metrics)


@app.command("reset", help="Reset cost and latency tracking.")
def routing_reset():
    from thegent.routing.cost_tracker import get_cost_tracker

    tracker = get_cost_tracker()
    tracker.clear()
    console.print("[green]Routing stats reset.[/green]")


# ---------------------------------------------------------------------------
# Pareto router (WL-012 Phase 3) subcommands — mounted as `thegent routing pareto-*`
# ---------------------------------------------------------------------------

from thegent.commands.router import app as _pareto_router_app  # noqa: E402

app.add_typer(_pareto_router_app, name="pareto", help="Pareto router Phase 3: status, config, and audit verification.")
