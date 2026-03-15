"""JSONL audit log for pull reflection status changes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import orjson as json

__all__ = ["PullReflectionAuditEntry", "PullReflectionAuditLog"]


@dataclass(frozen=True, slots=True)
class PullReflectionAuditEntry:
    """Single audit record for a reflected pull state change."""

    wl_id: str
    cycle_id: str
    connector: str
    before_status: str
    after_status: str
    timestamp: str
    sync_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict()).decode("utf-8")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PullReflectionAuditEntry":
        return cls(**payload)


class PullReflectionAuditLog:
    """Append-only JSONL audit file with simple read helpers."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, entry: PullReflectionAuditEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as handle:
            handle.write(entry.to_json_line().encode("utf-8"))
            handle.write(b"\n")

    def read_all(self) -> list[PullReflectionAuditEntry]:
        if not self.path.exists():
            return []
        entries: list[PullReflectionAuditEntry] = []
        for line in self.path.read_bytes().splitlines():
            if not line.strip():
                continue
            entries.append(PullReflectionAuditEntry.from_dict(json.loads(line)))
        return entries

    def read_by_cycle(self, cycle_id: str) -> list[PullReflectionAuditEntry]:
        return [entry for entry in self.read_all() if entry.cycle_id == cycle_id]

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
