"""Machine-readable conflict queue persistence.

# @trace WL-205
"""

from __future__ import annotations

import orjson as json
from dataclasses import asdict
from pathlib import Path

from thegent_sync.sync.conflicts import SyncConflict


class ConflictQueueStore:
    """JSON-backed conflict queue store."""

    def __init__(self, queue_path: Path) -> None:
        self._queue_path = queue_path

    @property
    def queue_path(self) -> Path:
        return self._queue_path

    def load(self) -> list[SyncConflict]:
        if not self._queue_path.exists():
            return []
        with self._queue_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict) or "conflicts" not in payload:
            raise ValueError("queue payload must be an object with 'conflicts'")
        conflicts = payload["conflicts"]
        if not isinstance(conflicts, list):
            raise ValueError("'conflicts' must be a list")
        return [SyncConflict(**item) for item in conflicts]

    def add(self, conflict: SyncConflict) -> None:
        current = self.load()
        if any(item.conflict_id == conflict.conflict_id for item in current):
            raise ValueError(f"conflict already exists: {conflict.conflict_id}")
        current.append(conflict)
        self._write(current)

    def pending(self) -> list[SyncConflict]:
        return [entry for entry in self.load() if not entry.resolved]

    def resolve(self, conflict_id: str) -> None:
        current = self.load()
        updated: list[SyncConflict] = []
        found = False
        for entry in current:
            if entry.conflict_id == conflict_id:
                found = True
                updated.append(
                    SyncConflict(
                        conflict_id=entry.conflict_id,
                        wl_id=entry.wl_id,
                        field=entry.field,
                        local_value=entry.local_value,
                        remote_value=entry.remote_value,
                        connector=entry.connector,
                        resolved=True,
                    )
                )
                continue
            updated.append(entry)
        if not found:
            raise KeyError(f"conflict not found: {conflict_id}")
        self._write(updated)

    def _write(self, conflicts: list[SyncConflict]) -> None:
        self._queue_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._queue_path.with_suffix(".tmp")
        payload = {
            "version": 1,
            "conflicts": [asdict(entry) for entry in conflicts],
        }
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        temp_path.replace(self._queue_path)
