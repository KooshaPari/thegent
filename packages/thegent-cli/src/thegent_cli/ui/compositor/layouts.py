"""Layout primitives and menubar widget for the TUI compositor.

Re-exports BaseLayout and MenubarWidget for use by CompositorApp.
Imports directly from submodules (not the tui package init) to avoid
circular import issues.
"""

from thegent.tui.layouts.base import BaseLayout, LayoutConfig, LayoutManager
from thegent.tui.widgets.menubar import MenubarWidget, MenuDropdown

__all__ = [
    "BaseLayout",
    "LayoutConfig",
    "LayoutManager",
    "MenuDropdown",
    "MenubarWidget",
]
