"""WL700 — L26 Event-Driven Extension Surface (Wildcard Subscription).

Pins the deferred wildcard subscription surface that was punted at
WL150 (per the audit: *"No wildcards — keep the surface minimal.
Wildcard subscription is a future Phase 4 surface; current call sites
never publish to wildcards."*).  The bus now supports both
**exact-match** (``subscribe(event_type, handler)``) and **wildcard**
(``subscribe_wildcard(pattern, handler)``) registration, with the
following guarantees:

* ``pattern`` uses ``fnmatch`` glob semantics (case-sensitive) via
  ``fnmatch.fnmatchcase``.
* A single ``publish(event_type, data)`` fans out to BOTH the
  exact-match and wildcard registries, in registration order, with
  the exact-match handlers firing first.
* ``subscribe_wildcard`` returns an idempotent unsubscriber (calling
  it twice is a no-op).
* ``unsubscribe_wildcard(pattern, handler)`` is the identity-keyed
  removal helper (for callers that lost the unsubscriber).
* ``wildcard_patterns()`` and ``wildcard_subscriber_count()`` expose
  the wildcard registry for telemetry / tests.
* The ``EventBusInterface`` Protocol is **not** widened — wildcards
  are a concrete-class extension so downstream Protocol checks (e.g.
  ``isinstance(bus, EventBusInterface)``) keep working.
* Handler exception isolation is preserved across both registries
  (a misbehaving wildcard subscriber cannot starve exact-match
  subscribers and vice versa).
* ``clear()`` wipes both registries.

These tests lock the contract used by extension surfaces (cockpit
telemetry, audit hooks, observability fans) that need to listen to
whole event-name families (``execution:*``, ``policy:*``, ``*:failed``)
without enumerating every concrete event type up front.
"""

from __future__ import annotations

import threading

import pytest

from thegent.core.events import (
    EventHandlerError,
    InMemoryEventBus,
    get_default_event_bus,
    reset_default_event_bus,
)
from thegent.core.ports import EventBusInterface


# ---------------------------------------------------------------------------
# Protocol identity preserved (wildcards do not widen the Protocol)
# ---------------------------------------------------------------------------


def test_event_bus_interface_protocol_unaffected_by_wildcards() -> None:
    """Wildcards are a concrete-class extension; the Protocol is unchanged.

    Downstream ``isinstance(bus, EventBusInterface)`` checks must keep
    working — WL700 deliberately does NOT add ``subscribe_wildcard``
    to ``EventBusInterface`` so the Protocol stays minimal.
    """
    bus = InMemoryEventBus()
    assert isinstance(bus, EventBusInterface)
    # Runtime-checkable Protocol only requires publish/emit/subscribe.
    assert callable(bus.publish)
    assert callable(bus.emit)
    assert callable(bus.subscribe)
    # The wildcard surface is concrete-class only — not on the Protocol.
    assert not hasattr(EventBusInterface, "subscribe_wildcard")
    assert not hasattr(EventBusInterface, "unsubscribe_wildcard")


def test_subscribe_wildcard_is_defined_on_concrete_class_only() -> None:
    bus = InMemoryEventBus()
    assert callable(bus.subscribe_wildcard)
    assert callable(bus.unsubscribe_wildcard)
    assert callable(bus.wildcard_patterns)
    assert callable(bus.wildcard_subscriber_count)


# ---------------------------------------------------------------------------
# Glob pattern semantics (fnmatch, case-sensitive)
# ---------------------------------------------------------------------------


def test_star_pattern_matches_every_event() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("*", lambda d: fired.append(d))

    bus.publish("execution:started", "a")
    bus.publish("policy:violation", "b")
    bus.publish("anything-at-all", "c")

    assert fired == ["a", "b", "c"]
    assert bus.wildcard_subscriber_count("*") == 1


def test_prefix_pattern_matches_family_events() -> None:
    bus = InMemoryEventBus()
    fired: list[tuple[str, str]] = []
    bus.subscribe_wildcard("execution:*", lambda d: fired.append(("exec", d)))

    bus.publish("execution:started", "a")
    bus.publish("execution:completed", "b")
    bus.publish("execution:failed", "c")
    bus.publish("policy:violation", "d")  # NOT matched

    assert fired == [("exec", "a"), ("exec", "b"), ("exec", "c")]
    assert bus.wildcard_subscriber_count("execution:*") == 1


def test_suffix_pattern_matches_event_family_suffix() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("*:failed", lambda d: fired.append(d))

    bus.publish("execution:failed", "a")
    bus.publish("validation:failed", "b")
    bus.publish("execution:started", "c")  # NOT matched

    assert fired == ["a", "b"]


