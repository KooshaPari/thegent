"""TUI Compositor module for Thegent.

Provides a Textual-based terminal UI compositor for managing multiple terminal panes,
including pane splitting, merging, layout management, and session persistence.

Phase 1 includes:
- Core layout engine for organizing widgets
- Basic component library (OutputWidget, StatusWidget, SidebarWidget, etc.)
- Pane management with split/merge operations
- Session persistence
"""

from thegent.compositor.app import CompositApp
from thegent.compositor.components import (
    DiffViewerPanel,
    FooterStatusBar,
    HeaderWidget,
    MetricsPanel,
    OutputWidget,
    ProgressIndicator,
    SidebarWidget,
    StatusWidget,
)
from thegent.compositor.layout_engine import (
    Direction,
    LayoutConstraints,
    LayoutEngine,
    LayoutNode,
    Margin,
    Padding,
    Size,
    SizeUnit,
)
from thegent.compositor.pane_manager import PaneManager, PaneNode
from thegent.compositor.session_state import SessionState
from thegent.compositor.terminal_pane import TerminalPane

__all__ = [
    # App and management
    "CompositApp",
    "DiffViewerPanel",
    "Direction",
    "FooterStatusBar",
    "HeaderWidget",
    "LayoutConstraints",
    # Layout engine
    "LayoutEngine",
    "LayoutNode",
    "Margin",
    "MetricsPanel",
    # Components
    "OutputWidget",
    "Padding",
    "PaneManager",
    "PaneNode",
    "ProgressIndicator",
    "SessionState",
    "SidebarWidget",
    "Size",
    "SizeUnit",
    "StatusWidget",
    "TerminalPane",
]
