"""Routing and Cost Dashboard TUI component."""

import logging
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Static

from thegent.utils.routing_impl.cost_tracker import get_cost_tracker

_log = logging.getLogger(__name__)


class RoutingStatsPanel(Static):
    """Statistics panel showing routing metrics."""

    def __init__(self, *args: Any, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stats: dict[str, Any] = {}

    def update_stats(self, stats: dict[str, Any]) -> None:
        """Update statistics display."""
        self.stats = stats
        self.update(self._render_stats())

    def _render_stats(self) -> str:
        """Render statistics as formatted text."""
        if not self.stats:
            return "[dim]Loading routing stats...[/dim]"

        total_calls = self.stats.get("total_calls", 0)
        total_cost = self.stats.get("total_cost_usd", 0.0)
        daily_spend = self.stats.get("daily_spend_usd", 0.0)
        avg_latency = self.stats.get("avg_latency_ms", 0.0)
        budget = self.stats.get("budget_remaining")

        budget_str = f"${budget:.2f}" if budget is not None else "N/A"

        return f"""\
[bold]Routing & Cost Statistics[/bold]

Total Calls: [green]{total_calls}[/green]
Total Cost:  [bold]${total_cost:.4f}[/bold]
Daily Spend: [yellow]${daily_spend:.4f}[/yellow]
Avg Latency: [cyan]{avg_latency:.1f}ms[/cyan]
Budget Rem:  [magenta]{budget_str}[/magenta]
"""


class RoutingTable(DataTable):
    """Table showing recent routing events."""

    def __init__(self, *args: Any, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("Time", "Model", "Provider", "Cost", "Latency")

    def update_entries(self, entries: list[dict[str, Any]]) -> None:
        """Update routing table."""
        self.clear()
        for entry in reversed(entries[-20:]):  # Last 20 entries
            ts = entry.get("timestamp", "")
            if "T" in ts:
                ts = ts.split("T")[1][:8]

            model = entry.get("model", "")
            provider = entry.get("provider", "")
            cost = f"${entry.get('cost_usd', 0.0):.4f}"
            latency = f"{entry.get('latency_ms', 0.0):.0f}ms"

            self.add_row(ts, model, provider, cost, latency)


class RoutingDashboard(Vertical):
    """Routing dashboard component."""

    def compose(self) -> ComposeResult:
        """Compose the routing dashboard."""
        with Horizontal(id="routing-top-row"):
            yield RoutingStatsPanel(id="routing-stats")

        yield Static("[bold]Recent Routing Events[/bold]", classes="section-header")
        yield RoutingTable(id="routing-table")

    def on_mount(self) -> None:
        """Initialize on mount."""
        self.set_timer(2.0, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh routing data."""
        try:
            tracker = get_cost_tracker()
            stats = tracker.get_stats()

            self.query_one("#routing-stats", RoutingStatsPanel).update_stats(stats.__dict__)

            # Load entries from log file for the table
            entries = []
            if tracker.log_path.exists():
                import json

                with tracker.log_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entries.append(json.loads(line))
                        except:  # noqa: PERF203, E722 - intentional per-line error handling for malformed JSON
                            continue

            self.query_one("#routing-table", RoutingTable).update_entries(entries)
        except Exception as e:
            _log.error(f"Error refreshing routing dashboard: {e}")
