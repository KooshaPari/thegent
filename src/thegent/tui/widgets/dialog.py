"""Dialog and floating window widgets for TUI compositor.

Provides modal dialogs, floating panels, and overlay widgets.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from textual.containers import Container
from textual.css.query import QueryError
from textual.keys import Keys
from textual.widgets import Button, Input, Label, Static

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult
    from textual.events import Click, Key
    from textual.widget import Widget


class DialogResult(Enum):
    """Result of a dialog interaction."""

    CONFIRM = "confirm"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"
    OK = "ok"
    CLOSE = "close"


class DialogStyle(Enum):
    """Dialog style variants."""

    DEFAULT = "default"
    DANGER = "danger"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"


class Dialog(Container):
    """Modal dialog widget with title, content, and buttons."""

    DEFAULT_CSS = """
    Dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: solid $accent;
        padding: 1;
        layout: vertical;
    }

    Dialog .dialog-header {
        height: 1;
        background: $accent;
        color: $text;
        text-align: center;
        weight: bold;
    }

    Dialog .dialog-content {
        height: auto;
        padding: 1;
        layout: vertical;
    }

    Dialog .dialog-buttons {
        height: 3;
        layout: horizontal;
        align: center middle;
        spacing: 1;
    }

    Dialog .button {
        width: 15;
        height: 3;
        background: $panel;
        color: $text;
        border: solid $secondary;
    }

    Dialog .button:hover {
        background: $secondary;
        color: $text;
    }

    Dialog .button.focus {
        border: solid $accent;
    }

    Dialog. danger {
        border: solid $error;
    }

    Dialog.danger .dialog-header {
        background: $error;
    }

    Dialog.success {
        border: solid $success;
    }

    Dialog.success .dialog-header {
        background: $success;
    }

    Dialog.warning {
        border: solid $warning;
    }

    Dialog.warning .dialog-header {
        background: $warning;
    }
    """

    def __init__(
        self,
        title: str,
        *,
        style: DialogStyle = DialogStyle.DEFAULT,
        buttons: list[tuple[str, DialogResult]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.style = style
        self.buttons = buttons or [("OK", DialogResult.OK), ("Cancel", DialogResult.CANCEL)]
        self._result: DialogResult | None = None
        self._on_result: Callable[[DialogResult], None] | None = None

    def compose(self) -> ComposeResult:
        yield Label(self.title, classes="dialog-header")
        with Container(classes="dialog-content"):
            yield from self._render_content()
        with Container(classes="dialog-buttons"):
            for label, result in self.buttons:
                yield Button(label, id=f"btn-{result.value}", classes="button")

    def _render_content(self) -> list[Widget]:
        """Override in subclasses to add content."""
        return []

    def on_mount(self) -> None:
        """Set initial focus."""
        try:
            first_button = self.query_one("#btn-ok", Button)
            first_button.focus()
        except QueryError:
            pass

    def on_click(self, event: Click) -> None:
        """Handle button clicks."""
        if event.widget and event.widget.id and event.widget.id.startswith("btn-"):
            result_value = event.widget.id[4:]  # Remove "btn-" prefix
            for _label, result in self.buttons:
                if result.value == result_value:
                    self._result = result
                    self._dismiss()
                    break

    def on_key(self, event: Key) -> None:
        """Handle keyboard navigation."""
        if event.key == Keys.Escape:
            self._result = DialogResult.CANCEL
            self._dismiss()
        elif event.key == Keys.Enter:
            # Confirm with Enter if there's a focused button
            try:
                focused = self.query_one(":focus", Button)
                if hasattr(focused, "id") and focused.id and focused.id.startswith("btn-"):
                    result_value = focused.id[4:]
                    for _label, result in self.buttons:
                        if result.value == result_value:
                            self._result = result
                            self._dismiss()
                            break
            except QueryError:
                pass

    def _dismiss(self) -> None:
        """Close the dialog."""
        if self._on_result:
            self._on_result(self._result)
        self.remove()

    def on_result(self, callback: Callable[[DialogResult], None]) -> None:
        """Set callback for dialog result."""
        self._on_result = callback


class MessageDialog(Dialog):
    """Simple message dialog with text content."""

    def __init__(
        self,
        message: str,
        title: str = "Message",
        **kwargs,
    ) -> None:
        super().__init__(title=title, **kwargs)
        self._message = message

    def _render_content(self) -> list[Widget]:
        return [Static(self._message)]


class InputDialog(Dialog):
    """Dialog with text input field."""

    def __init__(
        self,
        prompt: str,
        title: str = "Input",
        default: str = "",
        password: bool = False,
        placeholder: str = "",
        **kwargs,
    ) -> None:
        super().__init__(title=title, **kwargs)
        self._prompt = prompt
        self._input = Input(
            default,
            password=password,
            placeholder=placeholder,
        )

    def _render_content(self) -> list[Widget]:
        return [
            Label(self._prompt),
            self._input,
        ]

    def get_value(self) -> str:
        """Get the input value."""
        return self._input.value


class ConfirmDialog(Dialog):
    """Confirmation dialog with Yes/No buttons."""

    def __init__(
        self,
        message: str,
        title: str = "Confirm",
        yes_label: str = "Yes",
        no_label: str = "No",
        **kwargs,
    ) -> None:
        super().__init__(
            title=title,
            buttons=[
                (yes_label, DialogResult.YES),
                (no_label, DialogResult.NO),
            ],
            **kwargs,
        )
        self._message = message

    def _render_content(self) -> list[Widget]:
        return [Static(self._message)]


class Toast(Container):
    """Temporary notification toast."""

    DEFAULT_CSS = """
    Toast {
        width: 40;
        height: 3;
        background: $surface;
        border: solid $secondary;
        padding: 1;
        layout: vertical;
        offset: 0 10;
    }

    Toast.success {
        border: solid $success;
    }

    Toast.error {
        border: solid $error;
    }

    Toast.warning {
        border: solid $warning;
    }
    """

    def __init__(
        self,
        message: str,
        duration: float = 3.0,
        style: DialogStyle = DialogStyle.DEFAULT,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.message = message
        self.duration = duration
        self.style = style
        self._timer: float | None = None

    def compose(self) -> ComposeResult:
        yield Static(self.message)

    def on_mount(self) -> None:
        """Auto-dismiss after duration."""
        self.set_timer(self.duration, self.dismiss)

    def dismiss(self) -> None:
        """Remove the toast."""
        self.remove()


class Overlay(Container):
    """Full-screen overlay for dialogs and modals."""

    DEFAULT_CSS = """
    Overlay {
        width: 100%;
        height: 100%;
        background: $background with 50%;
        z-index: 100;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class DialogManager:
    """Manages dialogs and overlays."""

    def __init__(self) -> None:
        self._dialogs: list[Dialog] = []
        self._overlays: list[Overlay] = []

    def show_dialog(self, dialog: Dialog) -> None:
        """Show a dialog with overlay."""
        self._dialogs.append(dialog)

    def show_message(
        self,
        message: str,
        title: str = "Message",
        style: DialogStyle = DialogStyle.DEFAULT,
    ) -> None:
        """Show a simple message dialog."""
        dialog = MessageDialog(message, title=title, style=style)
        self.show_dialog(dialog)

    def show_confirm(
        self,
        message: str,
        title: str = "Confirm",
        on_result: Callable[[DialogResult], None] | None = None,
    ) -> None:
        """Show a confirmation dialog."""
        dialog = ConfirmDialog(message, title=title)
        if on_result:
            dialog.on_result(on_result)
        self.show_dialog(dialog)

    def show_input(
        self,
        prompt: str,
        title: str = "Input",
        default: str = "",
        password: bool = False,
        on_result: Callable[[str, DialogResult], None] | None = None,
    ) -> None:
        """Show an input dialog."""
        dialog = InputDialog(prompt, title=title, default=default, password=password)
        dialog.on_result(lambda r: on_result(dialog.get_value(), r) if on_result else None)
        self.show_dialog(dialog)

    def show_toast(
        self,
        message: str,
        duration: float = 3.0,
        style: DialogStyle = DialogStyle.DEFAULT,
    ) -> None:
        """Show a toast notification."""
        toast = Toast(message, duration=duration, style=style)
        # Would be added to screen

    def close_all(self) -> None:
        """Close all dialogs."""
        for dialog in self._dialogs:
            dialog.remove()
        self._dialogs.clear()
