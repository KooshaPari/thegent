"""WL-182 stale workstream item detector."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


def _utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class ItemActivity:
    """Local and remote movement timestamps for one work item."""

    item_id: str
    last_local_movement_at: datetime | None
    last_remote_movement_at: datetime | None


@dataclass(frozen=True)
class StaleItem:
    """Detection result for one stale item."""

    item_id: str
    stale_local_days: float
    stale_remote_days: float
    reason: str


@dataclass(frozen=True)
class StaleDetectorConfig:
    """Aging thresholds for stale movement checks."""

    local_threshold: timedelta
    remote_threshold: timedelta

    def __post_init__(self) -> None:
        if self.local_threshold.total_seconds() <= 0:
            raise ValueError("local_threshold must be positive")
        if self.remote_threshold.total_seconds() <= 0:
            raise ValueError("remote_threshold must be positive")


class StaleItemDetector:
    """Detect items with no local and remote movement beyond thresholds."""

    def __init__(self, config: StaleDetectorConfig) -> None:
        self.config = config

    def detect(self, items: list[ItemActivity], *, now: datetime | None = None) -> list[StaleItem]:
        now_utc = _utc(now or datetime.now(timezone.utc))
        assert now_utc is not None

        stale: list[StaleItem] = []
        for item in items:
            local_ts = _utc(item.last_local_movement_at)
            remote_ts = _utc(item.last_remote_movement_at)
            if local_ts and local_ts > now_utc:
                raise ValueError(f"local movement in future for {item.item_id}")
            if remote_ts and remote_ts > now_utc:
                raise ValueError(f"remote movement in future for {item.item_id}")

            local_age = (now_utc - local_ts) if local_ts else timedelta.max
            remote_age = (now_utc - remote_ts) if remote_ts else timedelta.max

            if local_age >= self.config.local_threshold and remote_age >= self.config.remote_threshold:
                stale.append(
                    StaleItem(
                        item_id=item.item_id,
                        stale_local_days=local_age.total_seconds() / 86400,
                        stale_remote_days=remote_age.total_seconds() / 86400,
                        reason=(
                            "No local or remote movement past thresholds: "
                            f"local={local_age}, remote={remote_age}"
                        ),
                    )
                )

        return stale
