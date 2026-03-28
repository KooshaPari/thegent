"""Timeline widget for run/event visibility (WL-017)."""

from __future__ import annotations

from collections import deque
from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static


class TimelineWidget(Widget):
    """Append-only timeline feed with fixed-length history."""

    DEFAULT_CSS = """
    TimelineWidget {
        width: 1fr;
        height: 8;
        border: solid $accent;
        padding: 0 1;
    }
    """

    def __init__(self, max_entries: int = 100) -> None:
        super().__init__()
        self._entries: deque[str] = deque(maxlen=max(1, max_entries))

    def compose(self):
        yield Static("No events yet.", id="timeline-content")

    def add_event(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._entries.append(f"[{ts}] {message}")
        if self.is_attached:
            self._render()

    def _render(self) -> None:
        content = self.query_one("#timeline-content", Static)
        if not self._entries:
            content.update("No events yet.")
            return
        content.update("\n".join(self._entries))
