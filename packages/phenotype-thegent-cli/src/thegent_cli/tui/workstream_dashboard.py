"""Workstream Dashboard TUI using Textual.

Real-time monitoring dashboard for workstream items, sessions, and auto-launch system.
"""

import logging
from datetime import UTC, datetime
from typing import Any, ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, ProgressBar, Static, TabbedContent, TabPane

from thegent_core.config import ThegentSettings
from thegent_execution.orchestration.resource.load_based_limits import compute_dynamic_limit, sample_resources
from thegent_planning.planning.workstream_db import WorkstreamDB

_log = logging.getLogger(__name__)


class StatsPanel(Static):
    """Statistics panel showing key metrics."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.stats: dict[str, Any] = {}

    def update_stats(self, stats: dict[str, Any]) -> None:
        """Update statistics display."""
        self.stats = stats
        self.update(self._render_stats())

    def _render_stats(self) -> str:
        """Render statistics as formatted text."""
        if not self.stats:
            return "[dim]Loading statistics...[/dim]"

        running = self.stats.get("running", 0)
        completed = self.stats.get("completed", 0)
        pending = self.stats.get("pending", 0)
        claimed = self.stats.get("claimed", 0)
        total_cost = self.stats.get("total_cost", 0.0)
        dynamic_limit = self.stats.get("dynamic_limit", 0)
        available = max(0, dynamic_limit - running)

        return f"""\
[bold]Workstream Statistics[/bold]

Running:     [green]{running}[/green] / {dynamic_limit}
Available:   [cyan]{available}[/cyan]
Completed:   [blue]{completed}[/blue]
Pending:     [yellow]{pending}[/yellow]
Claimed:     [magenta]{claimed}[/magenta]

Total Cost:  [bold]${total_cost:.4f}[/bold]
"""


class SessionsTable(DataTable):
    """Table showing active sessions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("Session ID", "Agent", "Status", "Item ID", "Started", "Lane")

    def update_sessions(self, sessions: list[dict[str, Any]]) -> None:
        """Update sessions table."""
        self.clear()
        for session in sessions[:20]:  # Limit to 20 rows
            session_id = session.get("session_id", "")[:12] + "..."
            agent = session.get("agent", "")
            status = session.get("status", "")
            item_id = (
                session.get("workstream_item_id", "")[:20] + "..."
                if len(session.get("workstream_item_id", "")) > 20
                else session.get("workstream_item_id", "")
            )
            started = session.get("started_at", "")
            if started:
                try:
                    dt = datetime.fromisoformat(started)
                    started = dt.strftime("%H:%M:%S")
                except Exception:
                    pass
            lane = session.get("lane", "")

            # Color code status
            status_style = {
                "running": "[green]",
                "exited": "[dim]",
                "failed": "[red]",
            }.get(status.lower(), "")

            self.add_row(
                session_id,
                agent,
                f"{status_style}{status}[/]",
                item_id or "—",
                started or "—",
                lane or "—",
            )


class WorkstreamItemsTable(DataTable):
    """Table showing workstream items."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("ID", "Status", "Priority", "Source", "Title")

    def update_items(self, items: list[dict[str, Any]]) -> None:
        """Update workstream items table."""
        self.clear()
        for item in items[:30]:  # Limit to 30 rows
            item_id = (
                item.get("item_id", "")[:20] + "..." if len(item.get("item_id", "")) > 20 else item.get("item_id", "")
            )
            status = item.get("status", "")
            priority = item.get("priority", "")
            source = item.get("source", "")
            title = item.get("title", "")[:40] + "..." if len(item.get("title", "")) > 40 else item.get("title", "")

            # Color code status
            status_style = {
                "backlog": "[dim]",
                "pending": "[yellow]",
                "claimed": "[cyan]",
                "completed": "[green]",
                "running": "[green bold]",
            }.get(status.lower(), "")

            self.add_row(
                item_id,
                f"{status_style}{status}[/]",
                priority or "—",
                source or "—",
                title or "—",
            )


class ConcurrencyPanel(Static):
    """Panel showing concurrency limits and usage."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.running = 0
        self.limit = 0

    def update_concurrency(self, running: int, limit: int) -> None:
        """Update concurrency display."""
        self.running = running
        self.limit = limit
        self.update(self._render_concurrency())

    def _render_concurrency(self) -> str:
        """Render concurrency as formatted text."""
        if self.limit == 0:
            return "[dim]Loading concurrency info...[/dim]"

        usage_pct = (self.running / self.limit * 100) if self.limit > 0 else 0
        available = max(0, self.limit - self.running)

        # Color code usage
        if usage_pct >= 90:
            color = "[red]"
        elif usage_pct >= 70:
            color = "[yellow]"
        else:
            color = "[green]"

        return f"""\
[bold]Concurrency[/bold]

Running:     {color}{self.running}[/] / {self.limit}
Available:   [cyan]{available}[/cyan]
Usage:       {color}{usage_pct:.1f}%[/]
"""


