"""Core tray application components."""

from thegent_platform.tray.core.plugin_system import PluginRegistry, SidebarItem, TrayPlugin
from thegent_platform.tray.core.shared_widgets import CARD_STYLE, create_status_badge, metric_card

__all__ = [
    "CARD_STYLE",
    "PluginRegistry",
    "SidebarItem",
    "TrayPlugin",
    "create_status_badge",
    "metric_card",
]
