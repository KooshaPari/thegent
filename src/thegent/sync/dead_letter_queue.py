"""Dead-letter queue utilities for board sync replay with backoff and ordering.

# @trace WL-213
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

from typing import Any, Final

DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS: Final[int] = 3
DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS: Final[float] = 60.0
DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER: Final[float] = 2.0


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _parse_float(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


def compute_backoff_seconds(attempt: int, *, base_delay_seconds: float, multiplier: float) -> float:
    """Compute deterministic retry delay in seconds for a given attempt number."""
    if attempt < 0:
        return base_delay_seconds
    if base_delay_seconds <= 0:
        base_delay_seconds = DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS
    if multiplier <= 1:
        return base_delay_seconds
    return base_delay_seconds * (multiplier**attempt)


@dataclass
class RemoteWriteDeadLetterRecord:
    """Single failed remote-write mutation entry."""

    entry_id: str
    source: str
    board_id: str
    item: dict[str, str]
    error: str
    status: str = "pending"
    attempts: int = 0
    first_failed_at: str = ""
    last_attempt_at: str | None = None
    next_attempt_at: str | None = None
    resolved_at: str | None = None
    max_attempts: int = DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS
    retry_interval_seconds: float = DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS
    backoff_multiplier: float = DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def can_retry(self) -> bool:
        return self.is_pending and self.attempts < self.max_attempts

    @property
    def first_failed_at_dt(self) -> datetime:
        return _parse_timestamp(self.first_failed_at) or datetime.now(UTC)

    @property
    def next_attempt_at_dt(self) -> datetime:
        return _parse_timestamp(self.next_attempt_at) or self.first_failed_at_dt

    @property
    def last_attempt_at_dt(self) -> datetime | None:
        return _parse_timestamp(self.last_attempt_at)

    def is_due(self, *, now: datetime) -> bool:
        if not self.can_retry:
            return False
        return self.next_attempt_at_dt <= now

    def mark_success(self, now: datetime) -> "RemoteWriteDeadLetterRecord":
        return replace(
            self,
            status="replayed",
            attempts=self.attempts + 1,
            resolved_at=now.isoformat(),
            last_attempt_at=now.isoformat(),
        )

    def mark_failed(self, *, now: datetime) -> "RemoteWriteDeadLetterRecord":
        attempts = self.attempts + 1
        next_interval = compute_backoff_seconds(
            attempt=attempts - 1,
            base_delay_seconds=self.retry_interval_seconds,
            multiplier=self.backoff_multiplier,
        )
        next_attempt_at = now + timedelta(seconds=max(0.0, next_interval))
        return replace(
            self,
            attempts=attempts,
            last_attempt_at=now.isoformat(),
            next_attempt_at=next_attempt_at.isoformat(),
            status="pending" if attempts < self.max_attempts else "failed",
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RemoteWriteDeadLetterRecord":
        return cls(
            entry_id=str(payload["entry_id"]),
            source=str(payload["source"]),
            board_id=str(payload["board_id"]),
            item=dict(payload["item"]),
            error=str(payload["error"]),
            status=str(payload.get("status", "pending")),
            attempts=_parse_int(payload.get("attempts"), default=0),
            first_failed_at=str(payload.get("first_failed_at", datetime.now(UTC).isoformat())),
            last_attempt_at=str(payload["last_attempt_at"]) if payload.get("last_attempt_at") else None,
            next_attempt_at=str(payload["next_attempt_at"]) if payload.get("next_attempt_at") else None,
            resolved_at=str(payload["resolved_at"]) if payload.get("resolved_at") else None,
            max_attempts=_parse_int(payload.get("max_attempts"), default=DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS),
            retry_interval_seconds=_parse_float(
                payload.get("retry_interval_seconds"),
                default=DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS,
            ),
            backoff_multiplier=_parse_float(
                payload.get("backoff_multiplier"),
                default=DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER,
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "source": self.source,
            "board_id": self.board_id,
            "item": self.item,
            "error": self.error,
            "status": self.status,
            "attempts": self.attempts,
            "first_failed_at": self.first_failed_at,
            "last_attempt_at": self.last_attempt_at,
            "next_attempt_at": self.next_attempt_at,
            "resolved_at": self.resolved_at,
            "max_attempts": self.max_attempts,
            "retry_interval_seconds": self.retry_interval_seconds,
            "backoff_multiplier": self.backoff_multiplier,
        }


class RemoteWriteDeadLetterQueue:
    """Persistent dead-letter queue for board remote writes."""

    def __init__(
        self,
        queue_path: Path,
        *,
        max_attempts: int = DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS,
        retry_interval_seconds: float = DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS,
        backoff_multiplier: float = DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER,
    ) -> None:
        self.queue_path = queue_path
        self.max_attempts = max(1, max_attempts)
        self.retry_interval_seconds = max(1.0, float(retry_interval_seconds))
        self.backoff_multiplier = max(1.0, float(backoff_multiplier))

    def load(self) -> list[RemoteWriteDeadLetterRecord]:
        if not self.queue_path.exists():
            return []

        entries: list[RemoteWriteDeadLetterRecord] = []
        for line in self.queue_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"Dead-letter queue entry must be an object: {line!r}")
            entries.append(RemoteWriteDeadLetterRecord.from_dict(payload))
        return entries

    def write(self, entries: list[RemoteWriteDeadLetterRecord]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = "\n".join(json.dumps(entry.to_dict(), sort_keys=True) for entry in entries)
        self.queue_path.write_text(f"{serialized}\n" if serialized else "", encoding="utf-8")

    def append(self, record: RemoteWriteDeadLetterRecord) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), sort_keys=True))
            handle.write("\n")

    def pending(self, *, source: str | None = None, board_id: str | None = None) -> list[RemoteWriteDeadLetterRecord]:
        return [
            entry
            for entry in self.load()
            if entry.is_pending
            and (source is None or entry.source == source)
            and (board_id is None or entry.board_id == board_id)
        ]

    def candidates_for_replay(
        self, *, now: datetime, source: str | None = None, board_id: str | None = None
    ) -> list[RemoteWriteDeadLetterRecord]:
        return sorted(
            [entry for entry in self.pending(source=source, board_id=board_id) if entry.is_due(now=now)],
            key=lambda entry: (entry.next_attempt_at_dt, entry.attempts, entry.entry_id),
        )

    def create_entry_id(self, source: str, board_id: str, item: dict[str, str], *, error: str) -> str:
        key = json.dumps({"source": source, "board_id": board_id, "item": item, "error": error}, sort_keys=True)
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
        return f"dlq-{digest}"

    def enqueue(self, *, source: str, board_id: str, item: dict[str, str], error: str) -> RemoteWriteDeadLetterRecord:
        now = datetime.now(UTC)
        record = RemoteWriteDeadLetterRecord(
            entry_id=self.create_entry_id(source=source, board_id=board_id, item=item, error=error),
            source=source,
            board_id=board_id,
            item=item,
            error=error,
            first_failed_at=now.isoformat(),
            max_attempts=self.max_attempts,
            retry_interval_seconds=self.retry_interval_seconds,
            backoff_multiplier=self.backoff_multiplier,
        )
        self.append(record)
        return record
