"""Plugin system for tray application.

Phase 2C DI migration
---------------------
The PluginRegistry class was previously instantiated ad-hoc wherever needed.
A module-level ``_registry`` singleton is now provided for backward
compatibility; new code should create and inject PluginRegistry instances
directly so they can be replaced in tests without module-level state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any


try:
    from PySide6.QtWidgets import QWidget
except ImportError:  # non-GUI environments (CI, headless tests)
    QWidget = Any  # type: ignore[assignment,misc]


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
    """Registry for managing tray plugins.

    Encapsulates formerly global plugin state so it can be created,
    injected, and replaced independently in tests.

    Attributes:
        _plugins: Internal name → plugin mapping.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, TrayPlugin] = {}

    def register(self, name: str, plugin: TrayPlugin) -> None:
        """Register a plugin under *name*.

        Args:
            name: Unique plugin identifier.
            plugin: A TrayPlugin implementation to register.
        """
        self._plugins[name] = plugin

    def get_plugin(self, name: str) -> TrayPlugin | None:
        """Return the plugin registered under *name*, or None if absent."""
        return self._plugins.get(name)

    def unregister(self, name: str) -> None:
        """Remove the plugin registered under *name*.  No-op if absent."""
        self._plugins.pop(name, None)

    def list_plugins(self) -> list[str]:
        """Return the names of all registered plugins."""
        return list(self._plugins.keys())

    def __contains__(self, name: str) -> bool:
        """Support ``'name' in registry`` syntax."""
        return name in self._plugins


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compat shim
# ---------------------------------------------------------------------------

#: Module-level PluginRegistry instance.
#: New code should create and inject PluginRegistry instances directly.
#: This singleton exists so existing callers that import ``_registry``
#: continue to work without modification.
_registry: PluginRegistry = PluginRegistry()


__all__ = [
    "PluginRegistry",
    "SidebarItem",
    "TrayPlugin",
    "_registry",
]
