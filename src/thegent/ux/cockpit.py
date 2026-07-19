"""Operator Cockpit: 4-pane live dashboard for thegent runs.

Implements:

* WP-4001 (Batch 7A) — Operator cockpit with traffic/lane/confidence/overrides
* FR-015, FR-039 — Progressive disclosure for transport / model picks
* FR-UX-007, OBS8, P-060, P-090, P-092 — operator-first UX

The cockpit is a **plain-Python** rendering engine that produces a single
``render()`` string per frame.  It does not depend on ``textual``,
``prompt_toolkit``, or any curses binding so it can be embedded in
non-interactive contexts (logs, ``rich.console.Console.print``,
``rich.live.Live``, CI capture, etc.).

Layout (4 panes):
    ┌───────────────────────┬─────────────────────────┐
    │ 1. Live Runs          │ 2. Lane Distribution    │
    │    (active, queued)   │    (counts per lane)     │
    ├───────────────────────┼─────────────────────────┤
    │ 3. Confidence Spark   │ 4. Active Overrides     │
    │    (P50, P95 trend)   │    (TTL countdowns)     │
    └───────────────────────┴─────────────────────────┘

The cockpit is **stateful**: callers feed it ``tick(events)`` once per
``DAG_TICK_MS`` (default 1000ms) and read out ``render()`` or individual
``snapshot()`` for downstream consumers.

Public surface:
  - ``CockpitPane`` — enum of the four panes
  - ``CockpitConfig`` — dataclass configuring the cockpit
  - ``OperatorCockpit`` — main entry point; ``tick()`` then ``render()``
  - ``render_cockpit(events)`` — convenience wrapper for one-shot rendering

Traces to: FR-015 (progressive disclosure), FR-039 (transport hints),
          FR-UX-007 (operator cockpit), OBS8 (realtime telemetry),
          P-060 (lane routing), P-090 (cockpit latency SLO),
          P-092 (progressive disclosure), WP-4001 (cockpit scaffolding),
          WP-4002 (explanations companion).
"""

from __future__ import annotations

import logging
import threading
import time
import weakref
from collections import Counter, deque
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DEFAULT_DAG_TICK_MS = 1000
MAX_RUNS_PANE_ROWS = 14
MAX_OVERRIDE_PANE_ROWS = 6
# Maximum number of decision notices kept in the bounded deque. Older
# notices roll off silently; full history is reachable via the JSONL
# audit log (``DecisionAuditAppender``).
MAX_DECISION_NOTICES = 64
# Cap on rendered rows in the decision-history pane. Slightly smaller
# than the bounded deque size (64) so the inline pane stays scannable;
# older notices are reachable through the JSONL audit log.
MAX_DECISION_PANE_ROWS = 8
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"
# How long an OverrideExpiryNotice stays visible in the inline banner
# before fading out. 30s matches the cockpit tick cadence and gives the
# operator enough time to glance up between DAG ticks.
OVERRIDE_BANNER_MAX_AGE_S = 30.0
# Default wall-clock function (overridable per-cockpit for deterministic
# audit replays; see ``OperatorCockpit(clock=...)``).
_DEFAULT_CLOCK: Callable[[], float] = staticmethod(time.time)


class CockpitPane(StrEnum):
    """The four panes of the operator cockpit."""

    RUNS = "runs"
    LANES = "lanes"
    CONFIDENCE = "confidence"
    OVERRIDES = "overrides"


class RunState(StrEnum):
    """Lifecycle states of a run."""

    QUEUED = "queued"
    ACTIVE = "active"
    PAUSED = "paused"
    DONE = "done"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Configuration & event model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CockpitConfig:
    """Configuration knobs for the cockpit render."""

    title: str = "thegent operator cockpit"
    tick_ms: int = DEFAULT_DAG_TICK_MS
    show_sparkline: bool = True
    sparkline_width: int = 24
    progress_total: int = 100  # for the progress bar (P-081)
    progress_label: str = "Run progress"
    pane_labels: Mapping[CockpitPane, str] = field(
        default_factory=lambda: {
            CockpitPane.RUNS: "Live Runs",
            CockpitPane.LANES: "Lane Distribution",
            CockpitPane.CONFIDENCE: "Confidence (P50/P95)",
            CockpitPane.OVERRIDES: "Active Overrides",
        }
    )


@dataclass(frozen=True)
class RunEvent:
    """Single run state observed by the cockpit (per tick)."""

    run_id: str
    state: RunState
    lane: str = "standard"
    agent: str = ""
    confidence: float | None = None
    elapsed_s: float = 0.0
    note: str = ""


