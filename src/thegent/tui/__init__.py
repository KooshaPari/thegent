"""TUI Compositor for thegent.

A unified terminal user interface combining multiple output streams,
agent status, and interactive controls using Textual.
"""

__version__ = "0.1.0"

from .compositor import CompositorApp, TUIContext, run_tui
from .config import ConfigManager, KeyBinding, TUIConfig, get_config
from .explorer import run_explorer_tui
from .layouts.base import BaseLayout, LayoutConfig
from .layouts.manager import LayoutManager, LayoutState, create_default_layout
from .plugins import (
    BuiltinPlugins,
    ExtensionPlugin,
    Plugin,
    PluginInfo,
    PluginLoader,
    WidgetPlugin,
)
from .session import SessionInfo, SessionPersistence
from .themes import ThemeColors, ThemeDefinition, ThemeManager, get_builtin_themes
from .widgets.dialog import (
    ConfirmDialog,
    Dialog,
    DialogManager,
    DialogResult,
    DialogStyle,
    InputDialog,
    MessageDialog,
    Overlay,
    Toast,
)
from .widgets.menubar import MenubarWidget
from .widgets.statusbar import StatusbarWidget
from .widgets.terminal_pane import TerminalConfig, TerminalManager, TerminalPane

__all__ = [
    # Layouts
    "BaseLayout",
    "BuiltinPlugins",
    # Core
    "CompositorApp",
    "ConfigManager",
    "ConfirmDialog",
    # Dialogs
    "Dialog",
    "DialogManager",
    "DialogResult",
    "DialogStyle",
    "ExtensionPlugin",
    "InputDialog",
    "KeyBinding",
    "LayoutConfig",
    "LayoutManager",
    "LayoutState",
    # Widgets
    "MenubarWidget",
    "MessageDialog",
    "Overlay",
    # Plugins
    "Plugin",
    "PluginInfo",
    "PluginLoader",
    "SessionInfo",
    # Session
    "SessionPersistence",
    "StatusbarWidget",
    # Config
    "TUIConfig",
    "TUIContext",
    "TerminalConfig",
    "TerminalManager",
    "TerminalPane",
    "ThemeColors",
    "ThemeDefinition",
    # Themes
    "ThemeManager",
    "Toast",
    "WidgetPlugin",
    # Version
    "__version__",
    "create_default_layout",
    "get_builtin_themes",
    "get_config",
    "run_tui",
]
