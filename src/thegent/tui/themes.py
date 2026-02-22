"""Theme system for TUI compositor.

Provides theme management with built-in themes and custom theme support.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from textual.css.styles import Styles
from textual.theme import Theme


@dataclass
class ThemeColors:
    """Color palette for a theme."""

    # Primary colors
    primary: str = "#00ff00"  # Terminal green
    secondary: str = "#0088ff"  # Blue
    accent: str = "#ffff00"  # Yellow

    # Status colors
    success: str = "#00cc00"
    warning: str = "#ffcc00"
    error: str = "#ff3333"
    info: str = "#00ccff"

    # Base colors
    foreground: str = "#e0e0e0"
    background: str = "#1a1a1a"
    surface: str = "#2a2a2a"
    panel: str = "#333333"
    highlight: str = "#444444"

    # Text colors
    text: str = "#e0e0e0"
    text_muted: str = "#888888"
    text_dim: str = "#666666"

    # Border colors
    border: str = "#444444"
    border_focus: str = "#00ff00"

    def to_dict(self) -> dict[str, str]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
            "foreground": self.foreground,
            "background": self.background,
            "surface": self.surface,
            "panel": self.panel,
            "highlight": self.highlight,
            "text": self.text,
            "text-muted": self.text_muted,
            "text-dim": self.text_dim,
            "border": self.border,
            "border-focus": self.border_focus,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ThemeColors:
        return cls(
            primary=data.get("primary", cls.primary),
            secondary=data.get("secondary", cls.secondary),
            accent=data.get("accent", cls.accent),
            success=data.get("success", cls.success),
            warning=data.get("warning", cls.warning),
            error=data.get("error", cls.error),
            info=data.get("info", cls.info),
            foreground=data.get("foreground", cls.foreground),
            background=data.get("background", cls.background),
            surface=data.get("surface", cls.surface),
            panel=data.get("panel", cls.panel),
            highlight=data.get("highlight", cls.highlight),
            text=data.get("text", cls.text),
            text_muted=data.get("text-muted", cls.text_muted),
            text_dim=data.get("text-dim", cls.text_dim),
            border=data.get("border", cls.border),
            border_focus=data.get("border-focus", cls.border_focus),
        )


@dataclass
class ThemeDefinition:
    """Complete theme definition."""

    name: str
    colors: ThemeColors
    dark: bool = True
    author: str = ""
    description: str = ""
    extensions: list[str] = field(default_factory=list)

    def to_textual_theme(self) -> Theme:
        """Convert to Textual Theme."""
        c = self.colors
        return Theme(
            name=self.name,
            primary=c.primary,
            secondary=c.secondary,
            accent=c.accent,
            success=c.success,
            warning=c.warning,
            error=c.error,
            foreground=c.foreground,
            background=c.background,
            surface=c.surface,
            panel=c.panel,
            dark=self.dark,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dark": self.dark,
            "author": self.author,
            "description": self.description,
            "extensions": self.extensions,
            "colors": self.colors.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeDefinition:
        colors = ThemeColors.from_dict(data.get("colors", {}))
        return cls(
            name=data.get("name", "unknown"),
            colors=colors,
            dark=data.get("dark", True),
            author=data.get("author", ""),
            description=data.get("description", ""),
            extensions=data.get("extensions", []),
        )


# Built-in themes
def get_builtin_themes() -> list[ThemeDefinition]:
    """Get list of built-in themes."""
    return [
        ThemeDefinition(
            name="thegent-dark",
            dark=True,
            author="thegent",
            description="Default terminal-style dark theme",
            colors=ThemeColors(
                primary="#00ff00",  # Terminal green
                secondary="#0088ff",  # Blue
                accent="#ffff00",  # Yellow
            ),
        ),
        ThemeDefinition(
            name="thegent-light",
            dark=False,
            author="thegent",
            description="Light variant of thegent theme",
            colors=ThemeColors(
                primary="#008800",  # Darker green for light backgrounds
                secondary="#0066cc",  # Darker blue
                accent="#cc8800",  # Darker yellow
                foreground="#1a1a1a",
                background="#f0f0f0",
                surface="#e0e0e0",
                panel="#d0d0d0",
                highlight="#c0c0c0",
                text="#1a1a1a",
                text_muted="#666666",
                text_dim="#888888",
                border="#aaaaaa",
                border_focus="#008800",
            ),
        ),
        ThemeDefinition(
            name="monokai",
            dark=True,
            author="thegent",
            description="Monokai-inspired color scheme",
            colors=ThemeColors(
                primary="#a6e22e",  # Green
                secondary="#66d9ef",  # Blue
                accent="#fd971f",  # Orange
                success="#a6e22e",
                warning="#fd971f",
                error="#f92672",
                foreground="#f8f8f2",
                background="#272822",
                surface="#3e3d32",
                panel="#49483e",
                highlight="#75715e",
                text="#f8f8f2",
                text_muted="#88846f",
                text_dim="#5c5b57",
                border="#49483e",
                border_focus="#a6e22e",
            ),
        ),
        ThemeDefinition(
            name="dracula",
            dark=True,
            author="thegent",
            description="Dracula-inspired theme",
            colors=ThemeColors(
                primary="#50fa7b",  # Green
                secondary="#8be9fd",  # Cyan
                accent="#ffb86c",  # Orange
                success="#50fa7b",
                warning="#f1fa8c",
                error="#ff5555",
                info="#bd93f9",
                foreground="#f8f8f2",
                background="#282a36",
                surface="#44475a",
                panel="#44475a",
                highlight="#6272a4",
                text="#f8f8f2",
                text_muted="#6272a4",
                text_dim="#8be9fd",
                border="#6272a4",
                border_focus="#50fa7b",
            ),
        ),
        ThemeDefinition(
            name="nord",
            dark=True,
            author="thegent",
            description="Nord-inspired polar night theme",
            colors=ThemeColors(
                primary="#88c0d0",  # Cyan
                secondary="#81a1c1",  # Blue
                accent="#ebcb8b",  # Yellow
                success="#a3be8c",
                warning="#ebcb8b",
                error="#bf616a",
                info="#5e81ac",
                foreground="#eceff4",
                background="#2e3440",
                surface="#3b4252",
                panel="#4c566a",
                highlight="#5e81ac",
                text="#eceff4",
                text_muted="#81a1c1",
                text_dim="#4c566a",
                border="#4c566a",
                border_focus="#88c0d0",
            ),
        ),
        ThemeDefinition(
            name="gruvbox",
            dark=True,
            author="thegent",
            description="Gruvbox retro theme",
            colors=ThemeColors(
                primary="#b8bb26",  # Green
                secondary="#83a598",  # Blue
                accent="#fabd2f",  # Yellow
                success="#b8bb26",
                warning="#fabd2f",
                error="#fb4934",
                info="#83a598",
                foreground="#ebdbb2",
                background="#282828",
                surface="#3c3836",
                panel="#504945",
                highlight="#665c54",
                text="#ebdbb2",
                text_muted="#928374",
                text_dim="#665c54",
                border="#504945",
                border_focus="#b8bb26",
            ),
        ),
    ]


class ThemeManager:
    """Manages themes for the TUI compositor."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._themes: dict[str, ThemeDefinition] = {}
        self._current: ThemeDefinition | None = None
        self._storage_dir = storage_dir or Path.home() / ".config" / "thegent" / "themes"
        self._load_builtin()
        self._load_custom()

    def _load_builtin(self) -> None:
        """Load built-in themes."""
        for theme in get_builtin_themes():
            self._themes[theme.name] = theme

    def _load_custom(self) -> None:
        """Load custom themes from storage."""
        themes_dir = self._storage_dir / "custom"
        if not themes_dir.exists():
            return

        for theme_file in themes_dir.glob("*.json"):
            try:
                data = json.loads(theme_file.read_text())
                theme = ThemeDefinition.from_dict(data)
                self._themes[theme.name] = theme
            except Exception:  # noqa: PERF203 - intentional per-item error handling
                pass

    def _save_custom(self, theme: ThemeDefinition) -> None:
        """Save a custom theme to storage."""
        themes_dir = self._storage_dir / "custom"
        themes_dir.mkdir(parents=True, exist_ok=True)

        data = theme.to_dict()
        (themes_dir / f"{theme.name}.json").write_text(json.dumps(data, indent=2))

    def add_theme(self, theme: ThemeDefinition) -> None:
        """Add a custom theme."""
        self._themes[theme.name] = theme
        self._save_custom(theme)

    def get_theme(self, name: str) -> ThemeDefinition | None:
        """Get a theme by name."""
        return self._themes.get(name)

    def list_themes(self) -> list[str]:
        """List all available theme names."""
        return list(self._themes.keys())

    def set_theme(self, name: str) -> bool:
        """Set the current theme."""
        if name in self._themes:
            self._current = self._themes[name]
            return True
        return False

    def get_current(self) -> ThemeDefinition | None:
        """Get the current theme."""
        if self._current is None:
            self._current = self._themes.get("thegent-dark")
        return self._current

    def create_theme(
        self,
        name: str,
        colors: ThemeColors,
        dark: bool = True,
        author: str = "",
        description: str = "",
    ) -> ThemeDefinition:
        """Create and save a new theme."""
        theme = ThemeDefinition(
            name=name,
            colors=colors,
            dark=dark,
            author=author,
            description=description,
        )
        self.add_theme(theme)
        return theme

    def duplicate_theme(self, source: str, new_name: str) -> ThemeDefinition | None:
        """Duplicate an existing theme."""
        source_theme = self._themes.get(source)
        if source_theme:
            new_theme = ThemeDefinition(
                name=new_name,
                colors=source_theme.colors,
                dark=source_theme.dark,
                author=source_theme.author,
                description=f"Duplicate of {source}",
            )
            self.add_theme(new_theme)
            return new_theme
        return None

    def delete_theme(self, name: str) -> bool:
        """Delete a custom theme."""
        if name in self._themes:
            del self._themes[name]
            theme_file = self._storage_dir / "custom" / f"{name}.json"
            if theme_file.exists():
                theme_file.unlink()
            return True
        return False

    def export_theme(self, name: str, path: Path) -> bool:
        """Export a theme to a JSON file."""
        theme = self._themes.get(name)
        if theme:
            path.write_text(json.dumps(theme.to_dict(), indent=2))
            return True
        return False

    def import_theme(self, path: Path) -> ThemeDefinition | None:
        """Import a theme from a JSON file."""
        try:
            data = json.loads(path.read_text())
            theme = ThemeDefinition.from_dict(data)
            self.add_theme(theme)
            return theme
        except Exception:
            return None

    def get_styles(self) -> Styles:
        """Get CSS styles for the current theme."""
        return Styles()

    def apply_to_app(self, app) -> None:
        """Apply current theme to a Textual app."""
        current = self.get_current()
        if current:
            app.theme = current.to_textual_theme()