@dataclass(frozen=True)
class OverrideEvent:
    """Single active override observed by the cockpit."""

    rule_id: str
    by: str
    reason: str
    expires_in_s: float
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OverrideExpiryNotice:
    """A single most-recent override-expiry event surfaced to the operator.

    Bridges WP-3003 (``OverrideEventEmitter`` writes the
    ``governance.override.expired`` JSONL line) to the WP-4001 cockpit UX
    surface. Operators can connect an :class:`OverrideExpiryMonitor` (or
    any tail-reader of the JSONL log) and call
    :meth:`OperatorCockpit.record_override_event` to surface recent
    expiry lines inline in the cockpit header.

    Attributes:
        rule_id: Policy rule whose override expired (e.g. ``"no-network"``).
        owner: Principal who applied the override.
        reason: Free-form reason text (``"ttl_elapsed"`` by default).
        expired_at: Unix timestamp of expiry.
        age_s: Seconds since expiry at render time. Updated lazily on
            every render so an old notice naturally fades out.
    """

    rule_id: str
    owner: str
    reason: str
    expired_at: float
    age_s: float = 0.0


@dataclass(frozen=True)
class DecisionNotice:
    """A governance decision surfaced to the operator cockpit (WP-3001 -> WP-4001).

    Bridges :class:`thegent.governance.policy_engine.PolicyDecision` into the
    cockpit UX so verdicts (allow / deny / warn), reason codes, and the
    matched ``rule_id`` are visible inline as the runtime produces them.

    Attributes:
        verdict: One of ``"allow"``, ``"deny"``, ``"warn"`` (matches
            ``thegent.governance.policy_engine.Verdict`` values).
        reason_code: Machine-readable reason code (``ReasonCode`` value).
        rule_id: Matched policy rule (or ``None`` when no rule matched).
        agent: Originating agent name (truncated for display).
        lane: Originating lane (e.g. ``"critical"``).
        evaluated_at: Unix timestamp of decision; used for stale-decay.
        reason: Free-form human-readable reason string.
    """

    verdict: str
    reason_code: str
    rule_id: str | None
    agent: str = ""
    lane: str = "standard"
    evaluated_at: float = 0.0
    reason: str = ""

    def is_deny(self) -> bool:
        """Whether the decision blocked the request."""
        return self.verdict == "deny"

    def is_warn(self) -> bool:
        """Whether the decision emitted a warning (admissible but flagged)."""
        return self.verdict == "warn"


# ---------------------------------------------------------------------------
# Internal state containers
# ---------------------------------------------------------------------------


@dataclass
class _CockpitState:
    """Mutable internal state of the cockpit (single source of truth).

    ``confidence_history`` and ``override_notices`` are bounded ``deque``
    collections to prevent unbounded memory growth across a long-running
    operator session.
    """

    last_tick_at: float = 0.0
    runs: dict[str, RunEvent] = field(default_factory=dict)
    overrides: dict[str, OverrideEvent] = field(default_factory=dict)
    confidence_history: deque[float] = field(default_factory=lambda: deque(maxlen=1024))
    override_notices: deque[OverrideExpiryNotice] = field(default_factory=lambda: deque(maxlen=32))
    decision_notices: deque[DecisionNotice] = field(
        default_factory=lambda: deque(maxlen=MAX_DECISION_NOTICES),
    )
    last_progress: tuple[int, int] = (0, 0)  # (done, total)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _progress_bar(done: int, total: int, *, width: int = 24) -> str:
    """Return a textual progress bar ``[####------]  42%``.

    Used by the cockpit header (P-081, FR-UX-007) to surface run progress.
    Width and percent are emitted in a single round-trip-safe string.
    """
    if total <= 0:
        return "[" + " " * width + "]   -"
    pct = max(0, min(100, int(100 * done / total)))
    filled = int(width * pct / 100)
    return f"[{'#' * filled}{'-' * (width - filled)}] {pct:3d}%"


