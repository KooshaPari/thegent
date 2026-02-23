"""Plugin system for thegent.

Allows lazy-loading of extensions, commands, and integrations.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Protocol

logger = logging.getLogger(__name__)


class Plugin(Protocol):
    """Protocol for plugins."""

    name: str
    version: str

    def activate(self) -> None:
        """Activate the plugin."""
        ...

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        ...


PluginLoader = Callable[[], Plugin]


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._loaders: dict[str, PluginLoader] = {}
        self._active: set[str] = set()

    def register(self, name: str, loader: PluginLoader) -> None:
        """Register a plugin loader."""
        self._loaders[name] = loader
        logger.info(f"Registered plugin: {name}")

    def activate(self, name: str) -> None:
        """Activate a plugin by name."""
        if name in self._active:
            logger.warning(f"Plugin {name} already active")
            return

        if name not in self._loaders:
            raise KeyError(f"Plugin {name} not registered")

        loader = self._loaders[name]
        plugin = loader()
        plugin.activate()
        self._plugins[name] = plugin
        self._active.add(name)
        logger.info(f"Activated plugin: {name}")

    def deactivate(self, name: str) -> None:
        """Deactivate a plugin by name."""
        if name not in self._active:
            return

        plugin = self._plugins[name]
        plugin.deactivate()
        del self._plugins[name]
        self._active.discard(name)
        logger.info(f"Deactivated plugin: {name}")

    def get(self, name: str) -> Plugin | None:
        """Get an active plugin by name."""
        return self._plugins.get(name)

    def list_active(self) -> list[str]:
        """List all active plugins."""
        return list(self._active)

    def load_plugins_from_dir(self, plugins_dir: Path) -> None:
        """Load all plugins from a directory."""
        if not plugins_dir.exists():
            return

        for entry in plugins_dir.iterdir():
            if entry.is_file() and entry.suffix == ".py" and not entry.name.startswith("_"):
                self._load_plugin_file(entry)
            elif entry.is_dir() and (entry / "__init__.py").exists():
                self._load_plugin_package(entry)

    def _load_plugin_file(self, path: Path) -> None:
        """Load a plugin from a Python file."""
        name = path.stem
        spec = importlib.util.spec_from_file_location(name, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            if hasattr(module, "get_plugin"):
                loader = module.get_plugin
                self.register(name, loader)

    def _load_plugin_package(self, path: Path) -> None:
        """Load a plugin from a Python package."""
        name = path.name
        spec = importlib.util.spec_from_file_location(name, path / "__init__.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            if hasattr(module, "get_plugin"):
                loader = module.get_plugin
                self.register(name, loader)


# Global registry instance
_registry: PluginRegistry | None = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def register_plugin(name: str, loader: PluginLoader) -> None:
    """Register a plugin with the global registry."""
    get_registry().register(name, loader)


def activate_plugin(name: str) -> None:
    """Activate a plugin from the global registry."""
    get_registry().activate(name)


def list_plugins() -> list[str]:
    """List active plugins."""
    return get_registry().list_active()
