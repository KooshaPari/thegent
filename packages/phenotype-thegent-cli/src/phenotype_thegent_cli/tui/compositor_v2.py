"""TUI Compositor - Main application with PaneManager integration.

A unified terminal user interface for thegent using Textual with support for:
- Multi-pane layouts with split/merge operations
- Session persistence
- Layout management
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import QueryError
from textual.theme import Theme
from textual.widgets import Footer, Header, Static

from .layouts.base import BaseLayout
from .pane_manager import PaneManager
from .session_state import SessionState
from .widgets.menubar import MenubarWidget

_log = logging.getLogger(__name__)


class TUIContext:
    """Context passed to all widgets/components."""

    def __init__(
        self,
        session_id: str | None = None,
        agent_name: str | None = None,
        cwd: Path | None = None,
    ) -> None:
        self.session_id = session_id
        self.agent_name = agent_name
        self.cwd = cwd or Path.cwd()
        self.state: dict[str, Any] = {}


class CompositorApp(App):
    """Main TUI application for thegent.

    Integrates:
    - PaneManager for multi-pane layout
    - SessionState for persistence
    - Textual widgets for UI
    """

    # Theme configuration
    CSS_THEMES: ClassVar[list[Any]] = [
        Theme(
            name="thegent-dark",
            primary="#00ff00",  # Terminal green
            secondary="#0088ff",  # Blue
            accent="#ffff00",  # Yellow
            success="#00cc00",
            warning="#ffcc00",
            error="#ff3333",
            foreground="#e0e0e0",
            background="#1a1a1a",
            surface="#2a2a2a",
            panel="#333333",
        ),
    ]

    # Default CSS
    CSS = """
    Screen {
        layout: vertical;
    }

    #header {
        height: 2;
        background: $accent;
        color: $text;
    }

    #menubar {
        height: 1;
        background: $surface;
        color: $text;
        dock: top;
    }

    #main {
        layout: horizontal;
    }

    #output-pane {
        width: 70%;
        border: solid $secondary;
        padding: 1;
    }

    #sidebar {
        width: 30%;
        border: solid $accent;
        padding: 1;
    }

    #footer {
        height: 1;
        background: $surface;
        color: $text-muted;
        dock: bottom;
    }

    .pane-header {
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
    }

    .agent-output {
        color: $text;
        background: $background;
    }

    .status-item {
        color: $text-muted;
    }

    .status-item.active {
        color: $success;
    }

    .status-item.error {
        color: $error;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        # Pane management
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+v", "split_vertical", "Split Vert"),
        ("ctrl+h", "split_horizontal", "Split Horiz"),
        ("ctrl+x", "close_pane", "Close Pane"),
        # Navigation
        ("f1", "focus_next", "Focus Next"),
        ("f2", "focus_prev", "Focus Prev"),
        # Layout
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+m", "toggle_maximize", "Maximize"),
        # Session
        ("ctrl+s", "save_layout", "Save Layout"),
        ("ctrl+r", "restore_layout", "Restore Layout"),
        # Application
        ("ctrl+q", "quit", "Quit"),
        # Help
        ("f12", "show_help", "Show Help"),
    ]

    def __init__(self, context: TUIContext | None = None) -> None:
        super().__init__()
        self.context = context or TUIContext()
        self._sidebar_visible = True
        self._output_maximized = False
        self._layout = BaseLayout()
        self.pane_manager = PaneManager()
        self.session_state = SessionState()

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header(show_clock=False)
        yield MenubarWidget(id="menubar")

        with Horizontal(id="main"):
            with Container(id="output-pane"):
                yield Static("Agent Output", classes="pane-header")
                yield Static("Waiting for agent...\n", id="output-content", classes="agent-output")

            if self._sidebar_visible:
                with Container(id="sidebar"):
                    yield Static("Status", classes="pane-header")
                    yield Static(id="status-content", classes="status-content")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app after mounting."""
        _log.info("TUI Compositor started")

        # Initialize with default pane
        self.pane_manager.create_pane()

        self.update_title()
        self.update_status()
        self.set_focus(None)  # Focus first available

    def update_title(self) -> None:
        """Update window title."""
        agent = self.context.agent_name or "thegent"
        session = self.context.session_id or "session"
        pane_count = len(self.pane_manager.collect_panes())
        self.title = f"thegent: {agent} [{session}] - {pane_count} pane(s)"

    def update_status(self) -> None:
        """Update status display."""
        try:
            status = self.query_one("#status-content", Static)
            panes = len(self.pane_manager.collect_panes())
            status.update(
                f"Session: {self.context.session_id or 'N/A'}\n"
                f"Agent: {self.context.agent_name or 'N/A'}\n"
                f"CWD: {self.context.cwd}\n"
                f"Panes: {panes}\n"
                f"\nStatus: Ready"
            )
        except QueryError:
            pass

    def action_new_pane(self) -> None:
        """Create a new terminal pane."""
        _pane = self.pane_manager.create_pane()
        self.update_title()
        self.update_status()
        _log.info("New pane created")

    def action_split_vertical(self) -> None:
        """Split current pane vertically."""
        _pane = self.pane_manager.split_pane("vertical")
        self.update_title()
        self.update_status()
        _log.info("Vertical split created")

    def action_split_horizontal(self) -> None:
        """Split current pane horizontally."""
        _pane = self.pane_manager.split_pane("horizontal")
        self.update_title()
        self.update_status()
        _log.info("Horizontal split created")

    def action_close_pane(self) -> None:
        """Close current pane."""
        self.pane_manager.close_pane()
        self.update_title()
        self.update_status()
        _log.info("Pane closed")

    def action_focus_next(self) -> None:
        """Focus the next pane."""
        self.pane_manager.focus_next()
        self.update_status()
        _log.debug("Focus moved to next pane")

    def action_focus_prev(self) -> None:
        """Focus the previous pane."""
        self.pane_manager.focus_prev()
        self.update_status()
        _log.debug("Focus moved to previous pane")

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self._sidebar_visible = not self._sidebar_visible
        if self._sidebar_visible:
            self.mount(
                Container(
                    Static("Status", classes="pane-header"),
                    Static(id="status-content", classes="status-content"),
                    id="sidebar",
                )
            )
            self.update_status()
        else:
            try:
                sidebar = self.query_one("#sidebar")
                sidebar.remove()
            except QueryError:
                pass

    def action_toggle_maximize(self) -> None:
        """Toggle output pane maximization."""
        self._output_maximized = not self._output_maximized
        try:
            output = self.query_one("#output-pane")
            try:
                sidebar = self.query_one("#sidebar")
                if self._output_maximized:
                    sidebar.styles.display = "none"
                    output.styles.width = "100%"
                else:
                    sidebar.styles.display = "block"
                    output.styles.width = "70%"
            except QueryError:
                pass
        except QueryError:
            pass

    def action_save_layout(self) -> None:
        """Save current layout."""
        layout = self.pane_manager.save_layout()
        if self.context.session_id:
            self.session_state.save_layout(f"{self.context.session_id}_layout", layout)
            self.notify("Layout saved", severity="information", timeout=3)
            _log.info("Layout saved")

    def action_restore_layout(self) -> None:
        """Restore a saved layout."""
        if self.context.session_id:
            layout = self.session_state.load_layout(f"{self.context.session_id}_layout")
            if layout:
                self.pane_manager.restore_layout(layout)
                self.update_title()
                self.update_status()
                self.notify("Layout restored", severity="information", timeout=3)
                _log.info("Layout restored")

    def action_quit(self) -> bool:
        """Quit the application."""
        # Save session on exit
        if self.context.session_id:
            layout = self.pane_manager.save_layout()
            self.session_state.save_session(self.context.session_id, layout)
            _log.info(f"Session {self.context.session_id} saved")

        self.exit(0)
        return True

    def action_show_help(self) -> None:
        """Show help dialog."""
        help_text = (
            "Ctrl+N: New Pane | Ctrl+V/H: Split V/H | Ctrl+X: Close\n"
            "F1/F2: Next/Prev | Ctrl+B: Toggle Sidebar | Ctrl+M: Maximize\n"
            "Ctrl+S/R: Save/Restore Layout | Ctrl+Q: Quit"
        )
        self.notify(help_text, severity="information", timeout=10)

    def write_output(self, text: str) -> None:
        """Write text to output pane."""
        try:
            output = self.query_one("#output-content", Static)
            output.update(text)
        except QueryError:
            pass

    def append_output(self, text: str) -> None:
        """Append text to output pane."""
        try:
            output = self.query_one("#output-content", Static)
            current = str(output._renderable)  # type: ignore[attr-defined] -- Static._renderable is internal but stable
            output.update(current + text)
        except QueryError:
            pass

    def set_agent_status(self, status: str, agent: str = "agent") -> None:
        """Update agent status display."""
        self.context.agent_name = agent
        self.update_title()
        try:
            status_widget = self.query_one("#status-content", Static)
            panes = len(self.pane_manager.collect_panes())
            status_widget.update(
                f"Session: {self.context.session_id or 'N/A'}\n"
                f"Agent: {agent}\n"
                f"CWD: {self.context.cwd}\n"
                f"Panes: {panes}\n"
                f"\nStatus: {status}"
            )
        except QueryError:
            pass


async def run_tui(
    session_id: str | None = None,
    agent_name: str | None = None,
    cwd: Path | None = None,
    *,
    headless: bool = False,
) -> int:
    """Run the TUI compositor.

    Args:
        session_id: Session identifier
        agent_name: Current agent name
        cwd: Current working directory
        headless: Run in headless mode (for testing)

    Returns:
        Exit code
    """
    context = TUIContext(session_id=session_id, agent_name=agent_name, cwd=cwd)
    app = CompositorApp(context=context)

    if headless:
        # Headless mode for testing
        async with app.run_test() as pilot:
            await pilot.pause()
            return 0

    return int(await app.run_async() or 0)


if __name__ == "__main__":
    import sys

    asyncio.run(run_tui(headless=False))
    sys.exit(0)
