"""CLI commands for swarm management — per-owner usage tracking (swarm-usage-tracking)."""

from __future__ import annotations

import orjson as json
import logging
from pathlib import Path

import typer

app = typer.Typer(help="Swarm management: concurrency, usage, and fairness")
logger = logging.getLogger(__name__)


@app.command("usage")
def swarm_usage(
    session_dir: str | None = typer.Option(None, "--session-dir", "-d", help="Session directory (default: cwd)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter to a specific owner"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich | json"),
) -> None:
    """Show per-owner concurrency usage statistics.

    Displays active slot counts, total runs, and average elapsed time for
    each owner (agent/user/project) tracked by the ConcurrencyController.
    """
    from phenotype_thegent_core.config import ThegentSettings
    from phenotype_thegent_execution.execution import ConcurrencyController
    from phenotype_thegent_execution.orchestration.resource.load_based_limits import get_usage_tracker

    settings = ThegentSettings()
    session_path = Path(session_dir) if session_dir else Path(settings.session_dir)
    if not session_path.exists():
        session_path = Path.cwd()

    # Instantiate the controller so it attaches to the shared singleton tracker.
    # The tracker is module-level so even if the controller is freshly created
    # it shares state with any other in-process controller instances.
    ConcurrencyController(
        session_dir=session_path,
        max_concurrency=settings.max_concurrency,
        use_load_based=settings.concurrency_load_based,
    )

    tracker = get_usage_tracker()
    all_stats = tracker.get_all_stats()

    if owner is not None:
        # Filter to requested owner; include even if unseen (zero stats).
        from phenotype_thegent_execution.orchestration.resource.load_based_limits import OwnerStats

        all_stats = {owner: all_stats.get(owner, OwnerStats(owner=owner))}

    if format == "json":
        payload = {o: s.to_dict() for o, s in all_stats.items()}
        typer.echo(json.dumps(payload, indent=2))
        return

    # Rich table output
    from rich.console import Console
    from rich.table import Table

    console = Console()

    if not all_stats:
        console.print("[yellow]No usage data recorded yet.[/yellow]")
        return

    table = Table(title="Swarm Usage — Per-Owner Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Owner", style="cyan", no_wrap=True)
    table.add_column("Active Slots", justify="right", style="green")
    table.add_column("Total Runs", justify="right", style="blue")
    table.add_column("Avg Elapsed (ms)", justify="right", style="magenta")
    table.add_column("Total Elapsed (ms)", justify="right", style="dim")

    for o, stats in sorted(all_stats.items()):
        table.add_row(
            o,
            str(stats.active_count),
            str(stats.total_runs),
            f"{stats.avg_elapsed_ms:.1f}",
            f"{stats.total_elapsed_ms:.1f}",
        )

    console.print(table)
