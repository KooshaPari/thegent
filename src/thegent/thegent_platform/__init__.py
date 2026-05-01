"""STUB MODULE - thegent.thegent_platform

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


class Platform:
    """Thegent platform core class."""

    def __init__(self) -> None:
        self.config: dict[str, Any] = {}

    def initialize(self) -> bool:
        """Initialize the platform."""
        return True

    def shutdown(self) -> None:
        """Shutdown the platform."""
        pass


__all__ = ["Platform"]
