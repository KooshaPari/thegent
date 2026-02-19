"""CompositApp - Main Textual application for the TUI compositor."""

import logging
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from thegent.ui.compositor.pane_manager import PaneManager

if TYPE_CHECKING:
    from thegent.ui.compositor.session_state import SessionState

logger = logging.getLogger(__name__)


class Statusbar(Static):
    """Custom status bar showing session and pane information."""

    DEFAULT_CSS = """
    Statusbar {
        width: 1fr;
        height: 1;
        background: $accent;
        color: $text;
        border: solid $primary 0 0 1 0;
    }
    """

    def render(self) -> str:
        """Render status bar content."""
        return "Session: default | Panes: 1 | Ready"


class CompositApp(App):
    """Main TUI Compositor application.

    Features:
    - Menubar with file/edit/view/tools/help menus
    - Statusbar with session info and pane count
    - Container for terminal panes
    - Key bindings for pane management

    Attributes:
        session_state: Optional persistent session state
        _pane_count: Current number of active panes
    """

    TITLE = "Thegent Compositor"
    SUBTITLE = "Terminal User Interface Compositor"

    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
        height: 1;
    }

    #main-pane-container {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
        background: $surface;
        padding: 0 1;
    }

    Statusbar {
        background: $accent;
        color: $text;
    }

    Footer {
        background: $primary;
        color: $text;
        height: 1;
    }

    #placeholder-pane {
        width: 1fr;
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+v", "split_vertical", "Split V"),
        ("ctrl+h", "split_horizontal", "Split H"),
        ("ctrl+x", "close_pane", "Close"),
        ("ctrl+l", "focus_next", "Focus Next"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, session_state: "SessionState | None" = None) -> None:
        """Initialize CompositApp.

        Args:
            session_state: Optional session state for persistence
        """
        super().__init__()
        self.session_state = session_state
        self._pane_count = 0
        self.pane_manager = PaneManager()
        logger.info("CompositApp initialized")

    def compose(self) -> ComposeResult:
        """Compose the app layout.

        Yields:
            Header widget
            Main pane container
            Statusbar widget
            Footer widget
        """
        logger.debug("Composing app layout")
        yield Header(show_clock=True)

        with Vertical(id="main-pane-container"):
            yield Static("Terminal Pane (empty)\nReady for input", id="placeholder-pane")

        yield Statusbar()
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted.

        Sets window title and subtitle, initializes pane count.
        """
        logger.info("Application mounted")
        self.title = "Thegent Compositor"
        self.sub_title = "Terminal UI for Agent Orchestration"
        self._pane_count = 1  # Start with 1 placeholder pane
        # Initialize pane manager with root pane
        self.pane_manager.create_root_pane("pane-0")
        self._update_statusbar()

    def _update_statusbar(self) -> None:
        """Update statusbar with current session info."""
        statusbar = self.query_one(Statusbar)
        session_name = self.session_state.session_id if self.session_state else "default"
        statusbar.update(f"Session: {session_name} | Panes: {self._pane_count} | Ready")

    def action_new_pane(self) -> None:
        """Create a new terminal pane.

        Increments pane count and updates statusbar.
        """
        logger.info("action_new_pane called")
        
        # Initialize pane manager if needed
        if not self.pane_manager.root:
            self.pane_manager.create_root_pane("pane-0")
        
        # Create new pane node
        import uuid
        new_pane_id = f"pane-{uuid.uuid4().hex[:8]}"
        
        # If we have a root, add as child; otherwise create new root
        if self.pane_manager.root and not self.pane_manager.root.is_leaf:
            # Add to existing split
            new_node = self.pane_manager.split_pane("vertical")
        else:
            # Create first split
            if self.pane_manager.root:
                old_id = self.pane_manager.root.pane_id
                self.pane_manager.root.pane_id = f"split-{uuid.uuid4().hex[:8]}"
                self.pane_manager.root.direction = "vertical"
                self.pane_manager.root.is_leaf = False
                from thegent.ui.compositor.pane_manager import PaneNode
                self.pane_manager.root.children = [
                    PaneNode(pane_id=old_id, is_leaf=True),
                    PaneNode(pane_id=new_pane_id, is_leaf=True),
                ]
            else:
                self.pane_manager.create_root_pane(new_pane_id)
        
        self._pane_count = len(self.pane_manager._get_all_leaves(self.pane_manager.root)) if self.pane_manager.root else 1
        self._update_statusbar()
        
        # TODO: Actually create Textual terminal widget and add to layout
        # This requires Textual Terminal widget integration

    def action_split_vertical(self) -> None:
        """Split the current pane vertically.

        Increments pane count and updates statusbar.
        """
        logger.info("action_split_vertical called")
        if not self.pane_manager.root:
            # Initialize root pane if needed
            self.pane_manager.create_root_pane("pane-0")
        
        new_node = self.pane_manager.split_pane("vertical")
        if new_node:
            self._pane_count = len(self.pane_manager._get_all_leaves(self.pane_manager.root))
            self._update_statusbar()

    def action_split_horizontal(self) -> None:
        """Split the current pane horizontally.

        Increments pane count and updates statusbar.
        """
        logger.info("action_split_horizontal called")
        if not self.pane_manager.root:
            # Initialize root pane if needed
            self.pane_manager.create_root_pane("pane-0")
        
        new_node = self.pane_manager.split_pane("horizontal")
        if new_node:
            self._pane_count = len(self.pane_manager._get_all_leaves(self.pane_manager.root))
            self._update_statusbar()

    def action_close_pane(self) -> None:
        """Close the current pane.

        Decrements pane count (if > 1) and updates statusbar.
        """
        logger.info("action_close_pane called")
        if self.pane_manager.close_pane():
            self._pane_count = len(self.pane_manager._get_all_leaves(self.pane_manager.root)) if self.pane_manager.root else 1
            self._update_statusbar()

    def action_focus_next(self) -> None:
        """Focus the next pane.

        Cycles focus through available panes.
        """
        logger.info("action_focus_next called")
        if self.pane_manager.focus_next():
            self._update_statusbar()

    def action_quit(self) -> None:
        """Quit the application.

        Cleans up resources and exits.
        """
        logger.info("Quitting application")
        super().exit()
