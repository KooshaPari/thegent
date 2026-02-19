"""Sitback agent components for never-idle loop.

This package provides:
- watchdog: Non-blocking background task completion detection
- gardening: Proactive gardening checks (governance, backlog, tests, etc.)
- never_idle: Main loop engine for continuous operation
"""

from thegent.sitback.gardening import GardeningManager
from thegent.sitback.never_idle import (
    NeverIdleLoop,
    get_never_idle,
    get_never_idle_status,
    start_never_idle,
    stop_never_idle,
)
from thegent.sitback.watchdog import BackgroundTaskWatcher

__all__ = [
    "BackgroundTaskWatcher",
    "GardeningManager",
    "NeverIdleLoop",
    "get_never_idle",
    "get_never_idle_status",
    "start_never_idle",
    "stop_never_idle",
]
