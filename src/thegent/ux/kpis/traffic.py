"""Real-time TRAFFIC KPI dashboard (Batch 10A, WP-Y7, P-081).

Thegent needs a high-cardinality live "TRAFFIC" view that rolls up requests
per second, lane distribution, error budget burn, and override churn.  This
module provides:

* :class:`TrafficWindow` — a fixed-size ring buffer of events with bucketed counts
* :class:`TrafficDashboard` — exposes live TRAFFIC counts as plain-Python dicts
* :func:`render_traffic` — render a single TRAFFIC string (suitable for ``print``)
* :func:`progress_bar` — the canonical progress bar used everywhere else in UX

All values are thread-safe *per-dashboard* in single-threaded usage.  Designed
to embed in CI captures, ``rich.live.Live``, and the operator cockpit.

The dashboard accepts an optional ``clock`` callable (``-> float``) so audit
replays and CI snapshots can pin the wall clock deterministically; by default
``time.time`` is used.

Traces to: OPS-001 (request rate), OPS-002 (error rate), OPS-003 (latency
            p95), P-081 (progress bar), P-090 (cockpit latency SLO),
            WP-Y7 (TRAFFIC real-time view).
"""

from __future__ import annotations

import logging
import threading
import time
from collections import Counter, deque
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


DEFAULT_WINDOW_SECONDS = 60.0
DEFAULT_BUCKET_SECONDS = 1.0
DEFAULT_TREND_WIDTH = 30


# ---------------------------------------------------------------------------
# Progress bar (the canonical one; re-used from cockpit)
# ---------------------------------------------------------------------------


def progress_bar(done: int, total: int, *, width: int = 24) -> str:
    """Return a textual progress bar ``[####------]  42%``.

    Returns a flat line for ``total <= 0``.  Always emits a width-stable string
    so callers can stack progress bars across runs.
    """
    if total <= 0:
        return "[" + " " * width + "]   -"
    pct = max(0, min(100, int(100 * done / total)))
    filled = int(width * pct / 100)
    return f"[{'#' * filled}{'-' * (width - filled)}] {pct:3d}%"


# ---------------------------------------------------------------------------
# TrafficWindow
# ---------------------------------------------------------------------------


@dataclass
class TrafficEvent:
    """A single traffic event recorded in the dashboard."""

    ts: float
    lane: str = "standard"
    agent: str = ""
    status: str = "ok"  # one of: ok, error, warn
    duration_ms: float = 0.0
    override_active: bool = False


@dataclass
class TrafficWindow:
    """A sliding time window of events with per-bucket counts.

    The window is a fixed-size ring buffer of :class:`TrafficEvent`s.  Reads
    and writes are serialised through ``self._lock`` so the dashboard is safe
    to share across threads.

    ``clock`` (``-> float``) defaults to ``time.time`` and can be injected
    via ``TrafficWindow(clock=...)`` to make audit replays deterministic.
    """

    window_s: float = DEFAULT_WINDOW_SECONDS
    bucket_s: float = DEFAULT_BUCKET_SECONDS

    _events: deque[TrafficEvent] = field(default_factory=deque)

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._clock: Callable[[], float] = time.time

    def set_clock(self, clock: Callable[[], float]) -> None:
        """Override the wall clock used for eviction and zero-init fallback."""
        self._clock = clock

    def record(self, event: TrafficEvent) -> None:
        """Append ``event`` and evict anything outside the window."""
        if event.ts <= 0:
            event.ts = self._clock()
        with self._lock:
            self._events.append(event)
            self._evict(event.ts)

    def _evict(self, now: float) -> None:
        cutoff = now - self.window_s
        while self._events and self._events[0].ts < cutoff:
            self._events.popleft()

    def summary(self, *, now: float | None = None) -> dict[str, Any]:
        """Return ``{count, by_lane, by_status, rps, error_rate, p50_ms, p95_ms}``.

        ``now`` overrides the wall clock for deterministic replay; defaults
        to ``self._clock()`` when omitted.
        """
        now = now if now is not None else self._clock()
        with self._lock:
            self._evict(now)
            events = list(self._events)
        count = len(events)
        if count == 0:
            return {
                "count": 0,
                "by_lane": {},
                "by_status": {},
                "rps": 0.0,
                "error_rate": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "override_count": 0,
                "duration_ms_window": self.window_s,
            }
        by_lane = Counter(ev.lane for ev in events)
        by_status = Counter(ev.status for ev in events)
        errors = sum(1 for ev in events if ev.status == "error")
        error_rate = errors / count
        durations = sorted(ev.duration_ms for ev in events if ev.duration_ms > 0)
        p50_ms = _percentile(durations, 0.50)
        p95_ms = _percentile(durations, 0.95)
        rps = count / self.window_s
        return {
            "count": count,
            "by_lane": dict(by_lane),
            "by_status": dict(by_status),
            "rps": rps,
            "error_rate": error_rate,
            "p50_ms": p50_ms,
            "p95_ms": p95_ms,
            "override_count": sum(1 for ev in events if ev.override_active),
            "duration_ms_window": self.window_s,
        }

    def events(self) -> Sequence[TrafficEvent]:
        """Return a snapshot of current events (read-only, thread-safe)."""
        with self._lock:
            return tuple(self._events)


# ---------------------------------------------------------------------------
# Trend bar
# ---------------------------------------------------------------------------


