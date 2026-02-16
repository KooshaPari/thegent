"""thegent plugin for tray application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from thegent.tray.core.plugin_system import SidebarItem, TrayPlugin

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from thegent.tray.plugins.thegent.api_client import ThegentAPIClient


class ThegentPlugin(TrayPlugin):
    """Plugin for thegent integration with the tray application."""

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the plugin.

        Args:
            api_client: The thegent API client.
        """
        self._api_client = api_client
        self._tabs: dict[str, QWidget] = {}

    @property
    def name(self) -> str:
        """Return the plugin name."""
        return "thegent"

    @property
    def sidebar_items(self) -> list[SidebarItem]:
        """Return sidebar items for this plugin."""
        return [
            SidebarItem(
                id="thegent-projects",
                label="Projects",
                icon=None,  # Will be set by the tray application
                section="thegent",
            ),
            SidebarItem(
                id="thegent-agents",
                label="Agents",
                icon=None,
                section="thegent",
            ),
            SidebarItem(
                id="thegent-runs",
                label="Runs",
                icon=None,
                section="thegent",
            ),
            SidebarItem(
                id="thegent-gardener",
                label="Gardener",
                icon=None,
                section="thegent",
            ),
            SidebarItem(
                id="thegent-costs",
                label="Costs",
                icon=None,
                section="thegent",
            ),
            SidebarItem(
                id="thegent-gamification",
                label="Gamification",
                icon=None,
                section="thegent",
            ),
        ]

    def get_tab(self, tab_id: str) -> QWidget | None:
        """Return the widget for the given tab_id (lazy loaded).

        Args:
            tab_id: The tab ID to retrieve.

        Returns:
            The widget for the tab, or None if not found.
        """
        # Return cached tab if already loaded
        if tab_id in self._tabs:
            return self._tabs[tab_id]

        # Lazy load the tab widget - try to import tabs module
        try:
            from thegent.tray.plugins.thegent.tabs import get_tab  # noqa: PLC0415
        except ImportError:
            # Tabs module doesn't exist yet - return None
            return None

        widget = get_tab(tab_id, self._api_client)
        if widget is not None:
            self._tabs[tab_id] = widget

        return self._tabs.get(tab_id)

    @property
    def api_client(self) -> ThegentAPIClient:
        """Return the API client."""
        return self._api_client

    def on_activate(self) -> None:
        """Called when the plugin is activated."""

    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        # Clean up tab widgets
        self._tabs.clear()
