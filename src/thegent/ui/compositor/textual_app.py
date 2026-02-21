"""CompositorApp - Agent-oriented Textual application with sidebar and output pane.

Provides TUIContext, CompositorApp (with sidebar/maximize toggle, output writing,
agent status), and run_tui() for launching the TUI from code or the CLI.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import QueryError
from textual.theme import Theme
from textual.widgets import Footer, Header, Static


# Lazy imports to avoid circular dependency with thegent.tui package init.
# thegent.tui.__init__ re-exports symbols from this module; importing tui
# submodules at the top level would create a circular import chain.
def _get_base_layout():  # noqa: ANN202 -- lazy import helper, return type depends on import
    from thegent.tui.layouts.base import BaseLayout  # noqa: PLC0415 -- deferred to break circular import

    return BaseLayout


def _get_menubar_widget():  # noqa: ANN202 -- lazy import helper, return type depends on import
    from thegent.tui.widgets.menubar import MenubarWidget  # noqa: PLC0415 -- deferred to break circular import

    return MenubarWidget


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
    """Agent-oriented TUI application for thegent.

    Features:
    - Menubar with file/edit/view/tools/help menus
    - Output pane for agent output with write/append helpers
    - Sidebar with session/agent status info
    - Sidebar toggle and output maximize actions
    - Keybindings for navigation and layout control
    - TUI context (session_id, agent_name, cwd) threading through UI
    """

    CSS_THEMES = [  # noqa: RUF012 -- mutable class default required by framework
        Theme(
            name="thegent-dark",
            primary="#00ff00",
            secondary="#0088ff",
            accent="#ffff00",
            success="#00cc00",
            warning="#ffcc00",
            error="#ff3333",
            foreground="#e0e0e0",
            background="#1a1a1a",
            surface="#2a2a2a",
            panel="#333333",
        ),
    ]

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

    BINDINGS = [  # noqa: RUF012 -- mutable class default required by framework
        ("f1", "focus_next", "Focus Next Pane"),
        ("f2", "focus_prev", "Focus Previous Pane"),
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+h", "toggle_maximize", "Maximize/Minimize Output"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("f12", "show_help", "Show Help"),
    ]

    def __init__(self, context: TUIContext | None = None) -> None:
        super().__init__()
        self.context = context or TUIContext()
        self._sidebar_visible = True
        self._output_maximized = False
        BaseLayout = _get_base_layout()
        self._layout = BaseLayout()

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        MenubarWidget = _get_menubar_widget()
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
        self.update_title()
        self.update_status()
        self.set_focus(None)

    def update_title(self) -> None:
        """Update window title."""
        agent = self.context.agent_name or "thegent"
        session = self.context.session_id or "session"
        self.title = f"thegent: {agent} [{session}]"

    def update_status(self) -> None:
        """Update status display."""
        try:
            status = self.query_one("#status-content", Static)
            status.update(
                f"Session: {self.context.session_id or 'N/A'}\n"
                f"Agent: {self.context.agent_name or 'N/A'}\n"
                f"CWD: {self.context.cwd}\n"
                f"\nStatus: Ready"
            )
        except QueryError:
            pass

    def action_focus_next(self) -> None:
        """Focus the next pane."""
        panes = ["output-pane", "sidebar"]
        try:
            current = self.focused
            if current:
                current_id = current.id or ""
                if current_id in panes:
                    idx = panes.index(current_id)
                    next_idx = (idx + 1) % len(panes)
                    next_pane = self.query_one(f"#{panes[next_idx]}")
                    next_pane.focus()
        except QueryError:
            pass

    def action_focus_prev(self) -> None:
        """Focus the previous pane."""
        panes = ["output-pane", "sidebar"]
        try:
            current = self.focused
            if current:
                current_id = current.id or ""
                if current_id in panes:
                    idx = panes.index(current_id)
                    prev_idx = (idx - 1) % len(panes)
                    next_pane = self.query_one(f"#{panes[prev_idx]}")
                    next_pane.focus()
        except QueryError:
            pass

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
            sidebar = self.query_one("#sidebar")

            if self._output_maximized:
                sidebar.styles.display = "none"
                output.styles.width = "100%"
            else:
                sidebar.styles.display = "block"
                output.styles.width = "70%"
        except QueryError:
            pass

    def action_quit(self) -> bool:
        """Quit the application."""
        self.exit(0)
        return True

    def action_show_help(self) -> None:
        """Show help dialog."""
        self.notify(
            "F1/F2: Navigate panes | Ctrl+B: Toggle sidebar | Ctrl+H: Toggle maximize | Ctrl+Q: Quit",
            severity="information",
            timeout=10,
        )

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
            current = str(output.renderable) if hasattr(output, "renderable") else str(output)
            output.update(current + text)
        except QueryError:
            pass

    def set_agent_status(self, agent_status: str, agent: str = "agent") -> None:
        """Update agent status display."""
        self.context.agent_name = agent
        self.update_title()
        try:
            status_widget = self.query_one("#status-content", Static)
            status_widget.update(
                f"Session: {self.context.session_id or 'N/A'}\n"
                f"Agent: {agent}\n"
                f"CWD: {self.context.cwd}\n"
                f"\nStatus: {agent_status}"
            )
        except QueryError:
            pass


async def run_tui(
    session_id: str | None = None,
    agent_name: str | None = None,
    cwd: Path | None = None,
    context: TUIContext | None = None,
    *,
    headless: bool = False,
) -> int:
    """Run the TUI compositor.

    Args:
        session_id: Session identifier (ignored if context is provided)
        agent_name: Current agent name (ignored if context is provided)
        cwd: Current working directory (ignored if context is provided)
        context: Optional pre-built TUIContext; takes precedence over other args.
        headless: Run in headless mode (for testing)

    Returns:
        Exit code
    """
    if context is None:
        context = TUIContext(session_id=session_id, agent_name=agent_name, cwd=cwd)
    app = CompositorApp(context=context)

    if headless:
        async with app.run_test() as pilot:
            await pilot.pause()
            return 0

    return await app.run_async()


if __name__ == "__main__":
    import sys

    asyncio.run(run_tui(headless=False))
    sys.exit(0)
