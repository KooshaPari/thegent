"""Typed P-081 progress bar emitter for the operator cockpit.

This module complements :mod:`thegent.ux.cockpit` (which owns the
``_progress_bar`` glyph helper) by adding a typed *emitter* API for callers
that want to feed the cockpit's header progress bar without poking at the
private ``tick(progress=...)`` signature from many call sites.

Goals:

* Type-safe payload (:class:`ProgressTick`) so audit replays are stable.
* Thread-safe delivery (an internal ``RLock`` serialises concurrent
  :meth:`ProgressTickEmitter.emit` calls).
* Bounded memory — ``done`` is clamped to ``[0, total]``, negatives are
  dropped, ``inf``/``nan`` floats are rejected.
* Composes with :class:`thegent.ux.cockpit.OperatorCockpit` without
  depending on :mod:`thegent.ux.cockpit_bridge` (so callers can use this
  helper without standing up the full governance bridge stack).
* Zero overhead when unbound — :class:`NullProgressEmitter` short-circuits
  all calls so unit tests and non-UI code paths don't allocate.
"""

from __future__ import annotations

import logging
import math
import threading
import time as _time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, Mapping, Protocol, runtime_checkable

from .cockpit import OperatorCockpit, _progress_bar

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Typed payload
# ---------------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ProgressTick:
    """A single typed progress-bar update (P-081).

    Attributes:
        done: Units completed (clamped to ``[0, total]`` on emit).
        total: Total units. ``<= 0`` renders the empty bar ``"[" + " " * width + "]   -"``.
        label: Short tag surfaced in telemetry (e.g. ``"policy-eval"``).
        lane: Optional operator lane key (e.g. ``"standard"``, ``"fast"``).
        eta_s: Optional estimated time-to-completion, used by the cockpit header.
        emitted_at: Unix epoch when the tick was minted (filled automatically
            when ``None`` is supplied).
    """

    done: int
    total: int
    label: str = ""
    lane: str = ""
    eta_s: float | None = None
    emitted_at: float = 0.0

    def to_payload(self) -> Mapping[str, object]:
        """Return a JSONL-friendly mapping for audit logs."""
        return {
            "done": int(self.done),
            "total": int(self.total),
            "label": self.label,
            "lane": self.lane,
            "eta_s": self.eta_s,
            "emitted_at": float(self.emitted_at),
        }


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ProgressEmitResult:
    """Outcome of a single :meth:`ProgressTickEmitter.emit` call.

    Mirrors :class:`thegent.ux.cockpit_bridge.BridgeResult` so callers can
    use the same error-handling pattern across the bridge layer.
    """

    accepted: int = 0
    dropped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """``True`` when no errors were encountered during emission."""
        return not self.errors


# ---------------------------------------------------------------------------
# Sink protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ProgressSink(Protocol):
    """Anything that can receive a :class:`ProgressTick` payload.

    Implemented by :class:`OperatorCockpit` indirectly via ``tick()``;
    the emitter wraps that to keep the public API typed.
    """

    def receive_progress_tick(self, tick: ProgressTick) -> None:
        """Receive a typed progress tick. Must be thread-safe."""
        ...


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _coerce_int(value: object) -> int | None:
    """Convert ``value`` to a real integer, rejecting ``bool`` and non-finite floats.

    Returns ``None`` when the value cannot be converted.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return int(value)
    return None


def _coerce_float(value: object) -> float | None:
    """Convert ``value`` to a finite float, rejecting ``bool`` and non-finite."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        return f if math.isfinite(f) else None
    return None


def _clamp_tick(tick: ProgressTick) -> ProgressTick:
    """Clamp ``done`` to ``[0, total]`` and reject non-finite floats.

    Returns a new :class:`ProgressTick`; never mutates the input.
    """
    done = max(0, min(int(tick.done), int(tick.total)))
    total = max(int(tick.total), 0)
    eta = tick.eta_s
    if eta is not None and not math.isfinite(float(eta)):
        eta = None
    return ProgressTick(
        done=done,
        total=total,
        label=tick.label,
        lane=tick.lane,
        eta_s=float(eta) if eta is not None else None,
        emitted_at=tick.emitted_at or _time.time(),
    )


# ---------------------------------------------------------------------------
# Cockpit-backed emitter
# ---------------------------------------------------------------------------


