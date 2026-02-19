"""Menubar widget for TUI compositor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Click


class MenubarWidget(Widget):
    """Simple menubar widget with keyboard shortcuts display."""

    # Reactive state
    active_menu: reactive[str | None] = reactive[str | None](None)

    DEFAULT_CSS = """
    MenubarWidget {
        height: 1;
        background: $surface;
        color: $text;
        dock: top;
    }

    MenubarWidget .menu-item {
        padding: 0 1;
        color: $text;
    }

    MenubarWidget .menu-item:hover {
        background: $accent;
        color: $text;
    }

    MenubarWidget .menu-item.active {
        background: $accent;
        color: $text;
    }

    MenubarWidget .shortcut {
        color: $text-muted;
        padding: 0 1;
    }
    """

    MENUS = [
        (
            "File",
            [
                ("New Session", "Ctrl+N"),
                ("Open Config", "Ctrl+O"),
                ("Save Layout", "Ctrl+S"),
                ("-", None),
                ("Exit", "Ctrl+Q"),
            ],
        ),
        (
            "Edit",
            [
                ("Copy", "Ctrl+C"),
                ("Paste", "Ctrl+V"),
                ("Select All", "Ctrl+A"),
            ],
        ),
        (
            "View",
            [
                ("Toggle Sidebar", "Ctrl+B"),
                ("Toggle Maximize", "Ctrl+H"),
                ("Next Pane", "F1"),
                ("Prev Pane", "F2"),
            ],
        ),
        (
            "Tools",
            [
                ("Run Agent", "F5"),
                ("Stop Agent", "F6"),
                ("Clear Output", "F7"),
            ],
        ),
        (
            "Help",
            [
                ("Shortcuts", "F12"),
                ("About", None),
            ],
        ),
    ]

    def compose(self) -> ComposeResult:
        """Create menubar layout."""
        with Horizontal():
            for label, _ in self.MENUS:
                yield Static(f" {label} ", classes="menu-item")

            # Spacer
            yield Static("", classes="spacer", expand=True)

            # Keyboard shortcuts hint
            yield Static(" [F12: Help] ", classes="shortcut")

    def on_mount(self) -> None:
        """Initialize menubar after mounting."""
        # Simplified initialization

    def on_click(self, event: Click) -> None:
        """Handle click on menu items."""
        if not hasattr(event, 'target') or not event.target:
            return
        
        # Find which menu item was clicked
        target = event.target
        if hasattr(target, 'renderable'):
            text = str(target.renderable)
            for menu_name, items in self.MENUS:
                if menu_name in text:
                    self.action_toggle_menu(menu_name)
                    break

    def action_toggle_menu(self, menu_name: str) -> None:
        """Toggle a menu dropdown."""
        if self.active_menu == menu_name:
            self.active_menu = None
        else:
            self.active_menu = menu_name


class MenuDropdown(Static):
    """Dropdown menu widget."""

    def __init__(self, items: list[tuple[str, str | None]], **kwargs) -> None:
        super().__init__(**kwargs)
        self.items = items

    def compose(self) -> ComposeResult:
        """Create dropdown items."""
        for label, shortcut in self.items:
            if label == "-":
                yield Static("-", classes="menu-separator")
            else:
                text = f" {label} "
                if shortcut:
                    text += f"  [{shortcut}]"
                yield Static(text, classes="menu-dropdown-item")