def _sparkline(values: Sequence[float], width: int) -> str:
    """Return a unicode sparkline representation.

    Maps a sequence of values to the eight ``SPARKLINE_CHARS`` characters.
    Empty input or all-equal values produce a flat line — never raises.
    """
    if not values:
        return "·" * width
    if width <= 0:
        return ""
    # Coerce to a windowed view
    windowed = list(values[-width:])
    if len(windowed) < width:
        windowed = ([0.0] * (width - len(windowed))) + windowed
    lo, hi = min(windowed), max(windowed)
    if hi - lo < 1e-9:
        return "·" * width
    out = []
    for v in windowed:
        idx = int((v - lo) / (hi - lo) * (len(SPARKLINE_CHARS) - 1))
        out.append(SPARKLINE_CHARS[idx])
    return "".join(out)


def _truncate(text: str, limit: int) -> str:
    """Truncate ``text`` to ``limit`` chars, appending an ellipsis when needed.

    A non-positive ``limit`` returns the empty string.
    """
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    if limit == 1:
        return text[:1]
    return text[: limit - 1] + "…"


def _format_run_row(ev: RunEvent) -> str:
    """Format a single run as a cockpit row."""
    state_glyph = {
        RunState.QUEUED: "·",
        RunState.ACTIVE: "▶",
        RunState.PAUSED: "⏸",
        RunState.DONE: "✓",
        RunState.ERROR: "✗",
    }.get(ev.state, "?")
    conf_str = f"{ev.confidence:.2f}" if ev.confidence is not None else "  - "
    return f"{state_glyph} {ev.run_id:<10}  {ev.lane:<9}  {ev.agent:<10}  c={conf_str}  {ev.elapsed_s:5.1f}s"


def _format_override_row(ev: OverrideEvent) -> str:
    """Format a single override row with TTL countdown."""
    return f"! {ev.rule_id:<22}  by {ev.by:<8}  ⏳ {ev.expires_in_s:5.0f}s  {_truncate(ev.reason, 32)}"


# ---------------------------------------------------------------------------
# Main cockpit class
# ---------------------------------------------------------------------------