class KPIPanel(Static):
    """KPI panel showing TRAFFIC metrics."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kpis: dict[str, Any] = {}

    def update_kpis(self, kpis: dict[str, Any]) -> None:
        """Update KPI display."""
        self.kpis = kpis
        self.update(self._render_kpis())

    def _render_kpis(self) -> str:
        """Render KPIs as formatted text."""
        if not self.kpis:
            return "[dim]Loading KPIs...[/dim]"

        return f"""\
[bold]TRAFFIC KPIs[/bold]

Throughput:  [green]{self.kpis.get("throughput", 0):.1f}/hr[/green]
Reliability: [cyan]{self.kpis.get("reliability", 1.0):.1%}[/cyan]
Finance:     [yellow]${self.kpis.get("finance", 0.0):.2f}[/yellow]
Fatigue:     [magenta]{self.kpis.get("fatigue", 0.0):.1%}[/magenta]
Integrity:   [blue]{self.kpis.get("integrity", 1.0):.1%}[/blue]
"""


class ReputationTable(DataTable):
    """Table showing agent reputation scores."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("Agent", "Trust Score", "Status")

    def update_scores(self, scores: dict[str, float]) -> None:
        """Update reputation scores table."""
        self.clear()
        for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            status = "Trusted" if score >= 0.7 else ("Probation" if score >= 0.3 else "Untrusted")
            status_color = "[green]" if score >= 0.7 else ("[yellow]" if score >= 0.3 else "[red]")
            self.add_row(agent, f"{score:.2f}", f"{status_color}{status}[/]")


class DependenciesTable(DataTable):
    """Table showing item dependencies."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("Item ID", "Depends On", "Status")

    def update_dependencies(self, deps: list[dict[str, Any]]) -> None:
        """Update dependencies table."""
        self.clear()
        for d in deps:
            item_id = d.get("item_id", "")[:20]
            dep_id = d.get("depends_on_item_id", "")[:20]
            satisfied = d.get("satisfied_at") is not None
            status = "[green]Satisfied[/]" if satisfied else "[yellow]Pending[/]"
            self.add_row(item_id, dep_id, status)


class XPTable(DataTable):
    """Table showing agent XP and levels."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_columns("Agent", "XP", "Level", "Trust Score")

    def update_xp(self, xp_data: list[dict[str, Any]]) -> None:
        """Update XP table."""
        self.clear()
        for entry in xp_data:
            self.add_row(
                str(entry.get("agent_id", "")),
                str(entry.get("xp", 0)),
                str(entry.get("level", 1)),
                f"{entry.get('trust_score', 1.0):.2f}",
            )


class GardenerPanel(Static):
    """Panel showing auto-launch system health and gardening status."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.health_data: dict[str, Any] = {}

    def update_health(self, health_data: dict[str, Any]) -> None:
        """Update health display."""
        self.health_data = health_data
        self.update(self._render_health())

    def _render_health(self) -> str:
        """Render health as formatted text."""
        if not self.health_data:
            return "[dim]Loading health info...[/dim]"

        score = self.health_data.get("health_score", 100)
        color = "[green]" if score >= 90 else ("[yellow]" if score >= 70 else "[red]")

        return f"""\
[bold]System Health[/bold]

