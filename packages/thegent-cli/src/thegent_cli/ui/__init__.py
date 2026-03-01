"""Thegent UI module - TUI compositors, dashboards, and terminal interfaces."""

from thegent_cli.ui.compositor.compositor import CompositorProfiler, RenderProfile
from thegent_cli.ui.compositor_manager import CompositorManager, CompositorSlot, Layout

__all__ = [
    "CompositorManager",
    "CompositorProfiler",
    "CompositorSlot",
    "Layout",
    "RenderProfile",
]