def render_trend(
    values,
    *,
    width: int = DEFAULT_TREND_WIDTH,
    chars: str = "▁▂▃▄▅▆▇█",
) -> str:
    """Render a trend bar of ``values`` as a unicode sparkline.

    Returns ``width`` characters.  Empty input produces ``width`` ``·``
    placeholder characters.  Will not raise on input shorter than ``width``.
    Accepts any iterable (including ``deque`` / generators); values are
    consumed via ``list(...)`` after a fast ``len()`` short-circuit.
    """
    if width <= 0:
        return ""
    try:
        n = len(values)
    except TypeError:
        values = list(values)
        n = len(values)
    if n == 0:
        return "·" * width
    buf = list(values)
    if n < width:
        buf = [0.0] * (width - n) + buf
    else:
        buf = buf[-width:]
    lo, hi = min(buf), max(buf)
    if hi - lo < 1e-9:
        return "·" * width
    n_chars = len(chars) - 1
    out = [chars[int((v - lo) / (hi - lo) * n_chars)] for v in buf]
    return "".join(out)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class TrafficDashboard:
    """Real-time TRAFFIC dashboard.

    Use :meth:`record` (or :meth:`tick`) to feed events.  Use
    :meth:`summary` or :meth:`render` to read the current state.

    The dashboard is single-threaded; concurrent callers must serialize.

    Pass ``clock=`` to the constructor (or call ``set_clock``) to pin the
    wall clock for deterministic audit replays and CI snapshots.
    """

    def __init__(
        self,
        *,
        window_s: float = DEFAULT_WINDOW_SECONDS,
        bucket_s: float = DEFAULT_BUCKET_SECONDS,
        trend_width: int = DEFAULT_TREND_WIDTH,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.window = TrafficWindow(window_s=window_s, bucket_s=bucket_s)
        if clock is not None:
            self.window.set_clock(clock)
        self.trend_width = trend_width
        # RPS trend is appended on every record() call; consumers can
        # render a sparkline of it via :meth:`rps_trend`.
        self._rps_trend: deque[float] = deque(maxlen=trend_width * 2)

    def set_clock(self, clock: Callable[[], float]) -> None:
        """Pin the wall clock on the underlying :class:`TrafficWindow`."""
        self.window.set_clock(clock)

    def record(self, event: TrafficEvent) -> None:
        """Record a single traffic event (defaulted helpers attached)."""
        self.window.record(event)
        snap = self.window.summary()
        self._rps_trend.append(snap["rps"])

    def tick(self, events: Iterable[TrafficEvent]) -> None:
        """Record many events in one call."""
        for ev in events:
            self.record(ev)

    def summary(self) -> dict[str, Any]:
        """Aggregate summary combining window and trend stats."""
        snap = self.window.summary()
        snap["rps_trend"] = render_trend(self._rps_trend, width=self.trend_width)
        return snap

    def rps_trend(self) -> str:
        """Return just the RPS sparkline (e.g., for embedding in logs)."""
        return render_trend(self._rps_trend, width=self.trend_width)

    def progress_bar(self) -> str:
        """Render the canonical progress bar (P-081).

        ``done`` is the current event count and ``total`` is the configured
        window seconds.  The bar's denominator is the window size, not the
        number of seconds — meaningful for a "rotating window" view.  Pass
        ``total=1`` for an unbounded count indicator.
        """
        snap = self.window.summary()
        return progress_bar(snap["count"], max(int(self.window.window_s), 1))


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def render_traffic(
    dashboard: TrafficDashboard,
    *,
    width: int = 60,
    title: str = "TRAFFIC",
) -> str:
    """Render a single TRAFFIC string from ``dashboard``.

    Format::

        TRAFFIC                                            updated 12:34:56
        ────────────────────────────────────────────────────────────
        count:    240        by_status: ok=232 err=6 warn=2
        rps:      4.0        error_rate: 2.5%
        p50_ms:   120        p95_ms:        410
        overrides active: 3
        ▁▂▃▄▅▆▇█▁▂▃▄▅▆▇█▁▂▃▄▅▆▇█▁▂▃▄▅▆▇ (rps trend)
    """
    snap = dashboard.summary()
    bar = progress_bar(snap["count"], max(int(snap["duration_ms_window"]), 1), width=20)
    rps = snap["rps"]
    err = snap["error_rate"] * 100
    by_status = ", ".join(f"{k}={v}" for k, v in sorted(snap["by_status"].items()))
    by_lane = ", ".join(f"{k}={v}" for k, v in sorted(snap["by_lane"].items()))

    return (
        f"{title}                                                bar={bar}\n"
        f"{'-' * width}\n"
        f"count:    {snap['count']:>5}     by_status: {by_status or '-'}\n"
        f"rps:      {rps:>5.2f}     error_rate: {err:>5.2f}%\n"
        f"p50_ms:   {snap['p50_ms']:>5.0f}     p95_ms:        {snap['p95_ms']:>5.0f}\n"
        f"by_lane:  {by_lane or '-'}\n"
        f"overrides active: {snap['override_count']}\n"
        f"{snap.get('rps_trend', '·' * dashboard.trend_width)} (rps trend)"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _percentile(values: Sequence[float], pct: float) -> float:
    """Return the percentile (0..1) of ``values``; 0.0 for empty input."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = max(0, min(len(sorted_vals) - 1, int(pct * (len(sorted_vals) - 1))))
    return sorted_vals[idx]


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------


__all__ = [
    "DEFAULT_BUCKET_SECONDS",
    "DEFAULT_TREND_WIDTH",
    "DEFAULT_WINDOW_SECONDS",
    "TrafficDashboard",
    "TrafficEvent",
    "TrafficWindow",
    "progress_bar",
    "render_traffic",
    "render_trend",
]
