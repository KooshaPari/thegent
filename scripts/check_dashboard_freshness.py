#!/usr/bin/env python3
"""Validate that .quality/loc-metrics.json is fresh (within 7 days).

Exits 0 if the metrics file exists and its timestamp is within the last 7 days.
Exits 1 if the file is stale, missing, or has an invalid timestamp.

# @trace WL-135 B90-W3-C3
"""

from __future__ import annotations

import orjson as json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
METRICS_PATH = ROOT / ".quality" / "loc-metrics.json"
STALE_THRESHOLD_DAYS = 7


def check_freshness() -> tuple[bool, str]:
    """Check freshness of loc-metrics.json.

    Returns:
        (is_fresh, status_message) tuple.
        is_fresh is True if the file exists and is within STALE_THRESHOLD_DAYS.
    """
    if not METRICS_PATH.exists():
        return False, f"STALE: {METRICS_PATH} does not exist. Run: uv run python scripts/collect_loc_metrics.py"

    try:
        data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, f"ERROR: Could not read {METRICS_PATH}: {exc}"

    ts_str = data.get("timestamp")
    if not ts_str:
        return False, f"ERROR: 'timestamp' key missing in {METRICS_PATH}"

    try:
        ts = datetime.fromisoformat(ts_str)
    except ValueError as exc:
        return False, f"ERROR: Could not parse timestamp '{ts_str}': {exc}"

    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    now = datetime.now(tz=timezone.utc)
    age = now - ts
    threshold = timedelta(days=STALE_THRESHOLD_DAYS)

    if age > threshold:
        return False, (
            f"STALE: loc-metrics.json is {age.days} day(s) old (threshold: {STALE_THRESHOLD_DAYS} days). "
            f"Last updated: {ts_str}. Run: uv run python scripts/collect_loc_metrics.py"
        )

    total_loc = data.get("total_loc", "N/A")
    total_files = data.get("total_files", "N/A")
    return True, (
        f"FRESH: loc-metrics.json is {age.seconds // 3600}h {(age.seconds % 3600) // 60}m old "
        f"({age.days} day(s)). total_loc={total_loc}, total_files={total_files}. "
        f"Last updated: {ts_str}"
    )


if __name__ == "__main__":
    is_fresh, message = check_freshness()
    print(message)
    sys.exit(0 if is_fresh else 1)