def test_contains_pattern_matches_event_name_substrings() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("*policy*", lambda d: fired.append(d))

    bus.publish("policy:violation", "a")
    bus.publish("audit:policy:check", "b")
    bus.publish("execution:started", "c")  # NOT matched

    assert fired == ["a", "b"]


def test_question_mark_matches_single_character() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("evt:?", lambda d: fired.append(d))

    bus.publish("evt:a", "1")  # matches (single char)
    bus.publish("evt:b", "2")  # matches
    bus.publish("evt:ab", "3")  # does NOT match (two chars)
    bus.publish("evt:", "4")  # does NOT match (zero chars)

    assert fired == ["1", "2"]


def test_character_class_pattern_matches_bracketed_set() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("status:[123]", lambda d: fired.append(d))

    bus.publish("status:1", "ok")
    bus.publish("status:2", "ok")
    bus.publish("status:3", "ok")
    bus.publish("status:4", "nope")

    assert fired == ["ok", "ok", "ok"]


def test_no_wildcard_characters_pattern_matches_exact_string() -> None:
    """Patterns without ``*?[`` are matched as exact strings (fnmatch)."""
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("execution:started", lambda d: fired.append(d))

    bus.publish("execution:started", "a")
    bus.publish("execution:started:late", "b")  # NOT matched (extra suffix)
    bus.publish("execution", "c")  # NOT matched (prefix only)

    assert fired == ["a"]


def test_pattern_matching_is_case_sensitive() -> None:
    """``fnmatchcase`` semantics — uppercase vs lowercase are distinct."""
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("Execution:*", lambda d: fired.append(d))

    bus.publish("Execution:Started", "a")
    bus.publish("execution:started", "b")  # NOT matched (lowercase)

    assert fired == ["a"]


# ---------------------------------------------------------------------------
# Unsubscriber semantics
# ---------------------------------------------------------------------------


def test_subscribe_wildcard_returns_idempotent_unsubscriber() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    unsub = bus.subscribe_wildcard("*", lambda d: fired.append(d))

    bus.publish("evt", "a")
    assert fired == ["a"]

    unsub()
    bus.publish("evt", "b")
    assert fired == ["a"]

    # Idempotent: a second call is a no-op.
    unsub()
    unsub()
    assert bus.wildcard_subscriber_count("*") == 0


def test_unsubscribe_wildcard_removes_by_identity() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    handler = lambda d: fired.append(d)  # noqa: E731
    bus.subscribe_wildcard("execution:*", handler)
    assert bus.wildcard_subscriber_count("execution:*") == 1

    removed = bus.unsubscribe_wildcard("execution:*", handler)
    assert removed is True
    assert bus.wildcard_subscriber_count("execution:*") == 0

    # Second remove returns False (no-op).
    assert bus.unsubscribe_wildcard("execution:*", handler) is False


def test_unsubscribe_wildcard_does_not_match_different_pattern() -> None:
    bus = InMemoryEventBus()
    handler = lambda d: None  # noqa: E731
    bus.subscribe_wildcard("execution:*", handler)
    # Wrong pattern — must not match.
    assert bus.unsubscribe_wildcard("policy:*", handler) is False
    assert bus.wildcard_subscriber_count("execution:*") == 1
    # Right pattern — must remove.
    assert bus.unsubscribe_wildcard("execution:*", handler) is True


def test_unsubscribe_wildcard_only_removes_first_matching_registration() -> None:
    """Same handler subscribed twice on the same pattern = two registrations."""
    bus = InMemoryEventBus()
    fired: list[str] = []
    handler = lambda d: fired.append(d)  # noqa: E731
    bus.subscribe_wildcard("e", handler)
    bus.subscribe_wildcard("e", handler)
    assert bus.wildcard_subscriber_count("e") == 2

    assert bus.unsubscribe_wildcard("e", handler) is True
    assert bus.wildcard_subscriber_count("e") == 1
    # Still one left.
    assert bus.unsubscribe_wildcard("e", handler) is True
    assert bus.wildcard_subscriber_count("e") == 0


def test_subscribe_wildcard_rejects_non_callable_handler() -> None:
    bus = InMemoryEventBus()
    with pytest.raises(TypeError) as excinfo:
        bus.subscribe_wildcard("e", "not-callable")  # type: ignore[arg-type]
    assert "callable" in str(excinfo.value).lower()


# ---------------------------------------------------------------------------
# Mixed dispatch: exact + wildcard fire together, exact first
# ---------------------------------------------------------------------------


def test_exact_and_wildcard_subscribers_both_fire_on_publish() -> None:
    bus = InMemoryEventBus()
    log: list[str] = []

    bus.subscribe("execution:started", lambda d: log.append(f"exact:{d}"))
    bus.subscribe_wildcard("execution:*", lambda d: log.append(f"wild:{d}"))

    bus.publish("execution:started", "x")
    # Exact first (registration order), then wildcard.
    assert log == ["exact:x", "wild:x"]


