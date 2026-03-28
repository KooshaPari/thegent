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
    from phenotype_thegent_core.utils.routing_impl.cost_tracker import get_cost_tracker

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
    from phenotype_thegent_core.utils.routing_impl.harvest import harvest_routing_metrics

    metrics = harvest_routing_metrics(session_id=session_id, output_path=output)
    if not output:
        console.print_json(data=metrics)


@app.command("reset", help="Reset cost and latency tracking.")
def routing_reset():
    from phenotype_thegent_core.utils.routing_impl.cost_tracker import get_cost_tracker

    tracker = get_cost_tracker()
    tracker.clear()
    console.print("[green]Routing stats reset.[/green]")


# ---------------------------------------------------------------------------
# Pareto router (WL-012 Phase 3) subcommands — mounted as `thegent routing pareto-*`
# ---------------------------------------------------------------------------

from phenotype_thegent_cli.commands.router import app as _pareto_router_app  # noqa: E402

app.add_typer(_pareto_router_app, name="pareto", help="Pareto router Phase 3: status, config, and audit verification.")


@app.command("pareto-panel", help="Render a CLI Pareto summary panel from routing_audit.jsonl.")
def routing_pareto_panel(
    audit: Path | None = typer.Option(None, "--audit", "-a", help="Path to routing_audit.jsonl"),
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=500, help="History rows to include"),
    strict: bool = typer.Option(
        False, "--strict/--no-strict", help="Fail on malformed audit lines (default: skip malformed lines)."
    ),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
) -> None:
    from phenotype_thegent_cli.cli.tui.pareto import ParetoTuiSession

    session = ParetoTuiSession(audit_path=audit) if audit else ParetoTuiSession()
    data = session.get_pareto_data(strict=strict)
    history = data.get("history", [])
    parse_errors = data.get("parse_errors", [])
    if isinstance(history, list) and len(history) > limit:
        history = history[-limit:]
    data["history"] = history

    if format == "json":
        console.print_json(data=data)
        return

    table = Table(title="Pareto Frontier Panel")
    table.add_column("Provider", style="cyan")
    table.add_column("Avg Cost USD", style="green")
    table.add_column("Avg Latency ms", style="magenta")
    table.add_column("Count", style="yellow")

    providers = data.get("providers", [])
    if isinstance(providers, list):
        for row in providers:
            if not isinstance(row, dict):
                continue
            table.add_row(
                str(row.get("name", "unknown")),
                f"{float(row.get('avg_cost_usd', 0.0)):.6f}",
                f"{float(row.get('avg_latency_ms', 0.0)):.1f}",
                str(int(row.get("count", 0))),
            )
    console.print(table)

    current = data.get("current")
    if isinstance(current, dict):
        console.print(
            f"[bold]Current:[/bold] provider={current.get('provider')} model={current.get('model')} "
            f"latency_ms={current.get('latency_ms')} cost_usd={current.get('cost_usd')}"
        )

    if parse_errors:
        console.print(f"[yellow]Skipped malformed audit rows: {len(parse_errors)}[/yellow]")
