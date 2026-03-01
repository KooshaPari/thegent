"""thegent plugin for tray application."""

from thegent_platform.tray.plugins.thegent.api_client import (
    Agent,
    CostSummary,
    GamificationStats,
    GardenerStatus,
    Project,
    Run,
    ThegentAPIClient,
)
from thegent_platform.tray.plugins.thegent.plugin import ThegentPlugin

__all__ = [
    "Agent",
    "CostSummary",
    "GamificationStats",
    "GardenerStatus",
    "Project",
    "Run",
    "ThegentAPIClient",
    "ThegentPlugin",
]
