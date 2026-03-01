"""TUI Compositor - Terminal-based multiplexer with pane management.

Main exports:
- CompositApp: Main Textual application
- TerminalPane: PTY-based terminal widget
- PaneManager: Pane tree management
- SessionState: Session persistence
- Panel: Named content panel with lifecycle hooks and error boundary
  (error_fallback, last_error, recover())
- Compositor: Panel collection manager with per-panel error isolation
- CompositorProfiler: Records per-panel render timing data
- RenderProfile: Dataclass holding a single render timing record
"""

from thegent.ui.compositor.app import CompositApp
from thegent.ui.compositor.compositor import (
    CacheStats,
    Compositor,
    CompositorProfiler,
    Panel,
    RenderProfile,
)
from thegent.ui.compositor.pane_manager import PaneManager
from thegent.ui.compositor.session_state import SessionState
from thegent.ui.compositor.terminal_pane import TerminalPane

__all__ = [
    "CacheStats",
    "CompositApp",
    "Compositor",
    "CompositorProfiler",
    "PaneManager",
    "Panel",
    "RenderProfile",
    "SessionState",
    "TerminalPane",
]