Health Score: {color}{score}%[/]
Sync Status:  [green]OK[/green]
DB Status:    [green]Connected[/green]
Pending Fixes: [yellow]{self.health_data.get("pending_fixes", 0)}[/yellow]
Last Cycle:   {self.health_data.get("last_cycle", "—")}
"""


class WorkstreamDashboard(App):
    """Real-time workstream monitoring dashboard."""

    CSS = """
    StatsPanel, ConcurrencyPanel, KPIPanel {
        height: 12;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    .section-header {
        background: $primary;
        color: $on-primary;
        padding: 0 1;
        margin-top: 1;
    }

    DataTable {
        height: 1fr;
        border: tall $primary;
    }

    #progress-container {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    """

    BINDINGS: ClassVar = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("g", "garden", "Garden"),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.settings = ThegentSettings()
        self.db = WorkstreamDB(settings=self.settings)
        self.refresh_interval = 2.0
        try:
            from thegent_cli.ux.kpis import KPIDashboard

            self.kpi_dashboard = KPIDashboard(self.settings)
        except Exception:
            self.kpi_dashboard = None

        from thegent_audit.economy.reputation import ReputationManager

        self.reputation_manager = ReputationManager(db_path=self.db.db_path)

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        yield Header(show_clock=True)

        with TabbedContent():
            with TabPane("Overview", id="overview"):
                with Horizontal():
                    with Vertical(id="left-sidebar"):
                        yield StatsPanel(id="stats")
                        yield ConcurrencyPanel(id="concurrency")
                        yield KPIPanel(id="kpis")

                    with Vertical(id="main-content"):
                        yield Static("[bold]Active Sessions[/bold]", classes="section-header")
                        yield SessionsTable(id="sessions")
                        yield Static("[bold]Workstream Items[/bold]", classes="section-header")
                        yield WorkstreamItemsTable(id="items")

            with TabPane("Costs", id="costs-tab"):
                yield Static("[bold]Cost History[/bold]", classes="section-header")
                yield DataTable(id="costs-history")

            with TabPane("Reputation", id="reputation-tab"):
                yield Static("[bold]Agent Reputation Scores[/bold]", classes="section-header")
                yield ReputationTable(id="reputation-table")

            with TabPane("Dependencies", id="deps-tab"):
                yield Static("[bold]Item Dependencies[/bold]", classes="section-header")
                yield DependenciesTable(id="deps-table")

            with TabPane("XP & Levels", id="xp-tab"):
                yield Static("[bold]Agent XP & Levels[/bold]", classes="section-header")
                yield XPTable(id="xp-table")

            with TabPane("Violations", id="violations-tab"):
                yield Static("[bold]Constitutional Violations[/bold]", classes="section-header")
                yield DataTable(id="violations-table")

            with TabPane("Audit Log", id="events-tab"):
                yield Static("[bold]Auto-Launch Audit Log[/bold]", classes="section-header")
                yield DataTable(id="events-table")

            with TabPane("Gardener", id="gardener-tab"):
                yield Static("[bold]Auto-Launch System Health[/bold]", classes="section-header")
                yield GardenerPanel(id="gardener-panel")
                yield Static("[bold]Gardening Tasks[/bold]", classes="section-header")
                yield DataTable(id="gardening-tasks")

        with Horizontal(id="progress-container"):
            yield Static("System Load: ")
            yield ProgressBar(id="progress", show_eta=True)

        yield Footer()

    def on_mount(self) -> None:
        """Initialize dashboard on mount."""
        # Initialize additional tables
        costs_table = self.query_one("#costs-history", DataTable)
        costs_table.add_columns("Period", "Cost ($)", "Tasks", "Avg/Task")

        violations_table = self.query_one("#violations-table", DataTable)
        violations_table.add_columns("Item ID", "Principle", "Reason", "Remediation", "Timestamp")

        events_table = self.query_one("#events-table", DataTable)
        events_table.add_columns("Timestamp", "Event", "Item ID", "Session ID")

        gardening_table = self.query_one("#gardening-tasks", DataTable)
        gardening_table.add_columns("ID", "Title", "Status", "Priority")

        self.set_interval(self.refresh_interval, self.refresh_data)
        self.refresh_data()

    @work(exclusive=False)
    async def action_garden(self) -> None:
        """Run gardening cycle from dashboard."""
        self.notify("Starting gardening cycle...", severity="information")
        try:
            from thegent_planning.planning.auto_launch import AutoLaunchSystem

            launcher = AutoLaunchSystem(self.settings)
            await launcher.run_gardening_cycle()
            self.notify("Gardening cycle completed", severity="information")
            self.refresh_data()
        except Exception as e:
            self.notify(f"Gardening failed: {e}", severity="error")

    @work(exclusive=False)
    async def refresh_data(self) -> None:
        """Refresh dashboard data."""
        try:
            # Get statistics
            stats = self.db.get_statistics()

            # Get dynamic limit
            snapshot = sample_resources()
            current_running = stats.get("running", 0)
            dynamic_limit, _ = compute_dynamic_limit(snapshot)
            stats["dynamic_limit"] = dynamic_limit

            # Update panels
            self.query_one("#stats", StatsPanel).update_stats(stats)
            self.query_one("#concurrency", ConcurrencyPanel).update_concurrency(current_running, dynamic_limit)

            if self.kpi_dashboard:
                kpis = self.kpi_dashboard.get_metrics()
                self.query_one("#kpis", KPIPanel).update_kpis(kpis)

            # Update Reputation
            scores = self.reputation_manager.get_all_scores()
            self.query_one("#reputation-table", ReputationTable).update_scores(scores)

            # Update Dependencies
            deps = self.db.execute_query("SELECT * FROM dependencies LIMIT 50")
            self.query_one("#deps-table", DependenciesTable).update_dependencies(deps)

            # Update XP
            xp_data = self.db.get_top_agents()
            self.query_one("#xp-table", XPTable).update_xp(xp_data)

            # Update sessions
            sessions = self.db.execute_query(
                "SELECT session_id, agent, status, workstream_item_id, started_at, lane "
                "FROM sessions WHERE status = 'running' ORDER BY started_at DESC LIMIT 20"
            )
            self.query_one("#sessions", SessionsTable).update_sessions(sessions)

            # Update items
            items = self.db.execute_query(
                "SELECT item_id, status, priority, source, title FROM workstream_items "
                "ORDER BY CASE status WHEN 'running' THEN 1 WHEN 'claimed' THEN 2 WHEN 'backlog' THEN 3 WHEN 'pending' THEN 3 ELSE 4 END, "
                "CASE priority WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 WHEN 'P2' THEN 3 ELSE 4 END LIMIT 30"
            )
            self.query_one("#items", WorkstreamItemsTable).update_items(items)

            # Update costs history
            costs = self.db.get_recent_costs(limit=20)
            costs_table = self.query_one("#costs-history", DataTable)
            costs_table.clear()
            for c in costs:
                costs_table.add_row(
                    str(c.get("period", "")),
                    f"{c.get('cost_usd', 0.0):.4f}",
                    str(c.get("task_count", 0)),
                    f"{c.get('avg_per_task', 0.0):.4f}",
                )

            # Update violations
            violations = self.db.execute_query(
                "SELECT item_id, principle_id, reason, remediation, timestamp "
                "FROM constitutional_violations ORDER BY timestamp DESC LIMIT 20"
            )
            v_table = self.query_one("#violations-table", DataTable)
            v_table.clear()
            for v in violations:
                v_table.add_row(
                    v.get("item_id", "")[:15],
                    v.get("principle_id", ""),
                    v.get("reason", "")[:30] + "...",
                    v.get("remediation", "")[:30] + "...",
                    v.get("timestamp", "")[11:19],
                )

            # Update events
            events = self.db.execute_query(
                "SELECT timestamp, event_type, item_id, session_id FROM auto_launch_events "
                "ORDER BY timestamp DESC LIMIT 20"
            )
            e_table = self.query_one("#events-table", DataTable)
            e_table.clear()
            for e in events:
                e_table.add_row(
                    e.get("timestamp", "")[11:19],
                    e.get("event_type", ""),
                    e.get("item_id", "—")[:15],
                    e.get("session_id", "—")[:12],
                )

            # Update Gardener
            # Heuristic health score
            reliability = stats.get("success_rate", 100.0)
            pending_fixes = self.db.execute_query("SELECT COUNT(*) FROM backlog_items WHERE status = 'open'")[0][
                "COUNT(*)"
            ]
            health_score = int(reliability * 0.8 + (100 - min(100, pending_fixes * 10)) * 0.2)

            self.query_one("#gardener-panel", GardenerPanel).update_health(
                {
                    "health_score": health_score,
                    "pending_fixes": pending_fixes,
                    "last_cycle": datetime.now(UTC).strftime("%H:%M:%S"),
                }
            )

            garden_tasks = self.db.execute_query(
                "SELECT item_id, title, status, priority FROM workstream_items "
                "WHERE source = 'gardening' ORDER BY priority ASC LIMIT 10"
            )
            g_table = self.query_one("#gardening-tasks", DataTable)
            g_table.clear()
            for gt in garden_tasks:
                g_table.add_row(
                    gt.get("item_id", "")[:15], gt.get("title", "")[:40], gt.get("status", ""), gt.get("priority", "")
                )

            # Update progress bar
            self.query_one("#progress", ProgressBar).update(progress=current_running, total=dynamic_limit)

        except Exception as e:
            _log.error(f"Error refreshing dashboard: {e}", exc_info=True)
            self.notify(f"Refresh error: {e}", severity="error")

    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()

    async def action_quit(self) -> None:
        """Quit the dashboard."""
        self.exit()


def run_dashboard() -> None:
    """Run the workstream dashboard."""
    app = WorkstreamDashboard()
    app.run()