def test_wildcard_only_subscriber_fires_on_match() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("policy:*", lambda d: fired.append(d))

    bus.publish("policy:violation", "x")
    assert fired == ["x"]
    # And the publish_count incremented normally.
    assert bus.publish_count == 1


def test_wildcard_handler_does_not_fire_on_non_matching_event() -> None:
    bus = InMemoryEventBus()
    fired: list[str] = []
    bus.subscribe_wildcard("execution:*", lambda d: fired.append(d))

    bus.publish("policy:violation", "x")
    assert fired == []
    # publish_count still increments.
    assert bus.publish_count == 1


def test_multiple_wildcard_handlers_dispatch_in_registration_order() -> None:
    bus = InMemoryEventBus()
    log: list[str] = []
    bus.subscribe_wildcard("evt:*", lambda d: log.append("a"))
    bus.subscribe_wildcard("evt:*", lambda d: log.append("b"))
    bus.subscribe_wildcard("evt:*", lambda d: log.append("c"))

    bus.publish("evt:1", None)
    assert log == ["a", "b", "c"]


def test_exact_handlers_dispatch_before_any_wildcard_handlers() -> None:
    bus = InMemoryEventBus()
    log: list[str] = []
    bus.subscribe_wildcard("*", lambda d: log.append("wild1"))
    bus.subscribe("e", lambda d: log.append("exact1"))
    bus.subscribe_wildcard("e", lambda d: log.append("wild2"))
    bus.subscribe("e", lambda d: log.append("exact2"))

    bus.publish("e", None)
    # Exact subscribers fire first in registration order, then wildcard
    # subscribers (also in registration order).  The order reflects
    # _dispatch's two-pass design.
    assert log == ["exact1", "exact2", "wild1", "wild2"]


def test_handler_invocation_count_includes_wildcard_dispatch() -> None:
    bus = InMemoryEventBus()
    bus.subscribe("e", lambda d: None)
    bus.subscribe_wildcard("e", lambda d: None)
    bus.subscribe_wildcard("*", lambda d: None)

    bus.publish("e", "data")
    # 1 exact + 1 wildcard-on-"e" + 1 wildcard-on-"*" = 3 invocations.
    assert bus.handler_invocation_count == 3


# ---------------------------------------------------------------------------
# Introspection helpers
# ---------------------------------------------------------------------------


def test_wildcard_subscriber_count_returns_zero_for_empty_registry() -> None:
    bus = InMemoryEventBus()
    assert bus.wildcard_subscriber_count() == 0
    assert bus.wildcard_subscriber_count("*") == 0


def test_wildcard_subscriber_count_per_pattern() -> None:
    bus = InMemoryEventBus()
    bus.subscribe_wildcard("execution:*", lambda d: None)
    bus.subscribe_wildcard("execution:*", lambda d: None)
    bus.subscribe_wildcard("policy:*", lambda d: None)

    assert bus.wildcard_subscriber_count() == 3
    assert bus.wildcard_subscriber_count("execution:*") == 2
    assert bus.wildcard_subscriber_count("policy:*") == 1
    assert bus.wildcard_subscriber_count("audit:*") == 0


def test_wildcard_patterns_returns_sorted_unique_patterns() -> None:
    bus = InMemoryEventBus()
    bus.subscribe_wildcard("zeta:*", lambda d: None)
    bus.subscribe_wildcard("alpha:*", lambda d: None)
    bus.subscribe_wildcard("alpha:*", lambda d: None)  # duplicate
    bus.subscribe_wildcard("mu:*", lambda d: None)

    assert bus.wildcard_patterns() == ["alpha:*", "mu:*", "zeta:*"]


def test_clear_wipes_exact_and_wildcard_registries() -> None:
    bus = InMemoryEventBus()
    bus.subscribe("e", lambda d: None)
    bus.subscribe_wildcard("*", lambda d: None)
    assert bus.subscribed_event_types() == ["e"]
    assert bus.wildcard_subscriber_count() == 1

    bus.clear()
    assert bus.subscribed_event_types() == []
    assert bus.wildcard_subscriber_count() == 0
    assert bus.wildcard_patterns() == []


# ---------------------------------------------------------------------------
# Handler exception isolation across both registries
# ---------------------------------------------------------------------------


