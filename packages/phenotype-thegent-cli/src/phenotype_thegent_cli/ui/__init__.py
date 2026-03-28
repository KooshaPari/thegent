"""Thegent UI module - TUI compositors, dashboards, and terminal interfaces."""

from phenotype_thegent_cli.ui.compositor.compositor import CompositorProfiler, RenderProfile
from phenotype_thegent_cli.ui.compositor_manager import CompositorManager, CompositorSlot, Layout

__all__ = [
    "CompositorManager",
    "CompositorProfiler",
    "CompositorSlot",
    "Layout",
    "RenderProfile",
]