class OperatorCockpit:
    """The 4-pane operator cockpit.

    Usage::

        cockpit = OperatorCockpit(config=CockpitConfig())
        cockpit.tick(runs=[RunEvent(...)], overrides=[OverrideEvent(...)])
        print(cockpit.render())
    """

    def __init__(
        self,
        config: CockpitConfig | None = None,
        *,
        clock: Callable[[], float] | None = None,
        audit_appender: "DecisionAuditAppender | None" = None,
        auto_tail: bool = False,
        tail_interval_s: float = 1.0,
    ) -> None:
        """Build the operator cockpit.

        Args:
            config: Optional :class:`CockpitConfig`; defaults to a fresh config.
            clock: Injectable wall-clock. Default ``time.time``. Useful for
                deterministic audit replays.
            audit_appender: Optional :class:`DecisionAuditAppender`. When
                provided *and* ``auto_tail`` is ``True``, the cockpit spins
                up a :class:`DecisionAuditTailer` so every
                :meth:`record_decision` call lands in the JSONL audit log
                without manual wiring. Production deployments should pass
                their own appender (so audit-path / cache / clock are
                controlled at boot); tests can pass an appender with a
                tmp_path and ``auto_tail=False`` for synchronous drains.
            auto_tail: Start a background :class:`DecisionAuditTailer`
                against ``audit_appender``. Ignored when no appender is
                supplied. Default ``False`` keeps the cockpit free of
                background threads in tests and short-lived scripts.
            tail_interval_s: Drain cadence for the background tailer.
                Same default as :data:`DEFAULT_TAIL_INTERVAL_S`.

        The cockpit owns the tailer for the lifetime of the instance; it
        is stopped on :meth:`shutdown` (and on garbage collection as a
        safety net so test sessions don't leak threads).
        """
        self.config = config or CockpitConfig()
        self._state = _CockpitState()
        # counters
        self._frame_count = 0
        self._last_render_ms = 0.0
        # State mutators (tick/reset) run concurrently with readers (render/
        # snapshot); serialise with an RLock so render can re-enter safely.
        self._lock = threading.RLock()
        # Clock function used for tick timestamps, banner age, render-time
        # metrics. Injected for deterministic audit replays; defaults to
        # ``time.time``. Monotonicity is the caller's responsibility.
        self._clock: Callable[[], float] = clock or _DEFAULT_CLOCK

        # Optional JSONL audit wiring. The appender is owned by the
        # caller (so multi-cockpit deployments can share one file
        # handle); the tailer is owned by the cockpit so the lifetime
        # matches the cockpit.
        self._audit_appender = audit_appender
        self._audit_tailer: "DecisionAuditTailer | None" = None
        self._tail_interval_s = float(tail_interval_s)
        if audit_appender is not None and auto_tail:
            self._start_audit_tailer()

        # Track whether ``shutdown`` was explicitly invoked so the
        # finaliser doesn't double-stop the tailer in production.
        self._shutdown_called = False
        weakref.finalize(self, _finalize_cockpit, self)

    # ------------------------------------------------------------- audit wiring

    def _start_audit_tailer(self) -> None:
        """Idempotently start the JSONL audit tailer, if configured.

        A no-op when ``audit_appender`` was not supplied at construction.
        Re-entrant (e.g. after a manual stop) — restarts a fresh thread.
        """
        if self._audit_appender is None:
            return
        from .decision_audit import DecisionAuditTailer  # local import to avoid cycle

        tailer = DecisionAuditTailer(
            cockpit=self,
            appender=self._audit_appender,
            interval_s=self._tail_interval_s,
        )
        tailer.start()
        self._audit_tailer = tailer

    def audit_appender(self) -> "DecisionAuditAppender | None":
        """Return the JSONL audit appender the cockpit is wired to (or ``None``)."""
        return self._audit_appender

    def shutdown(self, timeout_s: float = 5.0) -> None:
        """Stop the background audit tailer (idempotent, safe to call twice).

        Production deployments should invoke this on graceful shutdown so
        the daemon :class:`DecisionAuditTailer` thread exits cleanly and
        no notices are lost mid-drain. Tests can lean on the finaliser
        registered in ``__init__``.
        """
        self._shutdown_called = True
        tailer = self._audit_tailer
        if tailer is not None:
            tailer.stop(timeout_s=timeout_s)
            self._audit_tailer = None

    # --------------------------------------------------------------- mutators

    def tick(
        self,
        *,
        runs: Iterable[RunEvent] | None = None,
        overrides: Iterable[OverrideEvent] | None = None,
        progress: tuple[int, int] | None = None,
    ) -> None:
        """Apply one ``DAG_TICK`` worth of events.

        ``runs``: full replacement set of current runs (idempotent per ``run_id``).
        ``overrides``: full replacement set of active overrides (idempotent).
        ``progress``: ``(done, total)`` for the header progress bar.
        """
        now = self._clock()
        with self._lock:
            self._state.last_tick_at = now
            if runs is not None:
                self._state.runs = {ev.run_id: ev for ev in runs}
            if overrides is not None:
                self._state.overrides = {ev.rule_id: ev for ev in overrides}
            if progress is not None:
                self._state.last_progress = progress
            # Update confidence sparkline history with newest run confidence.
            # The deque is bounded (maxlen=1024) so this cannot grow unbounded.
            for ev in self._state.runs.values():
                if ev.confidence is not None and -1e-6 <= ev.confidence <= 1.0 + 1e-6:
                    self._state.confidence_history.append(ev.confidence)

    def reset(self) -> None:
        """Reset cockpit state (used between sessions / tests)."""
        with self._lock:
            self._state = _CockpitState()
            self._frame_count = 0
            self._last_render_ms = 0.0

    def record_override_event(self, notice: OverrideExpiryNotice) -> None:
        """Push a most-recent override-expiry notice into the cockpit.

        Designed to be called from an :class:`OverrideExpiryMonitor`
        callback (WP-3003) so the operator sees expiry events inline in
        the cockpit header as soon as they fire.

        The notice deque is bounded (``maxlen=32``); the oldest notice is
        silently dropped once full. ``age_s`` is recomputed against the
        current wall clock on every render so the banner naturally
        fades.
        """
        if not isinstance(notice, OverrideExpiryNotice):  # defensive — surface config drift
            raise TypeError(f"record_override_event expects OverrideExpiryNotice, got {type(notice).__name__}")
        with self._lock:
            self._state.override_notices.append(notice)

    def record_decision(self, notice: DecisionNotice) -> None:
        """Push a governance-decision notice into the cockpit (WP-3001 -> WP-4001).

        Surfaces :class:`thegent.governance.policy_engine.PolicyDecision`
        payloads inline so operators can see verdicts / reason codes
        appear as the runtime produces them. ``deny`` verdicts are
        rendered as a focused banner (similar to override expiry); all
        other verdicts accumulate into a bounded ``decision_notices``
        deque and can be read out via :meth:`snapshot` for downstream
        consumers (CI hooks, log shippers).

        The deque is bounded (``maxlen=64``) so a long-lived operator
        session cannot grow unbounded. ``evaluated_at == 0`` is filled
        with the cockpit's clock for ergonomic zero-init.
        """
        if not isinstance(notice, DecisionNotice):
            raise TypeError(f"record_decision expects DecisionNotice, got {type(notice).__name__}")
        with self._lock:
            payload = notice
            if payload.evaluated_at <= 0.0:
                payload = DecisionNotice(
                    verdict=payload.verdict,
                    reason_code=payload.reason_code,
                    rule_id=payload.rule_id,
                    agent=payload.agent,
                    lane=payload.lane,
                    evaluated_at=self._clock(),
                    reason=payload.reason,
                )
            self._state.decision_notices.append(payload)

    # -------------------------------------------------------------- snapshots

    def snapshot(self) -> dict[str, Any]:
        """Return a structured snapshot for downstream consumers (logs, JSON).

        Frontends that want plain text should use :meth:`render` instead.
        The snapshot is a consistent point-in-time copy under the cockpit's
        internal lock to avoid torn reads.
        """
        with self._lock:
            now = self._clock()
            runs = list(self._state.runs.values())
            overrides = list(self._state.overrides.values())
            lanes = Counter(ev.lane for ev in runs)
            return {
                "title": self.config.title,
                "tick_at": self._state.last_tick_at,
                "frame_count": self._frame_count,
                "runs": [
                    {
                        "run_id": r.run_id,
                        "state": r.state.value,
                        "lane": r.lane,
                        "agent": r.agent,
                        "confidence": r.confidence,
                        "elapsed_s": r.elapsed_s,
                        "note": r.note,
                    }
                    for r in runs
                ],
                "lanes": dict(lanes),
                "overrides": [
                    {
                        "rule_id": o.rule_id,
                        "by": o.by,
                        "reason": o.reason,
                        "expires_in_s": o.expires_in_s,
                        "metadata": dict(o.metadata),
                    }
                    for o in overrides
                ],
                "progress": self._state.last_progress,
                "confidence_history": list(self._state.confidence_history),
                "override_notices": [
                    {
                        "rule_id": n.rule_id,
                        "owner": n.owner,
                        "reason": n.reason,
                        "expired_at": n.expired_at,
                        "age_s": max(0.0, now - n.expired_at),
                    }
                    for n in self._state.override_notices
                ],
                "decision_notices": [
                    {
                        "verdict": d.verdict,
                        "reason_code": d.reason_code,
                        "rule_id": d.rule_id,
                        "agent": d.agent,
                        "lane": d.lane,
                        "evaluated_at": d.evaluated_at,
                        "age_s": max(0.0, now - d.evaluated_at) if d.evaluated_at > 0 else 0.0,
                        "reason": d.reason,
                    }
                    for d in self._state.decision_notices
                ],
                "last_render_ms": self._last_render_ms,
            }

    def progress_bar(self) -> str:
        """Return the current progress bar (``P-081``)."""
        done, total = self._state.last_progress
        return _progress_bar(done, total)

    def last_render_ms(self) -> float:
        """How long the most recent ``render()`` call took, in milliseconds."""
        return self._last_render_ms

    # ----------------------------------------------------------------- render

    def render(self) -> str:
        """Render the cockpit into a single string (the current frame).

        The render is plain ASCII/Unicode, with one pane per line, four panes
        laid out as a 2x2 grid.  Returns ``""`` if the cockpit is empty.
        """
        t0 = self._clock()
        try:
            text = self._render_grid()
        finally:
            dt = (self._clock() - t0) * 1000.0
            self._last_render_ms = dt
            self._frame_count += 1
        return text

    def _render_grid(self) -> str:
        cfg = self.config
        # 1. Header — title + progress bar (P-081)
        header = self._render_header()

        # 2. Optional override-expiry banner (WP-3003 -> WP-4001 bridge).
        #    Surfaces the most recent governance.override.expired events
        #    inline so operators see TTL expirations as they fire rather
        #    than waiting for the next JSONL tail.
        banner = self._render_override_banner()

        # 3. The four panes
        runs_lines = self._render_runs_pane()
        lanes_lines = self._render_lanes_pane()
        conf_lines = self._render_confidence_pane()
        ovr_lines = self._render_overrides_pane()

        # 4. Compose into 2x2 grid
        body_lines: list[str] = []
        for i in range(max(len(runs_lines), len(lanes_lines))):
            left = runs_lines[i] if i < len(runs_lines) else ""
            right = lanes_lines[i] if i < len(lanes_lines) else ""
            body_lines.append(f"{left:<46}│ {right}")
        for i in range(max(len(conf_lines), len(ovr_lines))):
            left = conf_lines[i] if i < len(conf_lines) else ""
            right = ovr_lines[i] if i < len(ovr_lines) else ""
            body_lines.append(f"{left:<46}│ {right}")
        # 5. Third row: decision-history pane (full-width). Mirrors the
        #    existing override-history UX (different stream): every
        #    recorded ``DecisionNotice`` shows up with verdict glyph +
        #    age so operators can trace governance denies without
        #    tailing the JSONL.
        decisions_lines = self._render_decisions_pane()
        body = "\n".join(body_lines) + "\n" + "\n".join(decisions_lines)

        if banner:
            return f"{header}\n{banner}\n{body}"
        return f"{header}\n{body}"

    def _render_override_banner(self) -> str:
        """Render an inline banner for the freshest operationally-relevant event.

        Walks both :attr:`_CockpitState.override_notices` and
        :attr:`_CockpitState.decision_notices` for any event whose age is
        within ``OVERRIDE_BANNER_MAX_AGE_S``, then picks the freshest.
        Returns ``""`` when nothing qualifies so the banner naturally
        fades between DAG ticks.
        """
        now = self._clock()
        with self._lock:
            last_override: OverrideExpiryNotice | None = (
                self._state.override_notices[-1] if self._state.override_notices else None
            )
            last_deny: DecisionNotice | None = None
            for n in reversed(self._state.decision_notices):
                if n.is_deny():
                    last_deny = n
                    break
        candidates: list[tuple[float, str]] = []
        if last_override is not None:
            o_age = max(0.0, now - last_override.expired_at)
            if o_age <= OVERRIDE_BANNER_MAX_AGE_S:
                candidates.append((o_age, "override"))
        if last_deny is not None and last_deny.evaluated_at > 0:
            d_age = max(0.0, now - last_deny.evaluated_at)
            if d_age <= OVERRIDE_BANNER_MAX_AGE_S:
                candidates.append((d_age, "deny"))
        if not candidates:
            return ""
        # Freshest wins.
        candidates.sort(key=lambda item: item[0])
        kind = candidates[0][1]
        if kind == "override":
            return _render_override_banner_text(last_override, now)
        return _render_decision_deny_banner(last_deny, now)  # type: ignore[arg-type]

    def _render_header(self) -> str:
        cfg = self.config
        done, total = self._state.last_progress
        bar = _progress_bar(done, total)
        ts = time.strftime("%H:%M:%S", time.localtime(self._state.last_tick_at))
        return f"  {cfg.title}   {cfg.progress_label}: {bar}   tick={ts} (#{self._frame_count + 1})"

    def _render_runs_pane(self) -> list[str]:
        cfg = self.config
        lines = [f"┌─ {cfg.pane_labels[CockpitPane.RUNS]} ───────────────┐"]
        runs = sorted(
            self._state.runs.values(),
            key=lambda ev: (ev.state.value, ev.run_id),
        )
        if not runs:
            lines.append("│  (no active runs)                    │")
            lines.append("│                                      │")
        else:
            for ev in runs[:MAX_RUNS_PANE_ROWS]:
                lines.append(f"│ {_format_run_row(ev):<38} │")
            if len(runs) > MAX_RUNS_PANE_ROWS:
                lines.append(f"│  … {len(runs) - MAX_RUNS_PANE_ROWS} more            │")
        lines.append("└──────────────────────────────────────┘")
        return lines

    def _render_lanes_pane(self) -> list[str]:
        cfg = self.config
        lines = [f"┌─ {cfg.pane_labels[CockpitPane.LANES]} ───────────────┐"]
        runs = list(self._state.runs.values())
        if not runs:
            lines.append("│  (idle)                              │")
            lines.append("│                                      │")
        else:
            counts = Counter(ev.lane for ev in runs)
            for lane, count in sorted(counts.items()):
                bar = _progress_bar(count, max(counts.values()), width=12)
                lines.append(f"│  {lane:<10} {count:3d}  {bar:<18} │")
        lines.append("└──────────────────────────────────────┘")
        return lines

    def _render_confidence_pane(self) -> list[str]:
        cfg = self.config
        # ``confidence_history`` is a bounded ``deque`` to prevent unbounded
        # memory growth. Materialise once into a plain list so the helpers
        # below can slice/index it without relying on ``collections.deque``
        # slice semantics (which Python 3.14 + abstract ``Sequence[float]``
        # typing can refuse at runtime).
        history: list[float] = list(self._state.confidence_history)
        p50 = self._percentile(history, 0.5)
        p95 = self._percentile(history, 0.95)
        lines = [f"┌─ {cfg.pane_labels[CockpitPane.CONFIDENCE]} ─┐"]
        lines.append(f"│ P50={p50:.2f}   P95={p95:.2f}   n={len(history):3d}     │")
        if cfg.show_sparkline:
            spark = _sparkline(history, cfg.sparkline_width)
            lines.append(f"│ {spark:<36} │")
        else:
            lines.append("│                                      │")
            lines.append("│                                      │")
        # Pad to same height as lanes pane
        while len(lines) < 4:
            lines.append("│                                      │")
        lines.append("└──────────────────────────────────────┘")
        return lines

    def _render_overrides_pane(self) -> list[str]:
        cfg = self.config
        lines = [f"┌─ {cfg.pane_labels[CockpitPane.OVERRIDES]} ───────────┐"]
        ovrs = sorted(
            self._state.overrides.values(),
            key=lambda ev: ev.expires_in_s,
        )
        if not ovrs:
            lines.append("│  (no active overrides)               │")
            lines.append("│                                      │")
        else:
            for ev in ovrs[:MAX_OVERRIDE_PANE_ROWS]:
                lines.append(f"│ {_format_override_row(ev):<38} │")
            if len(ovrs) > MAX_OVERRIDE_PANE_ROWS:
                lines.append(f"│  … {len(ovrs) - MAX_OVERRIDE_PANE_ROWS} more            │")
        lines.append("└──────────────────────────────────────┘")
        return lines

    def _render_decisions_pane(self) -> list[str]:
        """Render the decision-history stream (WP-3001 -> WP-4001 inline view).

        Full-width row sitting under the 2x2 grid. Shows the most recent
        :class:`DecisionNotice` events with verdict glyph, rule_id (12),
        agent (8), lane (8), and age (4s). Mirrors the existing
        override-banner UX so operators learn one pattern. Bounded by
        ``MAX_DECISION_NOTICES`` (deque maxlen, ``cockpit.py:67``) so long sessions
        can't blow up the renderer's memory.

        Empty panes render a single neutral line so the cockpit always
        reserves the row and operators can tell the audit pipeline is
        idle at a glance.
        """
        with self._lock:
            decisions: list[DecisionNotice] = list(self._state.decision_notices)
        lines: list[str] = ["┌─ Decision History ──────────────────────────────┐"]
        if not decisions:
            lines.append("│  (no policy decisions recorded yet)            │")
            lines.append("│                                                 │")
        else:
            now = self._clock()
            newest = list(reversed(decisions[-MAX_DECISION_PANE_ROWS:]))
            for d in newest:
                glyph = _decision_glyph(d)
                age = max(0.0, now - d.evaluated_at) if d.evaluated_at > 0 else 0.0
                lines.append(f"│ {glyph} {_format_decision_row(d, age):<47} │")
            total = len(decisions)
            if total > MAX_DECISION_PANE_ROWS:
                lines.append(f"│  … {total - MAX_DECISION_PANE_ROWS} older decisions hidden       │")
        lines.append("└─────────────────────────────────────────────────┘")
        return lines

    @staticmethod
    def _percentile(values: Sequence[float], pct: float) -> float:
        """Return the ``pct`` percentile of ``values`` (0..1).

        Returns ``0.0`` for empty input.
        """
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = max(0, min(len(sorted_vals) - 1, int(pct * (len(sorted_vals) - 1))))
        return sorted_vals[idx]

    # --------------------------------------------------- context-manager sugar

    def __enter__(self) -> "OperatorCockpit":
        return self

    def __exit__(self, *exc: Any) -> None:
        # Best-effort stop of the background tailer (if any) so the
        # daemon thread exits cleanly when used as ``with OperatorCockpit(...)``.
        self.shutdown(timeout_s=0.1)


