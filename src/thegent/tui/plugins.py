"""Plugin system for TUI compositor.

Provides dynamic loading of external widgets and extensions.
"""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult
    from textual.widget import Widget


@dataclass
class PluginInfo:
    """Metadata about a plugin."""

    name: str
    version: str
    author: str
    description: str
    entry_point: str
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies or [],
        }


class Plugin:
    """Base class for TUI plugins."""

    def __init__(self, info: PluginInfo) -> None:
        self.info = info
        self._enabled = True
        self._loaded = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        """Load the plugin."""
        self._loaded = True

    def unload(self) -> None:
        """Unload the plugin."""
        self._loaded = False

    def get_widgets(self) -> list[type[Widget]]:
        """Get widgets provided by this plugin."""
        return []

    def get_compose(self) -> ComposeResult:
        """Get widgets to compose into the app."""
        return []

    def on_mount(self) -> None:
        """Called when plugin is mounted."""

    def on_unmount(self) -> None:
        """Called when plugin is unmounted."""


class PluginLoader:
    """Loads and manages plugins."""

    def __init__(self, plugin_dir: Path | None = None) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._plugin_dir = plugin_dir or Path.home() / ".config" / "thegent" / "plugins"
        self._callbacks: list[Callable[[str], None]] = []

    def _load_plugin_module(self, path: Path) -> type[Plugin] | None:
        """Load a plugin module from a path."""
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)

            if hasattr(module, "create_plugin"):
                return module.create_plugin
        except Exception:
            pass
        return None

    def _discover_plugin(self, path: Path) -> PluginInfo | None:
        """Discover plugin info from a path."""
        # Check for plugin.json
        info_file = path / "plugin.json"
        if info_file.exists():
            try:
                import json

                data = json.loads(info_file.read_text())
                return PluginInfo(
                    name=data.get("name", path.name),
                    version=data.get("version", "0.1.0"),
                    author=data.get("author", ""),
                    description=data.get("description", ""),
                    entry_point=data.get("entry_point", "plugin.py"),
                    dependencies=data.get("dependencies", []),
                )
            except Exception:
                pass

        # Check for __init__.py with create_plugin
        init_file = path / "__init__.py"
        if init_file.exists():
            try:
                spec = importlib.util.spec_from_file_location(path.name, init_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "PLUGIN_INFO"):
                        info = module.PLUGIN_INFO
                        if isinstance(info, dict):
                            return PluginInfo(**info)
            except Exception:
                pass

        return None

    def discover_plugins(self) -> list[PluginInfo]:
        """Discover available plugins."""
        plugins = []

        if not self._plugin_dir.exists():
            return plugins

        for item in self._plugin_dir.iterdir():
            if item.is_dir():
                info = self._discover_plugin(item)
                if info:
                    plugins.append(info)

        return plugins

    def load_plugin(self, name: str) -> Plugin | None:
        """Load a plugin by name."""
        if name in self._plugins:
            return self._plugins[name]

        plugin_dir = self._plugin_dir / name
        if not plugin_dir.exists():
            return None

        # Check for plugin info
        info = self._discover_plugin(plugin_dir)
        if not info:
            return None

        # Load the module
        entry_point = info.entry_point
        module_path = plugin_dir / entry_point

        create_plugin = self._load_plugin_module(module_path)
        if create_plugin is None:
            return None

        try:
            plugin = create_plugin(info)
            if isinstance(plugin, Plugin):
                plugin.load()
                self._plugins[name] = plugin
                return plugin
        except Exception:
            pass

        return None

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self._plugins:
            plugin = self._plugins[name]
            plugin.unload()
            del self._plugins[name]
            return True
        return False

    def get_plugin(self, name: str) -> Plugin | None:
        """Get a loaded plugin."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        """List loaded plugin names."""
        return list(self._plugins.keys())

    def get_plugin_info(self, name: str) -> PluginInfo | None:
        """Get info about a plugin."""
        plugin = self._plugins.get(name)
        if plugin:
            return plugin.info
        return None

    def on_plugin_load(self, callback: Callable[[str], None]) -> None:
        """Register a callback for plugin loading."""
        self._callbacks.append(callback)

    def reload_all(self) -> None:
        """Reload all plugins."""
        for name in list(self._plugins.keys()):
            self.unload_plugin(name)
            self.load_plugin(name)


class WidgetPlugin(Plugin):
    """Plugin that provides custom widgets."""

    def __init__(self, info: PluginInfo) -> None:
        super().__init__(info)
        self._widget_classes: list[type[Widget]] = []

    def register_widget(self, widget_class: type[Widget]) -> None:
        """Register a widget class."""
        self._widget_classes.append(widget_class)

    def get_widgets(self) -> list[type[Widget]]:
        return self._widget_classes


class ExtensionPlugin(Plugin):
    """Plugin that extends compositor functionality."""

    def __init__(self, info: PluginInfo) -> None:
        super().__init__(info)
        self._hooks: dict[str, list[Callable]] = {}

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback."""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    def call_hooks(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """Call all hooks for an event."""
        results = []
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                with contextlib.suppress(Exception):
                    results.append(callback(*args, **kwargs))
        return results


# Built-in plugins registry
class BuiltinPlugins:
    """Registry of built-in plugins."""

    @staticmethod
    def create_terminal_plugin(info: PluginInfo) -> Plugin:
        """Create the terminal plugin."""
        from thegent.tui.widgets.terminal_pane import TerminalPane

        class TerminalPlugin(WidgetPlugin):
            def __init__(self, info: PluginInfo) -> None:
                super().__init__(info)
                self.register_widget(TerminalPane)

        return TerminalPlugin(info)

    @staticmethod
    def create_dialog_plugin(info: PluginInfo) -> Plugin:
        """Create the dialog plugin."""
        from thegent.tui.widgets.dialog import Dialog, Overlay, Toast

        class DialogPlugin(WidgetPlugin):
            def __init__(self, info: PluginInfo) -> None:
                super().__init__(info)
                self.register_widget(Dialog)
                self.register_widget(Toast)
                self.register_widget(Overlay)

        return DialogPlugin(info)

    @staticmethod
    def create_status_plugin(info: PluginInfo) -> Plugin:
        """Create the status bar plugin."""
        from thegent.tui.widgets.statusbar import StatusbarWidget

        class StatusPlugin(WidgetPlugin):
            def __init__(self, info: PluginInfo) -> None:
                super().__init__(info)
                self.register_widget(StatusbarWidget)

        return StatusPlugin(info)

    PLUGINS: ClassVar[dict[str, Any]] = {
        "terminal": create_terminal_plugin,
        "dialog": create_dialog_plugin,
        "status": create_status_plugin,
    }

    @classmethod
    def get_plugin(cls, name: str, info: PluginInfo | None = None) -> Plugin | None:
        """Get a built-in plugin by name."""
        if info is None:
            info = PluginInfo(
                name=name,
                version="0.1.0",
                author="thegent",
                description=f"Built-in {name} plugin",
                entry_point="",
            )

        if name in cls.PLUGINS:
            return cls.PLUGINS[name](info)
        return None
