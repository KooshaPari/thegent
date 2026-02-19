"""TUI Compositor - Terminal-based multiplexer with pane management.

Main exports:
- CompositApp: Main Textual application
- TerminalPane: PTY-based terminal widget
- PaneManager: Pane tree management
- SessionState: Session persistence
"""

from thegent.ui.compositor.app import CompositApp
from thegent.ui.compositor.pane_manager import PaneManager
from thegent.ui.compositor.session_state import SessionState
from thegent.ui.compositor.terminal_pane import TerminalPane

__all__ = [
    "CompositApp",
    "PaneManager",
    "SessionState",
    "TerminalPane",
]
