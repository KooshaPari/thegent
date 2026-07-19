"""JSONL audit appender for the operator cockpit's decision stream.

SOTA hardening lane — bridges the in-memory ``decision_notices`` deque
populated by :class:`thegent.ux.cockpit.OperatorCockpit` into a durable
JSONL audit log, so operators running SOTA replay tooling can correlate
inline banners with the same record their governance audit pipeline sees.

The appender is intentionally minimal:

* It exposes a single ``record(notice: DecisionNotice)`` API that mirrors
  the existing ``OverrideEventEmitter._append`` pattern (see
  ``thegent/governance/override_events.py``).
* A bounded background tail (``DecisionAuditTailer``) periodically drains
  the cockpit's decision deque and persists any new notices, so cockpit
  consumers that just ``record_decision(...)`` get audit persistence for
  free.
* Reads (``tail_events``) mirror the override emitter so the audit log
  can be ingested by downstream SOTA replay tooling using the same
  code path.
* Clock injection is honored end-to-end so deterministic replays
  produce byte-identical JSONL output.

This module is **deliberately small and side-effect-free**; the wider
governance JSONL pipeline already lives in
:mod:`thegent.governance.override_events` and is not changed here.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .cockpit import DecisionNotice

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from .cockpit import OperatorCockpit


_LOGGER = logging.getLogger(__name__)


# Default JSONL location, separate from override_events so SOTA replay
# tooling can ingest decisions in isolation. ``~/.thegent/`` is the
# canonical dotfile location (see ``thegent/governance/override_events.py``).
_DEFAULT_AUDIT_PATH = Path("~/.thegent/cockpit_decisions.jsonl").expanduser()

# Bounded background tail cadence. Mirrors OverrideExpiryMonitor's default
# (1s) so behaviour feels consistent for operators.
DEFAULT_TAIL_INTERVAL_S = 1.0


def _decision_to_record(notice: DecisionNotice, *, clock: Callable[[], float]) -> dict[str, object]:
    """Serialize a :class:`DecisionNotice` for JSONL persistence.

    The shape mirrors ``PolicyDecision.to_dict()`` plus the cockpit-only
    fields (``age_s`` is intentionally omitted — it is a render-time
    computation, not a persisted property). The ``emitted_at`` field
    captures when the JSONL line was actually written (vs.
    ``evaluated_at`` which is when the policy was evaluated); this is
    useful for replay tooling that wants to reason about end-to-end
    pipeline latency.
    """
    return {
        "event_type": "cockpit.decision.recorded",
        "verdict": notice.verdict,
        "reason_code": notice.reason_code,
        "rule_id": notice.rule_id,
        "agent": notice.agent,
        "lane": notice.lane,
        "evaluated_at": notice.evaluated_at,
        "emitted_at": clock(),
        "reason": notice.reason,
    }


class DecisionAuditAppender:
    """Append-only JSONL writer for :class:`DecisionNotice` records.

    Mirrors the ``OverrideEventEmitter`` surface so audit tooling can
    learn one API and apply it to both event streams. Files are created
    lazily on the first write; concurrent callers are serialised through
    an instance-level lock.
    """

    def __init__(
        self,
        audit_path: Path | None = None,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        import time as _time

        self._path = (audit_path or _DEFAULT_AUDIT_PATH).expanduser()
        self._lock = threading.Lock()
        # Default to ``time.time`` so callers that don't care about
        # deterministic replays get the same behaviour as the rest of
        # the codebase. Tests pin a frozen clock via the ``clock=`` arg.
        self._clock: Callable[[], float] = clock or _time.time

    def set_clock(self, clock: Callable[[], float]) -> None:
        """Pin the wall clock used for ``emitted_at``."""
        self._clock = clock

    def audit_path(self) -> Path:
        """Return the JSONL path the appender writes to."""
        return self._path

    def record(self, notice: DecisionNotice) -> None:
        """Persist a single :class:`DecisionNotice` to the JSONL log.

        Args:
            notice: Decision to persist. Anything that is not a
                :class:`DecisionNotice` is rejected with ``TypeError`` so
                downstream SOTA tooling can rely on the persisted shape.

        Raises:
            TypeError: ``notice`` is not a :class:`DecisionNotice`.
        """
        if not isinstance(notice, DecisionNotice):
            raise TypeError(f"DecisionAuditAppender.record expects DecisionNotice, got {type(notice).__name__}")
        record = _decision_to_record(notice, clock=self._clock)
        self._append(record)

    def record_many(self, notices: Iterable[DecisionNotice]) -> int:
        """Persist an iterable of notices. Returns the count persisted.

        Invalid items raise ``TypeError`` and abort the batch so callers
        don't end up with a half-written audit log. All items are
        validated before any line is appended.
        """
        records: list[dict[str, object]] = []
        count = 0
        for notice in notices:
            if not isinstance(notice, DecisionNotice):
                raise TypeError(
                    f"DecisionAuditAppender.record_many expects DecisionNotice, got {type(notice).__name__}"
                )
            records.append(_decision_to_record(notice, clock=self._clock))
            count += 1
        # Only now that every item is valid do we open the file and
        # write — a TypeError above leaves the JSONL untouched.
        for record in records:
            self._append(record)
        return count

    def tail_events(self, n: int = 20) -> list[dict[str, object]]:
        """Read the last ``n`` persisted events from the JSONL log.

        Mirrors ``OverrideEventEmitter.tail_events`` so operators can use
        a single ``tail -f`` workflow against both audit streams.
        """
        if not self._path.exists():
            return []
        with self._lock:
            raw = self._path.read_text(encoding="utf-8").splitlines()
        out: list[dict[str, object]] = []
        for line in raw[-n:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                _LOGGER.warning("skipping malformed decision audit line: %.80s", line)
        return out

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _append(self, record: dict[str, object]) -> None:
        """Thread-safe append of a single JSON record."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with self._lock:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line)


