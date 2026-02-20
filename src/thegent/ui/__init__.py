"""Thegent UI module - TUI compositors, dashboards, and terminal interfaces."""

from thegent.ui.compositor.compositor import CompositorProfiler, RenderProfile
from thegent.ui.compositor_manager import CompositorManager, CompositorSlot, Layout

__all__ = [
    "CompositorManager",
    "CompositorProfiler",
    "CompositorSlot",
    "Layout",
    "RenderProfile",
]