class ProgressTickEmitter:
    """Typed progress bar emitter that pushes into an :class:`OperatorCockpit`.

    The emitter:

    * holds a reference to a :class:`ProgressSink` (typically an
      :class:`OperatorCockpit`); if the sink is ``None`` every call is a
      no-op returning :class:`ProgressEmitResult` with zero accepted.
    * serialises concurrent calls under an ``RLock`` so the cockpit never
      sees interleaved ``tick()`` invocations.
    * never raises to the caller — invalid payloads are dropped and
      recorded in :attr:`ProgressEmitResult.errors`.
    """

    def __init__(
        self,
        sink: ProgressSink | OperatorCockpit | None,
        *,
        default_total: int = 100,
        clock: Callable[[], float] | None = None,
    ) -> None:
        # We accept OperatorCockpit by structural typing; we don't import
        # the class via ``isinstance`` so test doubles work easily.
        self._sink = sink
        self._default_total = max(int(default_total), 0)
        self._clock = clock or _time.time
        self._lock = threading.RLock()
        # Counters (read-only public surface)
        self._accepted = 0
        self._dropped = 0

    # ------------------------------------------------------------- counters

    @property
    def accepted(self) -> int:
        """Total ticks that were forwarded to the sink since construction."""
        return self._accepted

    @property
    def dropped(self) -> int:
        """Total ticks that were dropped (invalid payload) since construction."""
        return self._dropped

    @property
    def sink(self) -> ProgressSink | OperatorCockpit | None:
        """Currently bound sink (may be ``None`` for a null emitter)."""
        return self._sink

    # ------------------------------------------------------------- mutators

    def bind(self, sink: ProgressSink | OperatorCockpit | None) -> "ProgressTickEmitter":
        """Bind or rebind the sink. Returns ``self`` for chaining."""
        with self._lock:
            self._sink = sink
        return self

    # ------------------------------------------------------------- emit

    def emit(
        self,
        tick: ProgressTick | None = None,
        **overrides: object,
    ) -> ProgressEmitResult:
        """Forward one :class:`ProgressTick` to the sink.

        ``overrides`` lets callers write ``emit(done=42, total=100, label="x")``
        without building a dataclass; the kwargs are merged onto a fresh
        :class:`ProgressTick` with the emitter's defaults.
        """
        payload = self._materialise(tick, overrides)
        if payload is None:
            self._dropped += 1
            return ProgressEmitResult(dropped=1, errors=["invalid tick payload"])

        sink = self._sink
        if sink is None:
            # Null emitter: still count as accepted so tests can verify the
            # call path; downstream is intentionally absent.
            self._accepted += 1
            return ProgressEmitResult(accepted=1)

        try:
            with self._lock:
                self._forward(sink, payload)
        except Exception as exc:  # noqa: BLE001 - emitter never raises.
            _LOGGER.warning("progress emitter rejected tick %s: %s", payload, exc)
            self._dropped += 1
            return ProgressEmitResult(dropped=1, errors=[str(exc)])

        self._accepted += 1
        return ProgressEmitResult(accepted=1)

    def emit_many(self, ticks: Iterable[ProgressTick]) -> ProgressEmitResult:
        """Forward a sequence of ticks, aggregating the result."""
        aggregate = ProgressEmitResult()
        for tick in ticks:
            sub = self.emit(tick)
            aggregate.accepted += sub.accepted
            aggregate.dropped += sub.dropped
            aggregate.errors.extend(sub.errors)
        return aggregate

    # ------------------------------------------------------------- helpers

    def render_bar(
        self,
        tick: ProgressTick | None = None,
        *,
        width: int = 24,
        done: int | None = None,
        total: int | None = None,
    ) -> str:
        """Render the progress bar glyph for a tick without forwarding it.

        ``done`` / ``total`` are convenience kwargs so callers can write
        ``emitter.render_bar(done=5, total=10)`` without building a tick.

        Useful for tests and CLI banners that want to preview the bar
        before sending it through the cockpit.
        """
        if tick is None and (done is not None or total is not None):
            d = int(done or 0)
            t = int(total if total is not None else self._default_total)
            return _progress_bar(max(0, min(d, max(t, 0))), max(t, 0), width=width)
        if tick is None:
            return _progress_bar(0, self._default_total, width=width)
        return _progress_bar(
            max(0, tick.done),
            max(tick.total, 0),
            width=width,
        )

    # ------------------------------------------------------------- internals

    def _materialise(
        self,
        tick: ProgressTick | None,
        overrides: Mapping[str, object],
    ) -> ProgressTick | None:
        """Build a clamped :class:`ProgressTick` from inputs.

        Returns ``None`` when the payload is malformed so callers can short
        circuit via :attr:`ProgressEmitResult.dropped`.
        """
        # 1. Determine the raw fields.
        if tick is None:
            raw_done: object = overrides.get("done", 0)
            raw_total: object = overrides.get("total", self._default_total)
            raw_label: object = overrides.get("label", "")
            raw_lane: object = overrides.get("lane", "")
            raw_eta: object | None = overrides.get("eta_s", None)
            raw_emitted: object = overrides.get("emitted_at", self._clock())
        else:
            raw_done = overrides.get("done", tick.done)
            raw_total = overrides.get("total", tick.total)
            raw_label = overrides.get("label", tick.label)
            raw_lane = overrides.get("lane", tick.lane)
            raw_eta = overrides.get("eta_s", tick.eta_s)
            raw_emitted = overrides.get("emitted_at", tick.emitted_at)

        # 2. Coerce numerics, rejecting bool / nan / inf / wrong type.
        coerced_done = _coerce_int(raw_done)
        coerced_total = _coerce_int(raw_total)
        if coerced_done is None or coerced_total is None:
            _LOGGER.debug(
                "dropping tick with non-numeric done/total: %r/%r",
                raw_done,
                raw_total,
            )
            return None
        # Negative totals are nonsensical for the cockpit (no bar to render
        # against); reject the payload rather than silently floor to zero so
        # upstream callers learn about bad input.
        if coerced_total < 0:
            _LOGGER.debug("dropping tick with negative total: %r", raw_total)
            return None

        if raw_eta is None:
            coerced_eta: float | None = None
        else:
            coerced_eta = _coerce_float(raw_eta)

        # 3. Build the tick.
        try:
            emitted = float(raw_emitted) if raw_emitted is not None else self._clock()
        except (TypeError, ValueError):
            emitted = self._clock()
        try:
            base = ProgressTick(
                done=coerced_done,
                total=coerced_total,
                label=str(raw_label) if raw_label is not None else "",
                lane=str(raw_lane) if raw_lane is not None else "",
                eta_s=coerced_eta,
                emitted_at=emitted,
            )
        except (TypeError, ValueError) as exc:
            _LOGGER.debug("dropping tick with invalid fields: %s", exc)
            return None

        # 4. Clamp and return.
        return _clamp_tick(base)

    def _forward(self, sink: object, tick: ProgressTick) -> None:
        """Forward a tick to the sink via either the typed or duck-typed path."""
        # Preferred path: explicit protocol method.
        receive = getattr(sink, "receive_progress_tick", None)
        if callable(receive):
            receive(tick)
            return
        # Fallback path: OperatorCockpit uses tick(progress=...).
        cockpit_tick = getattr(sink, "tick", None)
        if callable(cockpit_tick):
            cockpit_tick(progress=(tick.done, max(tick.total, 0)))
            return
        raise RuntimeError(f"sink {sink!r} has no progress-receiving surface")


