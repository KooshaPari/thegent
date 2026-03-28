"""Interactive input widget for compositor workflows (WL-017)."""

from __future__ import annotations

from collections.abc import Callable

from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input


class InteractiveInputWidget(Widget):
    """Prompt input bar with submit button and Enter-to-send behavior."""

    DEFAULT_CSS = """
    InteractiveInputWidget {
        height: 3;
        width: 1fr;
        border: solid $primary;
        padding: 0 1;
    }
    """

    def __init__(self, on_submit: Callable[[str], None] | None = None, placeholder: str = "Type a prompt...") -> None:
        super().__init__()
        self._on_submit = on_submit
        self._placeholder = placeholder

    def compose(self):
        with Horizontal():
            yield Input(placeholder=self._placeholder, id="interactive-input")
            yield Button("Send", id="interactive-send", variant="primary")

    def _submit_current(self) -> None:
        input_widget = self.query_one("#interactive-input", Input)
        text = input_widget.value.strip()
        if not text:
            return
        if self._on_submit is not None:
            self._on_submit(text)
        input_widget.value = ""

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit_current()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "interactive-send":
            self._submit_current()
