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
import time
from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DEFAULT_DAG_TICK_MS = 1000
MAX_RUNS_PANE_ROWS = 14
MAX_OVERRIDE_PANE_ROWS = 6
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"


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


# ---------------------------------------------------------------------------
# Internal state containers
# ---------------------------------------------------------------------------


@dataclass
class _CockpitState:
    """Mutable internal state of the cockpit (single source of truth)."""

    last_tick_at: float = 0.0
    runs: dict[str, RunEvent] = field(default_factory=dict)
    overrides: dict[str, OverrideEvent] = field(default_factory=dict)
    confidence_history: list[float] = field(default_factory=list)
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
    """Truncate ``text`` to ``limit`` chars, appending an ellipsis when needed."""
    if len(text) <= limit:
        return text
    if limit <= 1:
        return text[:limit]
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
        self._state.last_tick_at = now

        if runs is not None:
            self._state.runs = {ev.run_id: ev for ev in runs}

        if overrides is not None:
            self._state.overrides = {ev.rule_id: ev for ev in overrides}

        if progress is not None:
            self._state.last_progress = progress

        # Update confidence sparkline history with newest run confidence (if any).
        for ev in self._state.runs.values():
            if ev.confidence is not None:
                self._state.confidence_history.append(ev.confidence)

    def reset(self) -> None:
        """Reset cockpit state (used between sessions / tests)."""
        self._state = _CockpitState()
        self._frame_count = 0
        self._last_render_ms = 0.0

    # -------------------------------------------------------------- snapshots

    def snapshot(self) -> dict[str, Any]:
        """Return a structured snapshot for downstream consumers (logs, JSON).

        Frontends that want plain text should use :meth:`render` instead.
        """
        runs = list(self._state.runs.values())
        overrides = list(self._state.overrides.values())
        lanes = Counter(ev.lane for ev in runs)
        return {
            "title": self.config.title,
            "tick_at": self._state.last_tick_at,
            "frame_count": self._frame_count,
            "runs": [r.__dict__ | {"state": r.state.value} for r in runs],
            "lanes": dict(lanes),
            "overrides": [o.__dict__ | {"metadata": dict(o.metadata)} for o in overrides],
            "progress": self._state.last_progress,
            "confidence_history": list(self._state.confidence_history),
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

        # 2. The four panes
        runs_lines = self._render_runs_pane()
        lanes_lines = self._render_lanes_pane()
        conf_lines = self._render_confidence_pane()
        ovr_lines = self._render_overrides_pane()

        # 3. Compose into 2x2 grid
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

        return f"{header}\n{body}"

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
        history = self._state.confidence_history
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
    "RunEvent",
    "RunState",
    "render_cockpit",
]