# ---------------------------------------------------------------------------
# Null emitter
# ---------------------------------------------------------------------------


class NullProgressEmitter(ProgressTickEmitter):
    """A no-op progress emitter.

    All :meth:`emit` calls succeed silently and the bar can still be
    rendered against the supplied values. Useful for unit tests and for
    contexts where the cockpit surface is intentionally absent.
    """

    def __init__(self, *, default_total: int = 100) -> None:
        super().__init__(sink=None, default_total=default_total)

    def emit(  # type: ignore[override]
        self,
        tick: ProgressTick | None = None,
        **overrides: object,
    ) -> ProgressEmitResult:
        """Always accept the tick without touching any sink."""
        payload = self._materialise(tick, overrides)
        if payload is None:
            self._dropped += 1
            return ProgressEmitResult(dropped=1, errors=["invalid tick payload"])
        self._accepted += 1
        return ProgressEmitResult(accepted=1)


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def stream_ticks(
    values: Iterable[tuple[int, int]],
    *,
    label: str = "",
    lane: str = "",
    clock: Callable[[], float] | None = None,
) -> Iterator[ProgressTick]:
    """Yield :class:`ProgressTick` instances for an iterable of ``(done, total)``.

    Used to wrap the common pattern of polling an external counter
    (queue length, completed work items, etc.) into typed ticks without
    needing the emitter for the iteration itself.
    """
    stamp = clock or _time.time
    for done, total in values:
        yield ProgressTick(
            done=int(done),
            total=int(total),
            label=label,
            lane=lane,
            emitted_at=stamp(),
        )


def coalesce_ticks(
    ticks: list[ProgressTick],
    *,
    window: int = 4,
) -> list[ProgressTick]:
    """Coalesce a sequence of ticks into a smaller windowed summary.

    The last ``window`` ticks are returned in order, with their
    ``done`` values re-baselined against the final ``total`` so the bar
    looks continuous when rendered in bursts.
    """
    if window <= 0 or not ticks:
        return []
    tail = list(ticks[-window:])
    last_total = tail[-1].total
    return [
        ProgressTick(
            done=max(0, min(int(t.done), max(int(last_total), 0))),
            total=int(last_total),
            label=t.label,
            lane=t.lane,
            eta_s=t.eta_s,
            emitted_at=t.emitted_at,
        )
        for t in tail
    ]


__all__ = [
    "NullProgressEmitter",
    "ProgressEmitResult",
    "ProgressSink",
    "ProgressTick",
    "ProgressTickEmitter",
    "coalesce_ticks",
    "stream_ticks",
]
