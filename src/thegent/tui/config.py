"""Configuration system for TUI compositor.

Provides YAML/JSON configuration file support with validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class TUIConfig:
    """Main TUI compositor configuration."""

    # General settings
    theme: str = "thegent-dark"
    layout: str = "default"
    auto_save: bool = True
    auto_save_interval: int = 30  # seconds

    # Window settings
    title: str = "thegent"
    width: int | None = None
    height: int | None = None
    fullscreen: bool = False

    # Panel settings
    sidebar_visible: bool = True
    sidebar_width: int = 30
    statusbar_visible: bool = True

    # Terminal settings
    shell: str = "/bin/zsh"
    cwd: str = ""
    env: dict[str, str] = field(default_factory=dict)

    # Session settings
    restore_session: bool = True
    max_saved_sessions: int = 10

    # Keybindings (can be overridden)
    keybindings: dict[str, str] = field(default_factory=dict)

    # Plugins to load
    plugins: list[str] = field(default_factory=list)

    # Custom CSS
    custom_css: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "layout": self.layout,
            "auto_save": self.auto_save,
            "auto_save_interval": self.auto_save_interval,
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "fullscreen": self.fullscreen,
            "sidebar_visible": self.sidebar_visible,
            "sidebar_width": self.sidebar_width,
            "statusbar_visible": self.statusbar_visible,
            "shell": self.shell,
            "cwd": self.cwd,
            "env": self.env,
            "restore_session": self.restore_session,
            "max_saved_sessions": self.max_saved_sessions,
            "keybindings": self.keybindings,
            "plugins": self.plugins,
            "custom_css": self.custom_css,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TUIConfig:
        return cls(
            theme=data.get("theme", cls.theme),
            layout=data.get("layout", cls.layout),
            auto_save=data.get("auto_save", cls.auto_save),
            auto_save_interval=data.get("auto_save_interval", cls.auto_save_interval),
            title=data.get("title", cls.title),
            width=data.get("width"),
            height=data.get("height"),
            fullscreen=data.get("fullscreen", cls.fullscreen),
            sidebar_visible=data.get("sidebar_visible", cls.sidebar_visible),
            sidebar_width=data.get("sidebar_width", cls.sidebar_width),
            statusbar_visible=data.get("statusbar_visible", cls.statusbar_visible),
            shell=data.get("shell", cls.shell),
            cwd=data.get("cwd", cls.cwd),
            env=data.get("env", {}),
            restore_session=data.get("restore_session", cls.restore_session),
            max_saved_sessions=data.get("max_saved_sessions", cls.max_saved_sessions),
            keybindings=data.get("keybindings", {}),
            plugins=data.get("plugins", []),
            custom_css=data.get("custom_css", ""),
        )


@dataclass
class KeyBinding:
    """Single key binding."""

    key: str
    action: str
    description: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "action": self.action,
            "description": self.description,
        }


class ConfigManager:
    """Manages TUI configuration."""

    DEFAULT_CONFIG = TUIConfig()

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir or Path.home() / ".config" / "thegent"
        self._config_file = self._config_dir / "tui.yaml"
        self._config: TUIConfig = self.DEFAULT_CONFIG
        self._load()

    def _load(self) -> None:
        """Load configuration from file."""
        if not self._config_file.exists():
            return

        try:
            # Try YAML first
            if self._config_file.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(self._config_file.read_text())
            else:
                data = json.loads(self._config_file.read_text())

            if data:
                self._config = TUIConfig.from_dict(data)
        except Exception:
            pass

    def _save(self) -> None:
        """Save configuration to file."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

        data = self._config.to_dict()
        if self._config_file.suffix in (".yaml", ".yml"):
            self._config_file.write_text(yaml.dump(data, default_flow_style=False))
        else:
            self._config_file.write_text(json.dumps(data, indent=2))

    def get(self) -> TUIConfig:
        """Get current configuration."""
        return self._config

    def set(self, config: TUIConfig) -> None:
        """Set configuration."""
        self._config = config
        self._save()

    def update(self, **kwargs) -> None:
        """Update specific configuration values."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self._save()

    def get_theme(self) -> str:
        """Get current theme."""
        return self._config.theme

    def set_theme(self, theme: str) -> None:
        """Set theme."""
        self._config.theme = theme
        self._save()

    def get_layout(self) -> str:
        """Get current layout."""
        return self._config.layout

    def set_layout(self, layout: str) -> None:
        """Set layout."""
        self._config.layout = layout
        self._save()

    def get_shell(self) -> str:
        """Get shell command."""
        return self._config.shell

    def set_shell(self, shell: str) -> None:
        """Set shell command."""
        self._config.shell = shell
        self._save()

    def get_keybindings(self) -> dict[str, str]:
        """Get custom keybindings."""
        return self._config.keybindings

    def set_keybinding(self, key: str, action: str) -> None:
        """Set a keybinding."""
        self._config.keybindings[key] = action
        self._save()

    def remove_keybinding(self, key: str) -> bool:
        """Remove a keybinding."""
        if key in self._config.keybindings:
            del self._config.keybindings[key]
            self._save()
            return True
        return False

    def get_plugins(self) -> list[str]:
        """Get list of enabled plugins."""
        return self._config.plugins

    def enable_plugin(self, plugin: str) -> None:
        """Enable a plugin."""
        if plugin not in self._config.plugins:
            self._config.plugins.append(plugin)
            self._save()

    def disable_plugin(self, plugin: str) -> bool:
        """Disable a plugin."""
        if plugin in self._config.plugins:
            self._config.plugins.remove(plugin)
            self._save()
            return True
        return False

    def get_custom_css(self) -> str:
        """Get custom CSS."""
        return self._config.custom_css

    def set_custom_css(self, css: str) -> None:
        """Set custom CSS."""
        self._config.custom_css = css
        self._save()

    def reset(self) -> None:
        """Reset to default configuration."""
        self._config = TUIConfig()
        self._save()

    def export(self, path: Path) -> bool:
        """Export configuration to a file."""
        try:
            data = self._config.to_dict()
            path.write_text(yaml.dump(data, default_flow_style=False))
            return True
        except Exception:
            return False

    @classmethod
    def import_config(cls, path: Path, _config_dir: Path | None = None) -> TUIConfig | None:
        """Import configuration from a file."""
        try:
            if path.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(path.read_text())
            else:
                data = json.loads(path.read_text())

            if data:
                return TUIConfig.from_dict(data)
        except Exception:
            pass
        return None


# Convenience function
def get_config(config_dir: Path | None = None) -> ConfigManager:
    """Get the configuration manager."""
    return ConfigManager(config_dir)
