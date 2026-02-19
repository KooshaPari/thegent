"""Base layout classes for TUI compositor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from textual.css.styles import Styles


@dataclass
class LayoutConfig:
    """Configuration for a layout."""

    name: str
    sidebar_visible: bool = True
    output_maximized: bool = False
    sidebar_width: int = 30
    output_height: int = 70
    custom_styles: dict[str, Any] | None = None


class BaseLayout:
    """Base class for layout managers."""

    DEFAULT_CONFIG = LayoutConfig(name="default")

    def __init__(self, config: LayoutConfig | None = None) -> None:
        self.config = config or self.DEFAULT_CONFIG
        self._saved_states: dict[str, LayoutConfig] = {}

    def get_config(self) -> LayoutConfig:
        """Get current layout configuration."""
        return self.config

    def apply_config(self, config: LayoutConfig) -> None:
        """Apply a layout configuration."""
        self.config = config

    def save_state(self, name: str) -> None:
        """Save current layout state."""
        self._saved_states[name] = self.get_config()

    def restore_state(self, name: str) -> bool:
        """Restore a saved layout state."""
        if name in self._saved_states:
            self.apply_config(self._saved_states[name])
            return True
        return False

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self.config.sidebar_visible = not self.config.sidebar_visible

    def toggle_maximize(self) -> None:
        """Toggle output maximization."""
        self.config.output_maximized = not self.config.output_maximized

    def reset(self) -> None:
        """Reset to default layout."""
        self.config = LayoutConfig(name="default")

    def get_styles(self) -> Styles:
        """Get CSS styles for the current layout."""
        styles = Styles()

        if self.config.sidebar_visible:
            styles.set("#sidebar", width=f"{self.config.sidebar_width}%", display="block")
        else:
            styles.set("#sidebar", display="none")

        if self.config.output_maximized:
            styles.set("#output-pane", width="100%")
        else:
            styles.set("#output-pane", width=f"{100 - self.config.sidebar_width}%")

        return styles


class LayoutManager:
    """Manages multiple layouts and transitions."""

    def __init__(self) -> None:
        self._layouts: dict[str, BaseLayout] = {}
        self._current: str | None = None

    def add_layout(self, name: str, layout: BaseLayout) -> None:
        """Add a named layout."""
        self._layouts[name] = layout

    def switch_layout(self, name: str) -> bool:
        """Switch to a named layout."""
        if name in self._layouts:
            self._current = name
            return True
        return False

    def get_current_layout(self) -> BaseLayout | None:
        """Get the current layout."""
        if self._current and self._current in self._layouts:
            return self._layouts[self._current]
        return None

    def list_layouts(self) -> list[str]:
        """List available layout names."""
        return list(self._layouts.keys())


# Predefined layouts
class SidebarLeftLayout(BaseLayout):
    def get_config(self) -> LayoutConfig:
        return LayoutConfig(name="sidebar-left", sidebar_visible=True, sidebar_width=30)

    def apply_config(self, config: LayoutConfig) -> None:
        self.config = config


class FullOutputLayout(BaseLayout):
    def get_config(self) -> LayoutConfig:
        return LayoutConfig(name="full-output", sidebar_visible=False, output_maximized=True)

    def apply_config(self, config: LayoutConfig) -> None:
        self.config = config