@dataclass
class DecisionAuditTailer:
    """Background tailer draining a cockpit's ``decision_notices`` to JSONL.

    The tailer is a thin, daemon-thread wrapper around
    :class:`DecisionAuditAppender` so SOTA replay tooling sees one
    canonical write path for both ``OverrideExpiredEvent`` and
    ``DecisionNotice`` payloads.

    Operators wire this up once at startup::

        cockpit = OperatorCockpit()
        appender = DecisionAuditAppender()
        tailer = DecisionAuditTailer(cockpit, appender)
        tailer.start()
        ...
        tailer.stop()
    """

    cockpit: "OperatorCockpit"
    appender: DecisionAuditAppender
    interval_s: float = DEFAULT_TAIL_INTERVAL_S
    max_batch: int = 64
    _stop_event: threading.Event = field(default_factory=threading.Event)
    _thread: threading.Thread | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _last_seen_index: int = 0

    def start(self) -> None:
        """Start the background tailing thread (idempotent)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="decision-audit-tailer",
            daemon=True,
        )
        self._thread.start()
        _LOGGER.debug("DecisionAuditTailer started (interval=%.2fs)", self.interval_s)

    def stop(self, timeout_s: float = 5.0) -> None:
        """Signal the background thread to stop and wait for it."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout_s)
            self._thread = None
        _LOGGER.debug("DecisionAuditTailer stopped")

    def drain_once(self) -> int:
        """Synchronously drain the cockpit's pending notices to JSONL.

        Returns the number of notices appended this call. Safe to call
        directly from tests or one-shot scripts.
        """
        notices = self._collect_new()
        if not notices:
            return 0
        return self.appender.record_many(notices)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _collect_new(self) -> "Sequence[DecisionNotice]":
        with self._lock:
            with self.cockpit._lock:  # noqa: SLF001 — coordinate with cockpit internal lock
                state = self.cockpit._state  # noqa: SLF001
                buf = list(state.decision_notices)
            # ``buf`` is a bounded deque. ``max_batch`` caps how many
            # items one drain call returns; ``_last_seen_index`` tracks
            # how many items we have already appended so a future call
            # drains whatever arrived after.
            current_size = len(buf)
            last_seen = self._last_seen_index
            new: list[DecisionNotice] = []
            if last_seen <= 0:
                # First call: persist everything currently buffered,
                # capped by max_batch so a single drain never blocks.
                new = buf[: self.max_batch]
            elif last_seen >= current_size:
                # Caught up; nothing new since last drain.
                new = []
            else:
                # Only the most recent ``max_batch`` items are reachable
                # (older items have rolled off the bounded deque). If
                # ``last_seen`` is older than that window we still want
                # to surface the freshest ``max_batch`` so audit
                # pipelines don't silently drop notices.
                window_start = max(0, current_size - self.max_batch)
                start = max(window_start, last_seen)
                new = list(buf[start:current_size])
                if not new and current_size > 0:
                    # ``last_seen`` was older than the overlap window
                    # (the deque rolled over); surface the freshest
                    # ``max_batch`` so we never silently lose notices.
                    new = list(buf[window_start:current_size])
                    self._last_seen_index = current_size - len(new)
            self._last_seen_index = last_seen + len(new)
            return new

    def _run(self) -> None:
        import time as _time

        while not self._stop_event.is_set():
            try:
                self.drain_once()
            except Exception as exc:  # noqa: BLE001 — background loop must never raise
                _LOGGER.warning("decision audit tailer drain failed: %s", exc)
            self._stop_event.wait(self.interval_s)


__all__ = [
    "DEFAULT_TAIL_INTERVAL_S",
    "DecisionAuditAppender",
    "DecisionAuditTailer",
]
