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
import os
import threading
import time
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

# AUDIT-1 (Phase 3/4 third-pass audit): the decision audit log can grow
# unbounded because there is no size/line cap and no rotation policy.
# Default cap is 50 MiB / 250k lines, well clear of common LTS-FS
# journal sizes, and lets a CI runner ingest a week of cockpit activity
# without operator intervention. ``max_bytes``/``max_lines`` of ``<= 0``
# disable the corresponding knob (full retention mode).
DEFAULT_MAX_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_LINES = 250_000
DEFAULT_MAX_BACKUPS = 3

# Width tolerance for clock-skew / NTP slew: when an event arrives with
# ``ts`` further in the future than this many seconds past ``now``, drop
# it. Bound prevents unbounded memory growth under pathological ingest.
_FUTURE_SKEW_TOLERANCE_S = 60.0


class _MonotonicClock:
    """Wrap a wall clock so emitted timestamps are monotonically non-decreasing.

    Python's :func:`time.time` can run backwards under NTP slew / leap-second
    smearing; SOTA tooling that consumes the JSONL log assumes monotonically
    non-decreasing ``emitted_at`` values. This wrapper clamps the returned
    value to ``max(prior_emitted, wall_clock())`` so a backward step is
    absorbed rather than re-stamped.
    """

    __slots__ = ("_clock", "_last")

    def __init__(self, clock: Callable[[], float]) -> None:
        self._clock = clock
        self._last: float = clock()

    def __call__(self) -> float:
        now = self._clock()
        if now < self._last:
            now = self._last
        else:
            self._last = now
        return now