# ---------------------------------------------------------------------------
# Module-level helpers (lifecycle)
# ---------------------------------------------------------------------------


def _finalize_cockpit(cockpit: "OperatorCockpit") -> None:
    """Finaliser that stops the audit tailer at garbage-collection time.

    Registered via :func:`weakref.finalize` so that test suites and
    short-lived scripts that forget to call :meth:`OperatorCockpit.shutdown`
    still exit their daemon threads and don't leave the JSONL file half
    written. Idempotent with explicit ``shutdown()`` because the tailer
    keeps its own state.
    """
    try:
        tailer = cockpit._audit_tailer  # noqa: SLF001 — finaliser contract
    except AttributeError:
        return
    if tailer is not None:
        try:
            tailer.stop(timeout_s=0.5)
        except Exception:  # noqa: BLE001 — finaliser must never raise
            pass
        cockpit._audit_tailer = None  # noqa: SLF001


# ---------------------------------------------------------------------------
# One-shot helper
# ---------------------------------------------------------------------------


def render_cockpit(
    runs: Iterable[RunEvent] | None = None,
    overrides: Iterable[OverrideEvent] | None = None,
    *,
    progress: tuple[int, int] | None = None,
    config: CockpitConfig | None = None,
    clock: Callable[[], float] | None = None,
) -> str:
    """One-shot convenience renderer.

    Equivalent to building an ``OperatorCockpit``, calling ``tick(...)`` once,
    and returning ``render()``. ``clock`` lets callers pin the wall clock for
    deterministic audit replays.
    """
    cockpit = OperatorCockpit(config=config, clock=clock)
    cockpit.tick(runs=runs, overrides=overrides, progress=progress)
    return cockpit.render()


