"""Main Textual application for the TUI compositor.

Provides the CompositApp class which manages the overall UI layout including
header, footer, and pane management.
"""

from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Static

from thegent.compositor.pane_manager import PaneManager
from thegent.compositor.session_state import SessionState


class StatusBar(Static):
    """Custom status bar widget."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $boost;
        color: $text;
        border-top: solid $primary;
    }
    """

    def __init__(self, pane_manager: PaneManager) -> None:
        """Initialize the status bar.

        Args:
            pane_manager: Reference to the pane manager
        """
        super().__init__()
        self.pane_manager = pane_manager

    def render(self) -> str:
        """Render the status bar with current information."""
        pane_count = self.pane_manager.get_pane_count()
        focused_pane_id = self.pane_manager.focus_pane_id
        return (
            f"Panes: {pane_count} | Focused: {focused_pane_id[:8]} | Ctrl+H: Split H | Ctrl+V: Split V | Ctrl+X: Close"
        )


class PaneContainer(Container):
    """Container for terminal panes."""

    DEFAULT_CSS = """
    PaneContainer {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
        background: $panel;
    }
    """

    def __init__(self, pane_manager: PaneManager) -> None:
        """Initialize the pane container.

        Args:
            pane_manager: Reference to the pane manager
        """
        super().__init__()
        self.pane_manager = pane_manager

    def compose(self) -> ComposeResult:
        """Compose the pane container with the root pane."""
        root_pane_node = self.pane_manager.root
        if root_pane_node.pane:
            yield root_pane_node.pane


class CompositApp(Vertical):
    """Main TUI Compositor application.

    This is a Textual application that provides a multi-pane terminal interface
    with support for splitting, merging, and layout management.
    """

    TITLE = "Thegent Compositor"
    SUB_TITLE = "Multi-pane terminal interface"

    BINDINGS: ClassVar[list] = [
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+h", "split_horizontal", "Split H"),
        ("ctrl+v", "split_vertical", "Split V"),
        ("ctrl+x", "close_pane", "Close Pane"),
        ("ctrl+l", "focus_next", "Focus Next"),
        ("ctrl+s", "save_layout", "Save Layout"),
        ("ctrl+r", "restore_layout", "Restore Layout"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        """Initialize the CompositApp."""
        super().__init__()
        self.pane_manager = PaneManager()
        self.session_state = SessionState()
        self.pane_container: PaneContainer | None = None
        self.status_bar: StatusBar | None = None

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        self.pane_container = PaneContainer(self.pane_manager)
        yield self.pane_container
        self.status_bar = StatusBar(self.pane_manager)
        yield self.status_bar
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Try to load previous session
        layout = self.session_state.load_session()
        if layout:
            self.pane_manager.restore_layout(layout)

        # Spawn the initial shell
        root_pane = self.pane_manager.root.pane
        if root_pane:
            root_pane.spawn_shell()

    def on_unmount(self) -> None:
        """Called when the app is unmounted. Clean up resources."""
        self.save_session_state()
        for pane in self.pane_manager.get_all_panes():
            pane.cleanup()

    def action_new_pane(self) -> None:
        """Action: Create a new pane."""
        self.action_split_horizontal()

    def action_split_horizontal(self) -> None:
        """Action: Split the current pane horizontally."""
        new_pane_node = self.pane_manager.split_pane("H")
        if new_pane_node and new_pane_node.pane:
            new_pane_node.pane.spawn_shell()
            self.update_pane_display()

    def action_split_vertical(self) -> None:
        """Action: Split the current pane vertically."""
        new_pane_node = self.pane_manager.split_pane("V")
        if new_pane_node and new_pane_node.pane:
            new_pane_node.pane.spawn_shell()
            self.update_pane_display()

    def action_close_pane(self) -> None:
        """Action: Close the current pane."""
        if self.pane_manager.close_pane():
            self.update_pane_display()

    def action_focus_next(self) -> None:
        """Action: Focus on the next pane."""
        self.pane_manager.focus_next()
        self.update_status()

    def action_save_layout(self) -> None:
        """Action: Save the current layout."""
        layout = self.pane_manager.save_layout()
        if self.session_state.save_session(layout):
            self.notify("Layout saved successfully")
        else:
            self.notify("Failed to save layout")

    def action_restore_layout(self) -> None:
        """Action: Restore a saved layout."""
        sessions = self.session_state.list_sessions()
        if not sessions:
            self.notify("No saved sessions available")
            return

        # For Phase 1, just restore the default session
        layout = self.session_state.load_session()
        if layout and self.pane_manager.restore_layout(layout):
            self.update_pane_display()
            self.notify("Layout restored")
        else:
            self.notify("Failed to restore layout")

    def update_pane_display(self) -> None:
        """Update the pane display after tree changes."""
        # Rebuild the pane container with updated tree
        if self.pane_container:
            self.pane_container.remove_children()
            root_pane_node = self.pane_manager.root
            if root_pane_node.pane:
                self.pane_container.mount(root_pane_node.pane)
        self.update_status()

    def update_status(self) -> None:
        """Update the status bar."""
        if self.status_bar:
            self.status_bar.update(self.status_bar.render())

    def save_session_state(self) -> None:
        """Save the current session state to disk."""
        layout = self.pane_manager.save_layout()
        self.session_state.save_session(layout)


def run() -> None:
    """Run the CompositApp."""
    app = CompositApp()
    app.run()


if __name__ == "__main__":
    run()
