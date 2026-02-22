"""Sync maintenance freeze controls.

# @trace WL-206
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class FreezeState:
    reason: str
    actor: str
    frozen_at: str


class SyncController:
    """Controls write freeze/unfreeze state for sync operations."""

    def __init__(self, state_path: Path) -> None:
        self._state_path = state_path

    def freeze(self, *, reason: str, actor: str) -> FreezeState:
        if self.is_frozen():
            raise RuntimeError("sync writes are already frozen")
        state = FreezeState(reason=reason, actor=actor, frozen_at=datetime.now(UTC).isoformat())
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        with self._state_path.open("w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, indent=2, sort_keys=True)
            handle.write("\n")
        return state

    def unfreeze(self, *, actor: str) -> None:
        if not self.is_frozen():
            raise RuntimeError("sync writes are not frozen")
        self._state_path.unlink()

    def is_frozen(self) -> bool:
        return self._state_path.exists()

    def status(self) -> FreezeState | None:
        if not self.is_frozen():
            return None
        with self._state_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return FreezeState(**payload)

    def assert_writes_allowed(self) -> None:
        state = self.status()
        if state is None:
            return
        raise RuntimeError(f"sync writes frozen by {state.actor}: {state.reason}")