def test_wildcard_handler_exception_does_not_block_exact_handlers() -> None:
    bus = InMemoryEventBus()
    survived: list[str] = []

    def bad_wild(_: object) -> None:
        raise ValueError("wild boom")

    bus.subscribe("e", lambda d: survived.append(f"exact:{d}"))
    bus.subscribe_wildcard("e", bad_wild)
    bus.subscribe("e", lambda d: survived.append(f"exact2:{d}"))

    bus.publish("e", "payload")
    # Both exact handlers fire; the bad wildcard does not abort dispatch.
    assert survived == ["exact:payload", "exact2:payload"]
    # handler_invocation_count = 3 (2 exact + 1 wildcard).
    assert bus.handler_invocation_count == 3


def test_exact_handler_exception_does_not_block_wildcard_handlers() -> None:
    bus = InMemoryEventBus()
    survived: list[str] = []

    def bad_exact(_: object) -> None:
        raise ValueError("exact boom")

    bus.subscribe("e", bad_exact)
    bus.subscribe("e", lambda d: survived.append(f"exact:{d}"))
    bus.subscribe_wildcard("e", lambda d: survived.append(f"wild:{d}"))

    bus.publish("e", "payload")
    # Wildcard handlers still fire after the bad exact handler.
    assert "wild:payload" in survived
    assert "exact:payload" in survived


def test_strict_mode_re_raises_wildcard_handler_exception() -> None:
    bus = InMemoryEventBus(strict=True)

    def bad_wild(_: object) -> None:
        raise RuntimeError("strict wild boom")

    bus.subscribe_wildcard("e", bad_wild)
    with pytest.raises(EventHandlerError) as excinfo:
        bus.publish("e", "data")
    assert isinstance(excinfo.value.__cause__, RuntimeError)
    assert "strict wild boom" in str(excinfo.value.__cause__)


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


def test_concurrent_subscribe_wildcard_and_publish_are_safe() -> None:
    bus = InMemoryEventBus()
    counter = []
    counter_lock = threading.Lock()

    def make_handler(label: str):
        def handler(_: object) -> None:
            with counter_lock:
                counter.append(label)

        return handler

    def worker(idx: int) -> None:
        # Each worker subscribes to its own wildcard AND publishes.
        bus.subscribe_wildcard(f"evt_{idx}:*", make_handler(f"w{idx}"))
        for k in range(20):
            bus.publish(f"evt_{idx}:k{k}", k)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 8 workers × 20 publishes each = 160 deliveries.
    assert bus.publish_count == 8 * 20
    assert len(counter) == 8 * 20


def test_concurrent_unsubscribe_wildcard_during_publish_is_safe() -> None:
    """Unsubscribe during dispatch must not corrupt or skip handlers."""
    bus = InMemoryEventBus()
    fired: list[str] = []

    # Register a wildcard handler that, on first fire, unsubscribes itself.
    unsub_holder: dict[str, object] = {}

    def one_shot(_: object) -> None:
        fired.append("one-shot")
        unsub = unsub_holder.get("u")
        if unsub is not None:
            unsub()  # type: ignore[arg-type]

    unsub_holder["u"] = bus.subscribe_wildcard("e", one_shot)
    bus.subscribe_wildcard("e", lambda d: fired.append("steady"))

    # First publish: both fire (one-shot fires then unsubscribes itself).
    bus.publish("e", "first")
    assert fired == ["one-shot", "steady"]
    assert bus.wildcard_subscriber_count("e") == 1

    # Second publish: only the steady handler fires.
    bus.publish("e", "second")
    assert fired == ["one-shot", "steady", "steady"]


# ---------------------------------------------------------------------------
# Singleton: wildcard registry is also reset
# ---------------------------------------------------------------------------


def test_reset_default_event_bus_clears_wildcard_registry() -> None:
    reset_default_event_bus()
    bus = get_default_event_bus()
    bus.subscribe_wildcard("*", lambda d: None)
    assert bus.wildcard_subscriber_count("*") == 1

    reset_default_event_bus()
    fresh = get_default_event_bus()
    assert fresh.wildcard_subscriber_count() == 0


# ---------------------------------------------------------------------------
# End-to-end via Executor: wildcard listeners see execution events
# ---------------------------------------------------------------------------


def test_executor_fires_wildcard_execution_listener() -> None:
    """A ``execution:*`` wildcard listener must observe executor publishes."""
    from thegent.execution.executor import Executor

    bus = InMemoryEventBus()
    fired_task_ids: list[str] = []
    bus.subscribe_wildcard("execution:*", lambda d: fired_task_ids.append(d["task_id"]))

    ex = Executor(event_bus=bus)
    result = ex.run("t-700", {"task": "demo"})

    assert result.success
    # Executor publishes at least "execution:started" + "execution:completed"
    # for a successful run; the wildcard listener sees both payloads.
    assert fired_task_ids == ["t-700", "t-700"]
    # publish_count reflects every dispatch (wildcard fans also count).
    assert bus.publish_count == 2
