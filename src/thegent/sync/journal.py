"""Local sync decision journal primitives.

# @trace WL-203
"""

from __future__ import annotations

import orjson as json
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SyncDecisionEntry:
    """A replayable decision made during a sync cycle."""

    entry_id: str
    cycle_id: str
    wl_id: str
    decision: str
    rationale: str
    before_state: dict[str, Any]
    after_state: dict[str, Any]
    replayable: bool
    created_at: str

    @classmethod
    def create(
        cls,
        *,
        cycle_id: str,
        wl_id: str,
        decision: str,
        rationale: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        replayable: bool = True,
    ) -> "SyncDecisionEntry":
        return cls(
            entry_id=str(uuid.uuid4())[:8],
            cycle_id=cycle_id,
            wl_id=wl_id,
            decision=decision,
            rationale=rationale,
            before_state=before_state,
            after_state=after_state,
            replayable=replayable,
            created_at=datetime.now(UTC).isoformat(),
        )


class LocalDecisionJournal:
    """Strict JSONL journal for sync decision replay."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def append(self, entry: SyncDecisionEntry) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(entry).decode(), sort_keys=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def read_all(self) -> list[SyncDecisionEntry]:
        if not self._path.exists():
            return []

        entries: list[SyncDecisionEntry] = []
        with self._path.open("r", encoding="utf-8") as handle:
            for line_num, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json_loads(line)
                    entries.append(SyncDecisionEntry(**payload))
                except Exception as exc:  # noqa: BLE001 -- strict failure is intentional
                    raise ValueError(f"invalid journal line {line_num}: {exc}") from exc
        return entries

    def read_replayable(self) -> list[SyncDecisionEntry]:
        return [entry for entry in self.read_all() if entry.replayable]
