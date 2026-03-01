"""Tabs package for thegent tray plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from thegent_platform.tray.plugins.thegent.tabs.agents import (
    AgentEditDialog,
    AgentsTab,
)
from thegent_platform.tray.plugins.thegent.tabs.agents import (
    get_tab as get_tab_agents,
)
from thegent_platform.tray.plugins.thegent.tabs.costs import (
    CostAlertDialog,
    CostsTab,
)
from thegent_platform.tray.plugins.thegent.tabs.costs import (
    get_tab as get_tab_costs,
)
from thegent_platform.tray.plugins.thegent.tabs.gardener import (
    GardenerConfigDialog,
    GardenerTab,
)
from thegent_platform.tray.plugins.thegent.tabs.gardener import (
    get_tab as get_tab_gardener,
)
from thegent_platform.tray.plugins.thegent.tabs.projects import (
    ProjectEditDialog,
    ProjectsTab,
)
from thegent_platform.tray.plugins.thegent.tabs.projects import (
    get_tab as get_tab_projects,
)
from thegent_platform.tray.plugins.thegent.tabs.gamification import (
    AchievementsDialog,
    GamificationTab,
)
from thegent_platform.tray.plugins.thegent.tabs.gamification import (
    get_tab as get_tab_gamification,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    # Try costs tab
    widget = get_tab_costs(tab_id, api_client)
    if widget is not None:
        return widget

    # Try gardener tab
    widget = get_tab_gardener(tab_id, api_client)
    if widget is not None:
        return widget

    # Try projects tab
    widget = get_tab_projects(tab_id, api_client)
    if widget is not None:
        return widget

    # Try agents tab
    widget = get_tab_agents(tab_id, api_client)
    if widget is not None:
        return widget

    # Try gamification tab
    return get_tab_gamification(tab_id, api_client)


__all__ = [
    "AchievementsDialog",
    "AgentEditDialog",
    "AgentsTab",
    "CostAlertDialog",
    "CostsTab",
    "GamificationTab",
    "GardenerConfigDialog",
    "GardenerTab",
    "ProjectEditDialog",
    "ProjectsTab",
    "get_tab",
]
