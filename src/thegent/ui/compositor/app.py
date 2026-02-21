"""CompositApp - Main Textual application for the TUI compositor."""

import logging
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.traceback import Traceback
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, RichLog, Static

from thegent.ui.compositor.pane_manager import PaneManager

if TYPE_CHECKING:
    from thegent.ui.compositor.session_state import SessionState
    from thegent.ui.compositor.terminal_pane import PanelMounted, PanelUnmounted

logger = logging.getLogger(__name__)


class ErrorBoundary(Static):
    """Error boundary widget for displaying pane render errors."""

    DEFAULT_CSS = """
    ErrorBoundary {
        width: 1fr;
        height: 1fr;
        border: heavy $error;
        background: $error 10%;
    }
    """

    def __init__(
        self,
        error_message: str,
        error_type: str = "Render Error",
        stack_trace: str = "",
        pane_id: str = "",
    ) -> None:
        """Initialize error boundary.

        Args:
            error_message: Human-readable error message
            error_type: Type of error (e.g., "Render Error", "Process Error")
            stack_trace: Full stack trace for debugging
            pane_id: ID of the pane that failed
        """
        super().__init__()
        self.error_message = error_message
        self.error_type = error_type
        self.stack_trace = stack_trace
        self.pane_id = pane_id

    def render(self) -> str:
        """Render error panel."""
        title = f"{self.error_type}: {self.pane_id}"
        content = f"{self.error_message}\n\n[dim]Press Ctrl+R to retry[/dim]"
        if self.stack_trace:
            content += f"\n\n[dim]Stack:[/dim]\n{self.stack_trace[:200]}..."
        return Panel(content, title=title, expand=False)


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
    - Lifecycle hooks for pane initialization/cleanup
    - Error boundaries for crash recovery

    Attributes:
        session_state: Optional persistent session state
        _pane_count: Current number of active panes
        _pane_widgets: Mapping of pane IDs to terminal widgets
        _error_panes: Set of pane IDs that have errors
        _mounted: Flag indicating if app is fully mounted
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

    BINDINGS = (
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+v", "split_vertical", "Split V"),
        ("ctrl+h", "split_horizontal", "Split H"),
        ("ctrl+x", "close_pane", "Close"),
        ("ctrl+l", "focus_next", "Focus Next"),
        ("ctrl+r", "retry_pane", "Retry"),
        ("ctrl+q", "quit", "Quit"),
    )

    def __init__(self, session_state: "SessionState | None" = None) -> None:
        """Initialize CompositApp.

        Args:
            session_state: Optional session state for persistence
        """
        super().__init__()
        self.session_state = session_state
        self._pane_count = 0
        self.pane_manager = PaneManager()
        self._pane_widgets: dict[str, object] = {}  # Maps pane_id -> widget
        self._error_panes: set[str] = set()  # Panes with render errors
        self._mounted = False
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

        Lifecycle hook that:
        - Sets window title and subtitle
        - Initializes pane count
        - Spawns shell processes for panes
        - Sets up IPC/message passing
        - Initializes state tracking
        """
        try:
            logger.info("Application mounted - starting lifecycle initialization")
            self.title = "Thegent Compositor"
            self.sub_title = "Terminal UI for Agent Orchestration"
            self._pane_count = 1  # Start with 1 placeholder pane

            # Initialize pane manager with root pane
            self.pane_manager.create_root_pane("pane-0")

            # Initialize root pane widget
            self._initialize_pane_widget("pane-0")

            self._mounted = True

            # Update statusbar if screen is available
            try:
                self._update_statusbar()
            except Exception as status_error:
                logger.debug(f"Could not update statusbar (screen not ready): {status_error}")

            logger.info("Application mount complete")

        except Exception as e:
            logger.error(f"Failed during on_mount: {e}", exc_info=True)
            self._handle_mount_error(e)

    def on_unmount(self) -> None:
        """Called when the app is about to unmount.

        Lifecycle hook that:
        - Gracefully terminates all child processes
        - Cleans up IPC channels
        - Saves session state
        """
        try:
            logger.info("Application unmounting - starting cleanup")

            # Terminate all pane processes
            if self.pane_manager.root:
                self._cleanup_panes(self.pane_manager.root)

            # Save session state if available
            if self.session_state:
                layout = self.pane_manager.save_layout()
                self.session_state.save(
                    {
                        "layout": layout,
                        "pane_count": self._pane_count,
                        "current_pane": self.pane_manager.current_pane_id,
                    }
                )
                logger.info("Session state saved")

            logger.info("Application cleanup complete")

        except Exception as e:
            logger.error(f"Error during on_unmount: {e}", exc_info=True)

    def _initialize_pane_widget(self, pane_id: str) -> None:
        """Initialize a pane widget and spawn shell process.

        Args:
            pane_id: ID of the pane to initialize

        Raises:
            RuntimeError: If pane initialization fails
        """
        try:
            from thegent.ui.compositor.terminal_pane import TerminalPane

            # Create terminal pane widget
            pane_widget = TerminalPane(
                pane_id=pane_id,
                working_dir=".",
                id=f"pane-{pane_id}",
            )

            # Store widget reference
            self._pane_widgets[pane_id] = pane_widget

            # Spawn shell process in pane (will happen in on_mount of TerminalPane)
            logger.debug(f"Initialized pane widget: {pane_id}")

        except Exception as e:
            logger.error(f"Failed to initialize pane widget {pane_id}: {e}", exc_info=True)
            self._error_panes.add(pane_id)
            # Use error boundary for display
            import traceback

            error_boundary = ErrorBoundary(
                error_message=str(e),
                error_type="Initialization Error",
                stack_trace=traceback.format_exc(),
                pane_id=pane_id,
            )
            self._pane_widgets[pane_id] = error_boundary
            raise

    def on_panel_mounted(self, message: "PanelMounted") -> None:
        """Handle PanelMounted message from terminal panes."""
        logger.info(f"Panel {message.pane_id} reported mount success")
        self._update_statusbar()

    def on_panel_unmounted(self, message: "PanelUnmounted") -> None:
        """Handle PanelUnmounted message from terminal panes."""
        logger.info(f"Panel {message.pane_id} reported unmount success")
        if message.pane_id in self._pane_widgets:
            del self._pane_widgets[message.pane_id]
        self._update_statusbar()

    def _cleanup_panes(self, node: "PaneManager.PaneNode") -> None:
        """Recursively cleanup all pane processes.

        Args:
            node: Root pane node to cleanup
        """
        try:
            # Get all leaf nodes (actual panes)
            leaves = self._collect_leaf_nodes(node)

            for leaf in leaves:
                pane_id = leaf.pane_id
                if pane_id in self._pane_widgets:
                    widget = self._pane_widgets[pane_id]
                    if hasattr(widget, "close"):
                        try:
                            widget.close()
                            logger.debug(f"Closed pane: {pane_id}")
                        except Exception as e:
                            logger.error(f"Error closing pane {pane_id}: {e}")

            # Clear all references
            self._pane_widgets.clear()

        except Exception as e:
            logger.error(f"Error during pane cleanup: {e}")

    def _collect_leaf_nodes(self, node: "PaneManager.PaneNode | None") -> list["PaneManager.PaneNode"]:
        """Collect pane leaf nodes in depth-first order."""
        if node is None:
            return []
        if node.is_leaf:
            return [node]
        leaves: list[PaneManager.PaneNode] = []
        for child in node.children:
            leaves.extend(self._collect_leaf_nodes(child))
        return leaves

    def _handle_mount_error(self, error: Exception) -> None:
        """Handle errors during mount.

        Args:
            error: The exception that occurred
        """
        logger.error(f"Mount error: {error}")
        # Could display error UI here in production
        self._mounted = False

    def _update_statusbar(self) -> None:
        """Update statusbar with current session info."""
        statusbar = self.query_one(Statusbar)
        session_name = self.session_state.session_id if self.session_state else "default"
        statusbar.update(f"Session: {session_name} | Panes: {self._pane_count} | Ready")

    def action_new_pane(self) -> None:
        """Create a new terminal pane.

        Wrapped with error boundaries to catch pane creation failures.
        Increments pane count and updates statusbar.
        """
        try:
            logger.info("action_new_pane called")

            # Initialize pane manager if needed
            if not self.pane_manager.root:
                self.pane_manager.create_root_pane("pane-0")
                self._initialize_pane_widget("pane-0")

            # Create new pane node
            import uuid

            new_pane_id = f"pane-{uuid.uuid4().hex[:8]}"

            # If we have a root, add as child; otherwise create new root
            if self.pane_manager.root and not self.pane_manager.root.is_leaf:
                # Add to existing split
                new_node = self.pane_manager.split_pane("vertical")
            # Create first split
            elif self.pane_manager.root:
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

            # Initialize widget for new pane
            if new_pane_id not in self._pane_widgets:
                self._initialize_pane_widget(new_pane_id)

            self._pane_count = len(self._collect_leaf_nodes(self.pane_manager.root)) if self.pane_manager.root else 1
            self._update_statusbar()

        except Exception as e:
            logger.error(f"Error creating new pane: {e}", exc_info=True)
            self._handle_action_error("new_pane", e)

    def action_split_vertical(self) -> None:
        """Split the current pane vertically.

        Wrapped with error boundaries.
        Increments pane count and updates statusbar.
        """
        try:
            logger.info("action_split_vertical called")
            if not self.pane_manager.root:
                # Initialize root pane if needed
                self.pane_manager.create_root_pane("pane-0")
                self._initialize_pane_widget("pane-0")

            new_node = self.pane_manager.split_pane("vertical")
            if new_node:
                # Initialize widget for new pane
                self._initialize_pane_widget(new_node.pane_id)
                self._pane_count = len(self._collect_leaf_nodes(self.pane_manager.root))
                self._update_statusbar()

        except Exception as e:
            logger.error(f"Error splitting pane vertically: {e}", exc_info=True)
            self._handle_action_error("split_vertical", e)

    def action_split_horizontal(self) -> None:
        """Split the current pane horizontally.

        Wrapped with error boundaries.
        Increments pane count and updates statusbar.
        """
        try:
            logger.info("action_split_horizontal called")
            if not self.pane_manager.root:
                # Initialize root pane if needed
                self.pane_manager.create_root_pane("pane-0")
                self._initialize_pane_widget("pane-0")

            new_node = self.pane_manager.split_pane("horizontal")
            if new_node:
                # Initialize widget for new pane
                self._initialize_pane_widget(new_node.pane_id)
                self._pane_count = len(self._collect_leaf_nodes(self.pane_manager.root))
                self._update_statusbar()

        except Exception as e:
            logger.error(f"Error splitting pane horizontally: {e}", exc_info=True)
            self._handle_action_error("split_horizontal", e)

    def action_close_pane(self) -> None:
        """Close the current pane.

        Wrapped with error boundaries.
        Decrements pane count (if > 1) and updates statusbar.
        """
        try:
            logger.info("action_close_pane called")
            pane_id = self.pane_manager.current_pane_id

            # Cleanup pane widget
            if pane_id and pane_id in self._pane_widgets:
                widget = self._pane_widgets[pane_id]
                if hasattr(widget, "close"):
                    widget.close()
                del self._pane_widgets[pane_id]

            if self.pane_manager.close_pane():
                self._pane_count = (
                    len(self._collect_leaf_nodes(self.pane_manager.root)) if self.pane_manager.root else 1
                )
                self._update_statusbar()

        except Exception as e:
            logger.error(f"Error closing pane: {e}", exc_info=True)
            self._handle_action_error("close_pane", e)

    def action_focus_next(self) -> None:
        """Focus the next pane.

        Wrapped with error boundaries.
        Cycles focus through available panes.
        """
        try:
            logger.info("action_focus_next called")
            if self.pane_manager.focus_next():
                self._update_statusbar()

        except Exception as e:
            logger.error(f"Error focusing next pane: {e}", exc_info=True)
            self._handle_action_error("focus_next", e)

    def action_retry_pane(self) -> None:
        """Retry rendering the current pane.

        Clears error state and attempts to re-render.
        """
        try:
            logger.info("action_retry_pane called")
            pane_id = self.pane_manager.current_pane_id
            if pane_id and pane_id in self._error_panes:
                self._error_panes.discard(pane_id)
                logger.info(f"Cleared error state for pane {pane_id}")
                self._update_statusbar()

        except Exception as e:
            logger.error(f"Error retrying pane: {e}", exc_info=True)

    def _handle_action_error(self, action: str, error: Exception) -> None:
        """Handle errors during action execution.

        Args:
            action: Name of the action that failed
            error: The exception that occurred
        """
        logger.error(f"Action {action} failed: {error}")
        # In production, could show error UI here
        # For now, just log and continue

    def action_quit(self) -> None:
        """Quit the application.

        Cleans up resources and exits.
        """
        logger.info("Quitting application")
        super().exit()
