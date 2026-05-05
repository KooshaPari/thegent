"""CLI memory module.

This module provides CLI memory functionality.
"""

from __future__ import annotations

from typing import Any


class MemoryApp:
    """Memory CLI application."""

    def __init__(self) -> None:
        self.name = "memory"


app: Any = MemoryApp()


__all__ = ["app", "MemoryApp"]