# ---------------------------------------------------------------------------
# Internal banner helpers (extracted so audit replays are byte-identical)
# ---------------------------------------------------------------------------


def _render_override_banner_text(notice: OverrideExpiryNotice, now: float) -> str:
    """Format the override-expiry banner line; deterministic given (notice, now)."""
    age = max(0.0, now - notice.expired_at)
    reason = notice.reason or "ttl_elapsed"
    glyph = "✓" if age < 1.0 else "!"
    # Fixed-width columns: rule_id (12), owner (8), age (4), reason (32).
    return (
        f"  {glyph} override expired: "
        f"{_truncate(notice.rule_id, 12):<12}  "
        f"by {_truncate(notice.owner, 8):<8}  "
        f"{age:4.0f}s ago  "
        f"{_truncate(reason, 32)}"
    )


def _render_decision_deny_banner(notice: DecisionNotice, now: float) -> str:
    """Render a single-line banner highlighting a recent policy deny.

    The rule_id is shown first so it survives Rich's default console
    width truncation on operators' terminals — operators triaging a deny
    always have the offending rule in view, even on 80-col consoles.
    """
    age = max(0.0, now - notice.evaluated_at)
    age_text = f"{age:.0f}s"
    head = f"\u2717 policy deny: {notice.rule_id}"
    if notice.lane:
        head = f"{head}  lane={notice.lane}"
    head = f"{head}  {age_text} ago"
    if notice.reason_code:
        head = f"{head}  ({notice.reason_code})"
    if notice.reason:
        head = f"{head}  {notice.reason}"
    return head


