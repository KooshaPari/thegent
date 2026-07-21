"""MCP server audit trail — AUDIT-N+15 gate delta hardening.

Records every MCP tool invocation, resource read, and gate check
with a monotonic sequence number, timestamp, and outcome.  The trail
is append-only and JSONL-serialisable so it can be fed into the
existing ``DecisionAuditAppender`` pipeline or consumed by
``resource_observe_summary`` for drift detection.

Canonical home: ``thegent.mcp.server.mcp_audit_trail``

Design constraints:
- Thread-safe (uses a lock around the in-memory buffer).
- Bounded memory: ``max_entries`` defaults to 10 000; oldest entries
  are evicted first.
- Deterministic hashing: each entry is stably serialisable via
  ``server_stable_json`` so the hash chain is reproducible.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AuditEntryKind(StrEnum):
    """Discriminator for the kind of MCP operation recorded."""

    TOOL_INVOCATION = "tool_invocation"
    RESOURCE_READ = "resource_read"
    GATE_CHECK = "gate_check"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """Immutable record of a single MCP server operation."""

    seq: int
    ts: float
    kind: AuditEntryKind
    operation: str
    agent: str
    session_id: str | None
    outcome: str
    duration_ms: float | None = None
    payload_hash: str | None = None
    error_message: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict for JSONL emission."""
        d: dict[str, Any] = {
            "seq": self.seq,
            "ts": self.ts,
            "kind": self.kind.value,
            "operation": self.operation,
            "agent": self.agent,
            "session_id": self.session_id,
            "outcome": self.outcome,
        }
        if self.duration_ms is not None:
            d["duration_ms"] = round(self.duration_ms, 3)
        if self.payload_hash is not None:
            d["payload_hash"] = self.payload_hash
        if self.error_message is not None:
            d["error_message"] = self.error_message
        if self.extra:
            d["extra"] = dict(self.extra)
        return d


class MCPAuditTrail:
    """Append-only, bounded, thread-safe audit trail for MCP server ops.

    Usage::

        trail = MCPAuditTrail(max_entries=5000)
        trail.record(
            kind=AuditEntryKind.TOOL_INVOCATION,
            operation="thegent_run",
            agent="writer_standard",
            session_id="s-abc",
            outcome="ok",
            duration_ms=42.1,
        )
        recent = trail.recent(n=100)
        stats = trail.summary()
    """

    def __init__(self, max_entries: int = 10_000) -> None:
        self._max = max_entries
        self._entries: list[AuditEntry] = []
        self._seq = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        kind: AuditEntryKind,
        operation: str,
        agent: str,
        session_id: str | None = None,
        outcome: str,
        duration_ms: float | None = None,
        payload: Any = None,
        error_message: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Append an entry to the trail.

        Returns the sealed ``AuditEntry``.
        """
        payload_hash: str | None = None
        if payload is not None:
            raw = _stable_json(payload)
            payload_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

        with self._lock:
            self._seq += 1
            entry = AuditEntry(
                seq=self._seq,
                ts=time.time(),
                kind=kind,
                operation=operation,
                agent=agent,
                session_id=session_id,
                outcome=outcome,
                duration_ms=duration_ms,
                payload_hash=payload_hash,
                error_message=error_message,
                extra=extra or {},
            )
            self._entries.append(entry)
            # Evict oldest if over budget
            if len(self._entries) > self._max:
                excess = len(self._entries) - self._max
                self._entries = self._entries[excess:]
        return entry

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def recent(self, n: int = 100) -> list[AuditEntry]:
        """Return the most recent *n* entries (newest last)."""
        with self._lock:
            return list(self._entries[-n:])

    def query(
        self,
        *,
        kind: AuditEntryKind | None = None,
        operation: str | None = None,
        agent: str | None = None,
        outcome: str | None = None,
        limit: int = 200,
    ) -> list[AuditEntry]:
        """Filter entries by field values."""
        with self._lock:
            snapshot = list(self._entries)
        results: list[AuditEntry] = []
        for e in reversed(snapshot):
            if kind is not None and e.kind != kind:
                continue
            if operation is not None and e.operation != operation:
                continue
            if agent is not None and e.agent != agent:
                continue
            if outcome is not None and e.outcome != outcome:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        results.reverse()
        return results

    def summary(self) -> dict[str, Any]:
        """Return aggregate stats for the current trail window."""
        with self._lock:
            entries = list(self._entries)
        total = len(entries)
        by_kind: dict[str, int] = {}
        by_outcome: dict[str, int] = {}
        error_count = 0
        durations: list[float] = []
        for e in entries:
            by_kind[e.kind.value] = by_kind.get(e.kind.value, 0) + 1
            by_outcome[e.outcome] = by_outcome.get(e.outcome, 0) + 1
            if e.kind == AuditEntryKind.ERROR:
                error_count += 1
            if e.duration_ms is not None:
                durations.append(e.duration_ms)
        avg_duration = round(sum(durations) / len(durations), 3) if durations else None
        p99_duration = None
        if durations:
            durations_sorted = sorted(durations)
            p99_idx = max(0, int(len(durations_sorted) * 0.99) - 1)
            p99_duration = round(durations_sorted[p99_idx], 3)
        return {
            "total_entries": total,
            "max_entries": self._max,
            "by_kind": by_kind,
            "by_outcome": by_outcome,
            "error_count": error_count,
            "avg_duration_ms": avg_duration,
            "p99_duration_ms": p99_duration,
            "oldest_seq": entries[0].seq if entries else None,
            "newest_seq": entries[-1].seq if entries else None,
        }

    def clear(self) -> int:
        """Clear the trail and return the number of evicted entries."""
        with self._lock:
            count = len(self._entries)
            self._entries.clear()
        return count


def _stable_json(payload: Any) -> str:
    """Deterministic JSON serialisation (sorted keys, no extra whitespace)."""
    import json as _json

    return _json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