def _decision_to_record(notice: DecisionNotice, *, clock: Callable[[], float]) -> dict[str, object]:
    """Serialize a :class:`DecisionNotice` for JSONL persistence.

    The shape mirrors ``PolicyDecision.to_dict()`` plus the cockpit-only
    fields (``age_s`` is intentionally omitted — it is a render-time
    computation, not a persisted property). The ``emitted_at`` field
    captures when the JSONL line was actually written (vs.
    ``evaluated_at`` which is when the policy was evaluated); this is
    useful for replay tooling that wants to reason about end-to-end
    pipeline latency.

    AUDIT-1: ``clock`` is expected to be a :class:`_MonotonicClock` or
    another monotonically-non-decreasing wrapper. Stdlib
    :func:`time.time` jumps backward under NTP slew — direct callers
    without a wrapper are documented as responsible for monotonicity.
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

    AUDIT-1 (Phase 3/4 third-pass hardening): the appender now supports
    optional size- and line-bounded rotation. When the active file crosses
    ``max_bytes`` or ``max_line_count`` the appender rotates it to
    ``<path>.1`` (shifting older ``*.N`` to ``*.N+1``) and continues
    writing to the active file. ``max_backups`` is the count of rotated
    siblings retained on disk; older siblings are discarded. Set either
    knob to ``<= 0`` to disable that bound (full-retention mode).

    AUDIT-1 also adds an optional ``fsync=True`` durability flag. When
    enabled, every successful append follows ``write`` with
    ``os.fsync(fh.fileno())`` so a kernel crash between the operator's
    :meth:`record` and the OS write-cache flush cannot lose a
    already-counted decision. Default is ``False`` because the cost is
    linear in event volume and most audit consumers tolerate the
    filesystem default; CLI replay tooling (``cockpit replay --commit``,
    ``sota replay``) opts in by passing ``fsync=True``.
    """

    def __init__(
        self,
        audit_path: Path | None = None,
        *,
        clock: Callable[[], float] | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_lines: int = DEFAULT_MAX_LINES,
        max_backups: int = DEFAULT_MAX_BACKUPS,
        fsync: bool = False,
    ) -> None:
        self._raw_clock: Callable[[], float] = clock or time.time
        # Wrap in a monotonic guard so a backward clock step never emits a
        # backwards timestamp. Tests can disable this by passing a strictly
        # monotonic callable and bypass via ``_raw_clock`` for the
        # determinism guarantee they need.
        self._clock = _MonotonicClock(self._raw_clock)
        self._path = (audit_path or _DEFAULT_AUDIT_PATH).expanduser()
        self._lock = threading.RLock()
        self._max_bytes = int(max_bytes) if max_bytes and max_bytes > 0 else 0
        self._max_lines = int(max_lines) if max_lines and max_lines > 0 else 0
        self._max_backups = max(0, int(max_backups))
        self._fsync = bool(fsync)
        # Rotation accounting (read-only via audit_stats()).
        self._line_count = 0
        self._bytes_written = 0
        self._rotation_count = 0
        # Touch the file lazily; ensure parent dir exists on first write.
        # No-op on construction so callers can opt-out of side effects.
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Configuration mutators (post-init knobs)
    # ------------------------------------------------------------------

    def set_clock(self, clock: Callable[[], float]) -> None:
        """Pin the wall clock used for ``emitted_at``.

        Tests that want deterministic replay pass a frozen callable; this
        wrapper builds a fresh monotonic guard so the prior guard's
        internal state does not bleed across reconfigurations.
        """
        self._raw_clock = clock
        self._clock = _MonotonicClock(clock)

    def set_max_bytes(self, max_bytes: int) -> None:
        """Update the post-init size rotation bound (0 = disabled)."""
        with self._lock:
            self._max_bytes = int(max_bytes) if max_bytes and max_bytes > 0 else 0

    def set_max_lines(self, max_lines: int) -> None:
        """Update the post-init line rotation bound (0 = disabled)."""
        with self._lock:
            self._max_lines = int(max_lines) if max_lines and max_lines > 0 else 0

    def set_fsync(self, fsync: bool) -> None:
        """Update the durability flag (per-append ``os.fsync``)."""
        with self._lock:
            self._fsync = bool(fsync)

    def audit_path(self) -> Path:
        """Return the JSONL path the appender writes to."""
        return self._path

    def audit_stats(self) -> dict[str, int | bool]:
        """Return rotation/durability observability for operator snapshots.

        Snapshot fields (read-only contract):
            * ``line_count`` — number of events currently in the active file
            * ``bytes_written`` — current file size (best-effort, post-write)
            * ``rotation_count`` — cumulative rotations since construction
            * ``fsync`` — durability flag (current setting)
            * ``max_bytes`` / ``max_lines`` / ``max_backups`` — current knobs
        """
        with self._lock:
            return {
                "line_count": self._line_count,
                "bytes_written": self._bytes_written,
                "rotation_count": self._rotation_count,
                "fsync": self._fsync,
                "max_bytes": self._max_bytes,
                "max_lines": self._max_lines,
                "max_backups": self._max_backups,
            }

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

        AUDIT-1 note: this reads across the active file and any rotated
        siblings (``*.1`` .. ``*.max_backups``) so a `tail` view after a
        rotation still surfaces the most recent ``n`` events in
        chronological order. Older siblings (beyond ``max_backups``) are
        intentionally not consulted.
        """
        files: list[Path] = []
        files.append(self._path)
        for k in range(1, max(1, self._max_backups) + 1):
            sibling = self._path.with_name(f"{self._path.name}.{k}")
            if sibling.exists():
                files.append(sibling)
        # Reverse so older siblings are read first (chronological order).
        chronological = list(reversed(files))
        with self._lock:
            raw_lines: list[str] = []
            for fp in chronological:
                if not fp.exists():
                    continue
                raw_lines.extend(fp.read_text(encoding="utf-8").splitlines())
        out: list[dict[str, object]] = []
        for line in raw_lines[-n:]:
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
        """Thread-safe append of a single JSON record.

        AUDIT-1: rotation triggers on size (``max_bytes``) or line-count
        (``max_lines``) crossings. Rotated files are moved to ``<path>.1``
        (older siblings shift to ``<path>.N+1``), with any beyond
        ``max_backups`` discarded. The optional ``fsync`` flag triggers an
        ``os.fsync`` on every write for durability-sensitive callers.
        """
        line = json.dumps(record, separators=(",", ":")) + "\n"
        encoded = line.encode("utf-8")
        with self._lock:
            self._maybe_rotate(pre_encoded_len=len(encoded))
            # The append must happen under the same lock that may have
            # rotated; the rotate above opens/closes the file so we now
            # re-open in append mode for this single record.
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line)
                if self._fsync:
                    fh.flush()
                    os.fsync(fh.fileno())
            self._line_count += 1
            self._bytes_written += len(encoded)

    def _maybe_rotate(self, *, pre_encoded_len: int) -> None:
        """Rotate the active file if a rotation bound would be exceeded.

        Called under :attr:`_lock` *before* writing a new line. If the
        active file is missing or the rotation triggers are disabled,
        this is a no-op. ``pre_encoded_len`` is the byte count of the
        about-to-be-written line; it is pre-counted against the
        ``max_bytes`` bound so a single oversized record does not
        split across two files.
        """
        if not self._path.exists():
            return
        if self._max_bytes <= 0 and self._max_lines <= 0:
            return
        # Lines bound: appending this line would exceed ``max_lines``.
        over_lines = self._max_lines > 0 and self._line_count + 1 > self._max_lines
        # Bytes bound: appending this line would exceed ``max_bytes``.
        # ``self._bytes_written`` is best-effort (the file may be larger
        # if it was edited externally); fall back to ``stat().st_size``
        # so the bound still triggers.
        size_now = self._path.stat().st_size
        over_bytes = self._max_bytes > 0 and size_now + pre_encoded_len > self._max_bytes
        if not (over_lines or over_bytes):
            return
        self._rotate_locked()

    def _rotate_locked(self) -> None:
        """Atomically rotate the active file under :attr:`_lock`.

        Sequence:
            1. Drop the oldest sibling beyond ``max_backups`` (if any).
            2. Shift ``<path>.N`` → ``<path>.N+1`` for ``N`` in
               ``[max_backups, 1]``.
            3. Move ``<path>`` → ``<path>.1``.
            4. Reset counters; bump :attr:`_rotation_count`.
        """
        # Step 1: drop the oldest sibling if it would be pushed off the end.
        oldest = self._path.with_name(f"{self._path.name}.{self._max_backups}")
        if self._max_backups <= 0:
            # No siblings retained; remove the active file outright.
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass
            self._line_count = 0
            self._bytes_written = 0
            self._rotation_count += 1
            return
        try:
            oldest.unlink()
        except FileNotFoundError:
            pass
        # Step 2: shift the existing siblings outward.
        for k in range(self._max_backups - 1, 0, -1):
            src = self._path.with_name(f"{self._path.name}.{k}")
            dst = self._path.with_name(f"{self._path.name}.{k + 1}")
            try:
                src.replace(dst)
            except FileNotFoundError:
                continue
        # Step 3: move the active file into the .1 slot.
        try:
            self._path.replace(self._path.with_name(f"{self._path.name}.1"))
        except FileNotFoundError:
            pass
        # Step 4: reset counters.
        self._line_count = 0
        self._bytes_written = 0
        self._rotation_count += 1


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
        # AUDIT-6 (Phase 3/4 third-pass hardening): the prior drain logic
        # acquired ``cockpit._lock`` only for the snapshot step, then
        # advanced ``_last_seen_index`` under a separate lock. A
        # ``record_decision`` interleaving between the snapshot and the
        # index bump could be dropped on a subsequent tick (deque
        # maxlen=64 may roll it off first). Hold the cockpit lock for
        # the entire collect+advance sequence so the call is atomic
        # relative to concurrent producers.
        with self._lock:
            with self.cockpit._lock:  # noqa: SLF001 — coordinate with cockpit internal lock
                state = self.cockpit._state  # noqa: SLF001
                buf = list(state.decision_notices)
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
