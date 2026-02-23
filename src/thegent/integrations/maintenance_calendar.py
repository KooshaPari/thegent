"""Connector maintenance calendar ingestion and window tracking.

Manages scheduled maintenance windows for connectors to avoid planned outages
during sync operations.

FR traceability: WL-282 (Connector Maintenance Calendar Ingestion)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class MaintenanceWindow:
    """Represents a scheduled maintenance window for a connector."""

    connector: str
    start: datetime
    end: datetime
    reason: str
    project: str = "default"


class MaintenanceCalendar:
    """Manages scheduled maintenance windows for connectors."""

    def __init__(self) -> None:
        """Initialize the maintenance calendar with empty windows."""
        self._windows: list[MaintenanceWindow] = []

    def add_window(self, window: MaintenanceWindow) -> None:
        """Add a maintenance window to the calendar.

        Args:
            window: The maintenance window to add.
        """
        self._windows.append(window)
        logger.debug(f"Added maintenance window for {window.connector}: {window.start} to {window.end}")

    def is_in_maintenance(self, connector: str, at: datetime | None = None) -> bool:
        """Check if a connector has an active maintenance window.

        Args:
            connector: Name of the connector.
            at: Datetime to check (defaults to current UTC time).

        Returns:
            True if connector has an active maintenance window at the given time.
        """
        if at is None:
            at = datetime.now(timezone.utc)

        return any(window.connector == connector and window.start <= at <= window.end for window in self._windows)

    def is_project_in_blackout(self, project: str, connector: str, at: datetime | None = None) -> bool:
        """Check if a project-scoped blackout window is active."""
        if at is None:
            at = datetime.now(timezone.utc)

        project_key = project.strip().lower()
        connector_key = connector.strip().lower()
        return any(
            window.project.strip().lower() == project_key
            and window.connector.strip().lower() == connector_key
            and window.start <= at <= window.end
            for window in self._windows
        )

    def upcoming_windows(self, connector: str, after: datetime | None = None) -> list[MaintenanceWindow]:
        """Get upcoming maintenance windows for a connector.

        Args:
            connector: Name of the connector.
            after: Datetime to search after (defaults to current UTC time).

        Returns:
            List of maintenance windows starting after 'after', sorted by start.
        """
        if after is None:
            after = datetime.now(timezone.utc)

        upcoming = [window for window in self._windows if window.connector == connector and window.start >= after]

        return sorted(upcoming, key=lambda w: w.start)

    def load_from_config(self, config: list[dict]) -> None:
        """Load maintenance windows from configuration.

        Args:
            config: List of dicts with keys 'connector', 'start' (ISO str),
                    'end' (ISO str), 'reason'.

        Raises:
            ValueError: If config dict is missing required keys or has invalid format.
        """
        for item in config:
            missing_keys = {"connector", "start", "end", "reason"} - set(item.keys())
            if missing_keys:
                raise ValueError(f"Config item missing required keys: {missing_keys}")

            try:
                start = datetime.fromisoformat(item["start"])
                end = datetime.fromisoformat(item["end"])
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid datetime format in config: {e}")

            window = MaintenanceWindow(
                connector=item["connector"],
                start=start,
                end=end,
                reason=item["reason"],
                project=str(item.get("project", "default")),
            )
            self.add_window(window)

    def load_project_blackout_config(self, project: str, config: list[dict]) -> None:
        """Load project-scoped blackout windows."""
        for item in config:
            item_with_project = dict(item)
            item_with_project["project"] = project
            self.load_from_config([item_with_project])

    def list_connectors(self) -> list[str]:
        """Get a sorted list of all connectors with maintenance windows.

        Returns:
            Sorted list of unique connector names.
        """
        connectors = {window.connector for window in self._windows}
        return sorted(connectors)


def format_maintenance_banner(*, connector: str, reason: str, project: str = "default") -> str:
    """Render a deterministic maintenance banner string."""
    normalized_reason = reason.strip() or "scheduled maintenance"
    return f"[MAINTENANCE] project={project} connector={connector} reason={normalized_reason}"
