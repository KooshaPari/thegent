"""WP-5004: Non-critical deferral rules."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class DeferralRule:
    """Rule for deferring non-critical tasks."""

    def __init__(self, id: str, condition: str, action: str) -> None:
        self.id = id
        self.condition = condition
        self.action = action


class DeferralManager:
    """Manages deferral of non-critical tasks under high load."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.deferral_log = settings.session_dir / "deferred_tasks.jsonl"

    def should_defer(self, task_priority: str, load_level: float) -> bool:
        """
        Determine if a task should be deferred.
        Priority: P0 (critical) to P3 (low).
        """
        if task_priority == "P0":
            return False  # Never defer critical tasks

        if load_level > 0.9:
            return True  # Defer all non-P0 at very high load

        if load_level > 0.7 and task_priority in ["P2", "P3"]:
            return True  # Defer low priority at high load

        return False

    def defer_task(self, task_id: str, reason: str):
        """Record a task as deferred."""
        _log.info("Deferring task %s: %s", task_id, reason)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "task_id": task_id,
            "reason": reason,
            "status": "deferred",
        }
        self.settings.session_dir.mkdir(parents=True, exist_ok=True)
        with self.deferral_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def list_deferred(self) -> list[dict[str, Any]]:
        """List all currently deferred tasks."""
        if not self.deferral_log.exists():
            return []
        deferred = []
        with self.deferral_log.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    deferred.append(json.loads(line))
                except Exception:
                    continue
        return deferred