def _decision_glyph(notice: DecisionNotice) -> str:
    """Glyph used in the decision-history pane for a given verdict.

    Same vocabulary as the deny banner (``\u2717`` = ballot-x) so the
    pane and the banner read identically. ``allow`` gets a check mark;
    ``warn`` gets a bang. ``evaluated_at == 0`` (no clock yet) is
    represented as a dash to avoid displaying nonsense ages.
    """
    if notice.is_deny():
        return "\u2717"
    if notice.is_warn():
        return "!"
    if notice.evaluated_at <= 0:
        return "-"
    return "\u2713"


def _format_decision_row(notice: DecisionNotice, age: float) -> str:
    """Format one row of the decision-history pane.

    Columns (fixed-width):
        rule_id (12) | agent (8) | lane (8) | age (4s) | reason_code
    The reason is omitted to keep the row readable on 80-col consoles;
    operators wanting the full message read the JSONL audit log via
    ``thegent cockpit audit tail``.
    """
    age_text = f"{age:.0f}s" if notice.evaluated_at > 0 else "   -"
    rule = _truncate(notice.rule_id or "-", 12)
    agent = _truncate(notice.agent or "-", 8)
    lane = _truncate(notice.lane or "-", 8)
    code = notice.reason_code or ""
    code = _truncate(code, 16)
    return f"{rule:<12}  {agent:<8}  {lane:<8}  {age_text:>4}  {code}"


__all__ = [
    "CockpitConfig",
    "CockpitPane",
    "DecisionNotice",
    "OperatorCockpit",
    "OverrideEvent",
    "OverrideExpiryNotice",
    "RunEvent",
    "RunState",
    "render_cockpit",
]
