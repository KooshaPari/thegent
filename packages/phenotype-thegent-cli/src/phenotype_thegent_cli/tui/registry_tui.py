"""Agent Registry TUI using Textual (WP-9000)."""

import asyncio
import logging
from typing import Any, ClassVar

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
)

from phenotype_thegent_cli.cli.commands.impl import logs_impl, ps_impl, session_send_impl

_log = logging.getLogger(__name__)


class SessionDetails(Static):
    """Details panel for a selected session."""

    def update_details(self, session: dict[str, Any]) -> None:
        interactivity = session.get("interactivity", "unknown")
        attach_hint = ""
        if interactivity in {"tmux", "headless-holdpty"}:
            attach_hint = "\n[bold yellow]Attach:[/] thegent session attach " + session.get("id", "")

        self.update(
            f"[bold cyan]ID:[/] {session.get('id')}\n"
            f"[bold cyan]Agent:[/] {session.get('agent')}\n"
            f"[bold cyan]Owner:[/] {session.get('owner')}\n"
            f"[bold cyan]Status:[/] {session.get('status')}\n"
            f"[bold cyan]Started:[/] {session.get('started_at_utc')}\n"
            f"[bold cyan]Source:[/] {session.get('source')}\n"
            f"[bold cyan]Mode:[/] {interactivity}"
            f"{attach_hint}"
        )


class RegistryTUI(App):
    """Unified Agent Registry TUI."""

    TITLE = "thegent — Agent Registry"
    SUBTITLE = "Interactive Session Management"
    CSS = """
    #sidebar {
        width: 40;
        border-right: solid $accent;
    }
    #main-content {
        width: 1fr;
    }
    #log-view {
        height: 1fr;
        border: solid $accent;
    }
    #input-container {
        height: 3;
        border-top: solid $accent;
    }
    .section-header {
        background: $accent;
        color: $text;
        padding: 0 1;
        bold: True;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("r", "refresh", "Refresh"),
        ("a", "toggle_all", "All Owners"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_all = False
        self.selected_session_id: str | None = None
        self.sessions: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static(" Sessions ", classes="section-header")
                yield DataTable(id="session-list")
                yield Static(" Details ", classes="section-header")
                yield SessionDetails(id="session-details")

            with Vertical(id="main-content"):
                with TabbedContent():
                    with TabPane("Logs", id="logs-tab"):
                        yield RichLog(id="log-view", highlight=True, markup=True)
                    with TabPane("Chat", id="chat-tab"):
                        yield RichLog(id="chat-view", highlight=True, markup=True)
                    with TabPane("Audit", id="audit-tab"):
                        yield RichLog(id="audit-view", highlight=True, markup=True)

                with Horizontal(id="input-container"):
                    yield Input(placeholder="Type message to session...", id="message-input")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#session-list", DataTable)
        table.cursor_type = "row"
        table.add_columns("Agent", "Status", "ID")
        self.refresh_data()
        self.set_interval(3.0, self.refresh_data)

    @work(exclusive=True)
    async def refresh_data(self) -> None:
        """Poll registry for session updates."""
        try:
            self.sessions = ps_impl(all=self.show_all)
            table = self.query_one("#session-list", DataTable)

            # Keep track of current selection
            current_row = table.cursor_row

            table.clear()
            for s in self.sessions:
                status = s.get("status", "?")
                status_style = "green" if status == "running" else "dim"
                if "failed" in status or "error" in status or "crashed" in status:
                    status_style = "red"

                table.add_row(
                    s.get("agent", "?"),
                    f"[{status_style}]{status}[/]",
                    s.get("id", "?")[:12],
                    key=s.get("id"),
                )

            if current_row is not None and current_row < len(self.sessions):
                table.move_cursor(row=current_row)
        except Exception as e:
            _log.error("Failed to refresh sessions: %s", e)

    @on(DataTable.RowSelected)
    def on_session_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_session_id = str(event.row_key.value)
        session = next((s for s in self.sessions if s.get("id") == self.selected_session_id), None)
        if session:
            self.query_one("#session-details", SessionDetails).update_details(session)
            self.load_session_logs()

    @work(exclusive=True)
    async def load_session_logs(self) -> None:
        """Load logs for the selected session."""
        if not self.selected_session_id:
            return

        log_view = self.query_one("#log-view", RichLog)
        log_view.clear()

        try:
            res = logs_impl(session_id=self.selected_session_id, tail=500)
            if res:
                log_view.write(res)
        except Exception as e:
            log_view.write(f"[red]Error loading logs: {e}[/red]")

    @on(Input.Submitted, "#message-input")
    async def on_message_submitted(self, event: Input.Submitted) -> None:
        if not self.selected_session_id:
            self.notify("No session selected", severity="warning")
            return

        message = event.value.strip()
        if not message:
            return

        ok, msg = session_send_impl(self.selected_session_id, message)
        if ok:
            self.notify(f"Sent: {msg}")
            self.query_one("#message-input", Input).value = ""
            # Refresh logs/chat after a short delay
            await asyncio.sleep(0.5)
            self.load_session_logs()
        else:
            self.notify(f"Failed: {msg}", severity="error")

    def action_refresh(self) -> None:
        self.refresh_data()
        if self.selected_session_id:
            self.load_session_logs()

    def action_toggle_all(self) -> None:
        self.show_all = not self.show_all
        self.notify(f"Show all owners: {self.show_all}")
        self.refresh_data()


if __name__ == "__main__":
    app = RegistryTUI()
    app.run()
