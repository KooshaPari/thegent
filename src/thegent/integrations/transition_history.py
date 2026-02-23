# @trace WL-272 B90-W2-B1
"""Append-only history log for local status transitions.

Maintains an audit trail of all status transitions caused by sync operations,
persisted to JSONL format for deterministic replay and compliance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class StatusTransition:
    """Single status transition record.

    Attributes:
        wl_id: Work item identifier (e.g., "WL-272")
        from_status: Source status before transition
        to_status: Target status after transition
        timestamp: ISO 8601 timestamp of transition
        trigger: Trigger reason (e.g., "sync_cycle", "manual")
        cycle_id: Sync cycle identifier (optional)
    """

    wl_id: str
    from_status: str
    to_status: str
    timestamp: str
    trigger: str
    cycle_id: str | None = None


class TransitionHistoryLog:
    """Append-only log for status transitions.

    Persists transitions to JSONL format (one record per line) for
    efficient appending, streaming, and deterministic replay.
    """

    def __init__(self, log_path: Path | str = "docs/reference/transition_history.jsonl"):
        """Initialize the transition history log.

        Args:
            log_path: Path to JSONL log file. Created if it does not exist.
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, transition: StatusTransition) -> None:
        """Append a transition record to the log.

        Args:
            transition: StatusTransition record to append.
        """
        import json

        record = asdict(transition)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record).decode().decode() + "\n")

    def read_all(self) -> list[StatusTransition]:
        """Read all transition records from the log.

        Returns:
            List of StatusTransition records, in chronological order.
        """
        import json

        if not self.log_path.exists():
            return []

        transitions = []
        with open(self.log_path) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    transitions.append(StatusTransition(**data))
        return transitions

    def read_since(self, dt: datetime) -> list[StatusTransition]:
        """Read transition records since a specific datetime.

        Args:
            dt: Datetime cutoff (inclusive). Records with timestamp >= dt are returned.

        Returns:
            List of StatusTransition records matching the time range.
        """
        cutoff_iso = dt.isoformat()
        return [t for t in self.read_all() if t.timestamp >= cutoff_iso]
