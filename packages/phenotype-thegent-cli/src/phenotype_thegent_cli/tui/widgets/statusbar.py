"""Statusbar widget for TUI compositor."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class StatusItem:
    """Represents a status indicator."""

    def __init__(
        self,
        label: str,
        value: str = "",
        active: bool = True,
        color: str = "status-item",
    ) -> None:
        self.label = label
        self.value = value
        self.active = active
        self.color = color

    def __str__(self) -> str:
        return f"{self.label}: {self.value}"


def compute_context_usage_display(
    used: int | None,
    max_val: int | None,
) -> tuple[str, str | None]:
    """Compute display text and class for context usage."""
    if used is None or max_val is None or max_val == 0:
        return "N/A", None

    ratio = used / max_val
    used_display = f"{used // 1000}k" if used >= 1000 else str(used)
    max_display = f"{max_val // 1000}k" if max_val >= 1000 else str(max_val)
    display = f"{used_display}/{max_display}"

    if ratio < 0.6:
        return display, "ctx-green"
    if ratio < 0.8:
        return display, "ctx-yellow"
    return display, "ctx-red"


class StatusbarWidget(Widget):
    """Status bar showing session and agent status."""

    # Reactive state
    session_id: reactive[str | None] = reactive[str | None](None)
    agent_name: reactive[str | None] = reactive[str | None](None)
    agent_status: reactive[str] = reactive[str]("idle")
    cwd: reactive[str] = reactive[str]("")
    # WL-108: Context usage tracking
    context_tokens_used: reactive[int | None] = reactive[int | None](None)
    context_window_max: reactive[int | None] = reactive[int | None](None)

    DEFAULT_CSS = """
    StatusbarWidget {
        height: 1;
        background: $surface;
        color: $text-muted;
        dock: bottom;
    }

    StatusbarWidget .status-section {
        padding: 0 1;
        color: $text-muted;
    }

    StatusbarWidget .status-value {
        color: $text;
        font-weight: bold;
    }

    StatusbarWidget .status-active {
        color: $success;
    }

    StatusbarWidget .status-error {
        color: $error;
    }

    StatusbarWidget .status-warning {
        color: $warning;
    }

    StatusbarWidget .separator {
        color: $panel;
    }

    StatusbarWidget #clock {
        color: $text-muted;
        padding: 0 1;
    }

    StatusbarWidget .ctx-green {
        color: $success;
    }

    StatusbarWidget .ctx-yellow {
        color: $warning;
    }

    StatusbarWidget .ctx-red {
        color: $error;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._items: list[StatusItem] = []
        self._clock_format = "%H:%M:%S"

    def compose(self) -> ComposeResult:
        """Create statusbar layout."""
        yield Static(id="clock")
        yield Static("│", classes="separator")
        yield Static("Session:", classes="status-section")
        yield Static(id="session-value", classes="status-value status-section")
        yield Static("│", classes="separator")
        yield Static("Agent:", classes="status-section")
        yield Static(id="agent-value", classes="status-value status-section")
        yield Static("│", classes="separator")
        yield Static("Status:", classes="status-section")
        yield Static(id="status-value", classes="status-value status-section status-active")
        yield Static("│", classes="separator")
        # WL-108: Context usage display
        yield Static("CTX:", classes="status-section")
        yield Static(id="ctx-value", classes="status-value status-section")
        yield Static("│", classes="separator")
        yield Static("CWD:", classes="status-section")
        yield Static(id="cwd-value", classes="status-value status-section")

    def on_mount(self) -> None:
        """Initialize statusbar after mounting."""
        self._update_clock()
        self.set_interval(1.0, self._update_clock)

    def _update_clock(self) -> None:
        """Update clock display."""
        try:
            clock = self.query_one("#clock", Static)
            clock.update(datetime.now().strftime(self._clock_format))
        except Exception:
            pass

    def watch_session_id(self, value: str | None) -> None:
        """Update session ID display."""
        try:
            session = self.query_one("#session-value", Static)
            session.update(value or "N/A")
        except Exception:
            pass

    def watch_agent_name(self, value: str | None) -> None:
        """Update agent name display."""
        try:
            agent = self.query_one("#agent-value", Static)
            agent.update(value or "N/A")
        except Exception:
            pass

    def watch_agent_status(self, value: str) -> None:
        """Update agent status display."""
        try:
            status = self.query_one("#status-value", Static)
            status.update(value)

            # Update color based on status
            status.remove_class("status-active", "status-error", "status-warning")
            if value == "running":
                status.add_class("status-active")
            elif value == "error":
                status.add_class("status-error")
            elif value == "warning":
                status.add_class("status-warning")
        except Exception:
            pass

    def watch_cwd(self, value: str) -> None:
        """Update CWD display."""
        try:
            cwd = self.query_one("#cwd-value", Static)
            # Truncate if too long
            display = value if len(value) <= 40 else f"...{value[-37:]}"
            cwd.update(display)
        except Exception:
            pass

    def watch_context_tokens_used(self, value: int | None) -> None:
        """Update context tokens display."""
        self._update_context_display()

    def watch_context_window_max(self, value: int | None) -> None:
        """Update context window max display."""
        self._update_context_display()

    def _update_context_display(self) -> None:
        """Update the context usage display with color coding."""
        try:
            ctx = self.query_one("#ctx-value", Static)
            display, css_class = compute_context_usage_display(
                self.context_tokens_used,
                self.context_window_max,
            )
            ctx.update(display)

            ctx.remove_class("ctx-green", "ctx-yellow", "ctx-red")
            if css_class is not None:
                ctx.add_class(css_class)
        except Exception:
            pass

    def set_status(self, status: str, message: str = "") -> None:
        """Set overall status with optional message."""
        self.agent_status = status
        if message:
            self.notify(message, severity="information" if status == "running" else "warning")

    def add_item(self, item: StatusItem) -> None:
        """Add a custom status item."""
        self._items.append(item)

    def remove_item(self, label: str) -> None:
        """Remove a custom status item."""
        self._items = [i for i in self._items if i.label != label]

    def clear_items(self) -> None:
        """Clear all custom status items."""
        self._items.clear()
