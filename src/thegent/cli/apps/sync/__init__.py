"""CLI sync module.

This module provides CLI synchronization functionality.
"""

from __future__ import annotations

from typing import Any


class SyncApp:
    """Sync CLI application."""

    def __init__(self) -> None:
        self.name = "sync"


app: Any = SyncApp()


__all__ = ["app", "SyncApp"]
