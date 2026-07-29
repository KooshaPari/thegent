"""Tests for sink release on the progress emitter (L19).

These tests verify that the emitter exposes an explicit ``release()`` method
so callers can drop a strong reference to the bound sink without losing the
emitter. This closes the leak path described in L19 (audit scorecard) for
long-running sessions where sinks are rotated.
"""

from __future__ import annotations

from thegent.ux.progress_emitter import ProgressTick, ProgressTickEmitter


class _FakeSink:
    """Weak-referenceable stand-in for an :class:`OperatorCockpit`."""


def test_bind_keeps_strong_reference() -> None:
    emitter = ProgressTickEmitter(sink=None)
    sink = _FakeSink()

    emitter.bind(sink)
    assert emitter.sink is sink


def test_bind_with_non_weakrefable_sink_does_not_raise() -> None:
    """Plain ``dict`` instances cannot be weak-referenced; binding must still work."""
    emitter = ProgressTickEmitter(sink=None)

    emitter.bind({"not": "weakrefable"})  # type: ignore[arg-type]

    assert emitter.sink == {"not": "weakrefable"}


def test_bind_none_clears_sink() -> None:
    emitter = ProgressTickEmitter(sink=None)
    sink = _FakeSink()

    emitter.bind(sink)
    assert emitter.sink is sink

    emitter.bind(None)
    assert emitter.sink is None

    # Re-binding after None must work and return the new sink.
    sink2 = _FakeSink()
    emitter.bind(sink2)
    assert emitter.sink is sink2


def test_release_drops_sink_reference() -> None:
    emitter = ProgressTickEmitter(sink=None)
    sink = _FakeSink()
    emitter.bind(sink)
    assert emitter.sink is sink

    emitter.release()
    assert emitter.sink is None


def test_release_is_chainable() -> None:
    emitter = ProgressTickEmitter(sink=None).bind(_FakeSink())

    result = emitter.release()

    assert result is emitter
    assert emitter.sink is None


def test_emit_after_release_drops_silently() -> None:
    """After release, emit should behave like the null path."""
    emitter = ProgressTickEmitter(sink=None)
    sink = _FakeSink()
    emitter.bind(sink)
    emitter.release()

    result = emitter.emit(ProgressTick(done=5, total=10))
    assert result.ok
    assert result.accepted == 1
