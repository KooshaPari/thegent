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
from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
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
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"
# How long an OverrideExpiryNotice stays visible in the inline banner
# before fading out. 30s matches the cockpit tick cadence and gives the
# operator enough time to glance up between DAG ticks.
OVERRIDE_BANNER_MAX_AGE_S = 30.0


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
    override_notices: deque[OverrideExpiryNotice] = field(
        default_factory=lambda: deque(maxlen=32)
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

    def __init__(self, config: CockpitConfig | None = None) -> None:
        self.config = config or CockpitConfig()
        self._state = _CockpitState()
        # counters
        self._frame_count = 0
        self._last_render_ms = 0.0
        # State mutators (tick/reset) run concurrently with readers (render/
        # snapshot); serialise with an RLock so render can re-enter safely.
        self._lock = threading.RLock()

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
        now = time.time()
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
            raise TypeError(
                f"record_override_event expects OverrideExpiryNotice, got "
                f"{type(notice).__name__}"
            )
        with self._lock:
            self._state.override_notices.append(notice)

    # -------------------------------------------------------------- snapshots

    def snapshot(self) -> dict[str, Any]:
        """Return a structured snapshot for downstream consumers (logs, JSON).

        Frontends that want plain text should use :meth:`render` instead.
        The snapshot is a consistent point-in-time copy under the cockpit's
        internal lock to avoid torn reads.
        """
        with self._lock:
            runs = list(self._state.runs.values())
            overrides = list(self._state.overrides.values())
            lanes = Counter(ev.lane for ev in runs)
            return {
                "title": self.config.title,
                "tick_at": self._state.last_tick_at,
                "frame_count": self._frame_count,
                "runs": [{"run_id": r.run_id, "state": r.state.value,
                         "lane": r.lane, "agent": r.agent,
                         "confidence": r.confidence, "elapsed_s": r.elapsed_s,
                         "note": r.note} for r in runs],
                "lanes": dict(lanes),
                "overrides": [{"rule_id": o.rule_id, "by": o.by,
                              "reason": o.reason, "expires_in_s": o.expires_in_s,
                              "metadata": dict(o.metadata)} for o in overrides],
                "progress": self._state.last_progress,
                "confidence_history": list(self._state.confidence_history),
                "override_notices": [
                    {"rule_id": n.rule_id, "owner": n.owner,
                     "reason": n.reason, "expired_at": n.expired_at,
                     "age_s": max(0.0, time.time() - n.expired_at)}
                    for n in self._state.override_notices
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
        t0 = time.time()
        try:
            text = self._render_grid()
        finally:
            dt = (time.time() - t0) * 1000.0
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
        body = "\n".join(body_lines)

        if banner:
            return f"{header}\n{banner}\n{body}"
        return f"{header}\n{body}"

    def _render_override_banner(self) -> str:
        """Render an inline banner for the most-recent override-expiry event.

        Reads the most recent :class:`OverrideExpiryNotice` from the bounded
        notice deque under the cockpit lock, recomputes its ``age_s`` against
        the wall clock, and returns a single-line banner. Returns ``""``
        when there are no notices or the most recent one has aged past
        ``OVERRIDE_BANNER_MAX_AGE_S`` (so the banner naturally fades).
        """
        now = time.time()
        with self._lock:
            if not self._state.override_notices:
                return ""
            notice = self._state.override_notices[-1]
        age = max(0.0, now - notice.expired_at)
        if age > OVERRIDE_BANNER_MAX_AGE_S:
            return ""
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
        # No resources to release; defined so callers can use ``with``.
        return None


# ---------------------------------------------------------------------------
# One-shot helper
# ---------------------------------------------------------------------------


def render_cockpit(
    runs: Iterable[RunEvent] | None = None,
    overrides: Iterable[OverrideEvent] | None = None,
    *,
    progress: tuple[int, int] | None = None,
    config: CockpitConfig | None = None,
) -> str:
    """One-shot convenience renderer.

    Equivalent to building an ``OperatorCockpit``, calling ``tick(...)`` once,
    and returning ``render()``.
    """
    cockpit = OperatorCockpit(config=config)
    cockpit.tick(runs=runs, overrides=overrides, progress=progress)
    return cockpit.render()


__all__ = [
    "CockpitConfig",
    "CockpitPane",
    "OperatorCockpit",
    "OverrideEvent",
    "OverrideExpiryNotice",
    "RunEvent",
    "RunState",
    "render_cockpit",
]
