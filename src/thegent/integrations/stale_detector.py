"""Stale Item Detector — identify dormant items beyond configured age.

Detects items with no local or remote activity beyond age thresholds.

# @trace WL-182
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class StaleConfig:
    """Configuration for stale detection.

    Attributes:
        stale_after_days: Items inactive for this many days are considered stale.
    """

    stale_after_days: int = 14


@dataclass
class StaleItem:
    """A stale item detected by the detector.

    Attributes:
        wl_id: The workstream item identifier.
        last_activity: Timestamp of last activity (local or remote).
        age_days: Age in days since last activity.
        connector: The connector name (e.g., 'github', 'linear').
    """

    wl_id: str
    last_activity: datetime
    age_days: float
    connector: str


class StaleItemDetector:
    """Detector for items inactive beyond configured threshold."""

    def __init__(self, config: StaleConfig | None = None) -> None:
        """Initialize stale detector.

        Args:
            config: StaleConfig with stale_after_days threshold. Uses default if None.
        """
        self.config = config or StaleConfig()

    def is_stale(
        self,
        last_activity: datetime,
        now: datetime | None = None,
    ) -> bool:
        """Check if an item is stale.

        Args:
            last_activity: Timestamp of last activity.
            now: Current time (defaults to UTC now).

        Returns:
            True if age_days >= stale_after_days.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        # Ensure both datetimes are timezone-aware
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        age_seconds = (now - last_activity).total_seconds()
        age_days = age_seconds / (24 * 3600)

        return age_days >= self.config.stale_after_days

    def detect(
        self,
        items: list[dict],
        now: datetime | None = None,
    ) -> list[StaleItem]:
        """Detect stale items from a list.

        Each dict must have: wl_id, last_activity (ISO str or datetime), connector.

        Args:
            items: List of item dicts with wl_id, last_activity, connector.
            now: Current time (defaults to UTC now).

        Returns:
            List of StaleItem objects for items that are stale (only).
        """
        if now is None:
            now = datetime.now(timezone.utc)

        stale_items = []

        for item in items:
            wl_id = item["wl_id"]
            connector = item["connector"]
            last_activity = item["last_activity"]

            # Parse last_activity if it's a string
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity)

            # Ensure timezone-aware
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)

            if self.is_stale(last_activity, now):
                age_seconds = (now - last_activity).total_seconds()
                age_days = age_seconds / (24 * 3600)

                stale_items.append(StaleItem(
                    wl_id=wl_id,
                    last_activity=last_activity,
                    age_days=age_days,
                    connector=connector,
                ))

        return stale_items

    def summary(self, stale_items: list[StaleItem]) -> dict:
        """Generate summary statistics for stale items.

        Args:
            stale_items: List of StaleItem objects.

        Returns:
            Dict with count, oldest_days, and list of connectors.
        """
        if not stale_items:
            return {
                "count": 0,
                "oldest_days": None,
                "connectors": [],
            }

        oldest_days = max(item.age_days for item in stale_items)
        connectors = sorted({item.connector for item in stale_items})

        return {
            "count": len(stale_items),
            "oldest_days": oldest_days,
            "connectors": connectors,
        }
