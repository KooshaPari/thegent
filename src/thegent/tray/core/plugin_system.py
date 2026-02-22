"""Plugin system for tray application."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from PySide6.QtWidgets import QWidget


@dataclass
class SidebarItem:
    """Represents a sidebar navigation item."""

    id: str
    label: str
    icon: Any  # QIcon
    tab_ids: list[str] = field(default_factory=list)
    section: str = "main"


class TrayPlugin(ABC):
    """Abstract base class for tray application plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""

    @property
    @abstractmethod
    def sidebar_items(self) -> list[SidebarItem]:
        """Return sidebar items for this plugin."""

    @abstractmethod
    def get_tab(self, tab_id: str) -> QWidget | None:
        """Return the widget for the given tab_id."""

    @abstractmethod
    def on_activate(self) -> None:
        """Called when the plugin is activated."""

    @abstractmethod
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""


class PluginRegistry:
    """Registry for managing tray plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, TrayPlugin] = {}

    def register(self, name: str, plugin: TrayPlugin) -> None:
        """Register a plugin."""
        self._plugins[name] = plugin

    def get_plugin(self, name: str) -> TrayPlugin | None:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        """List all registered plugin names."""
        return list(self._plugins.keys())
