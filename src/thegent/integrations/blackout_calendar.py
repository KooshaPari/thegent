"""Blackout Calendar Support for operational scheduling.

WL-222: Blackout Calendar Support
Manages blackout windows where operations are not permitted, enabling
maintenance windows and operational exclusions.

# @trace WL-222
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlackoutWindow:
    """A blackout period during which operations are not permitted."""

    name: str
    start: datetime
    end: datetime


class BlackoutCalendar:
    """Manages blackout windows for operational scheduling."""

    def __init__(self) -> None:
        """Initialize an empty blackout calendar."""
        self._windows: dict[str, BlackoutWindow] = {}

    def add(self, name: str, start: datetime, end: datetime) -> BlackoutWindow:
        """Add a blackout window to the calendar.

        Args:
            name: Unique name for the blackout window.
            start: Start time of the blackout period.
            end: End time of the blackout period.

        Returns:
            The created BlackoutWindow.

        Raises:
            ValueError: If a window with this name already exists, or if end <= start.
        """
        if name in self._windows:
            raise ValueError(f"Blackout window '{name}' already exists")
        if end <= start:
            raise ValueError("Blackout window end time must be after start time")

        window = BlackoutWindow(name=name, start=start, end=end)
        self._windows[name] = window
        return window

    def is_blacked_out(self, dt: datetime) -> bool:
        """Check if a datetime falls within any blackout window.

        Args:
            dt: The datetime to check.

        Returns:
            True if dt falls within any blackout window, False otherwise.
        """
        return any(window.start <= dt < window.end for window in self._windows.values())

    def active_windows(self, dt: datetime) -> list[BlackoutWindow]:
        """Get all blackout windows that contain the given datetime.

        Args:
            dt: The datetime to check.

        Returns:
            List of BlackoutWindow objects containing dt, sorted by start time.
        """
        active = [w for w in self._windows.values() if w.start <= dt < w.end]
        return sorted(active, key=lambda w: w.start)

    def all_windows(self) -> list[BlackoutWindow]:
        """Get all blackout windows in the calendar.

        Returns:
            List of all BlackoutWindow objects, sorted by start time.
        """
        return sorted(self._windows.values(), key=lambda w: w.start)
