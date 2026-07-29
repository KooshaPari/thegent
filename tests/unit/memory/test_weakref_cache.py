"""Tests for weak-reference cache and cleanup helpers."""

import gc

from thegent.memory.weakref_cache import (
    WeakrefCache,
    cleanup_weakrefs,
    register_finalizer,
)


class Referent:
    """Weak-referenceable object used by cache and finalizer tests."""


class NoClear:
    """Container-shaped object without a clear method."""


def collect_garbage() -> None:
    """Collect unreachable referents, including cyclic garbage if present."""
    gc.collect()


def test_set_and_get_returns_live_value() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    value = Referent()

    cache.set("item", value)

    assert cache.get("item") is value


def test_get_returns_none_for_missing_key() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()

    assert cache.get("missing") is None


def test_get_evicts_entry_after_weakref_dies() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    cache.set("item", Referent())

    collect_garbage()

    assert cache.get("item") is None
    assert len(cache) == 0


def test_pop_returns_and_removes_live_value() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    value = Referent()
    cache.set("item", value)

    popped = cache.pop("item")

    assert popped is value
    assert cache.get("item") is None
    assert len(cache) == 0


def test_pop_returns_none_for_missing_key() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()

    assert cache.pop("missing") is None


def test_clear_removes_all_entries() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    values = [Referent(), Referent()]
    cache.set("first", values[0])
    cache.set("second", values[1])

    cache.clear()

    assert len(cache) == 0
    assert list(cache) == []


def test_len_counts_cached_entries() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    values = [Referent(), Referent()]
    cache.set("first", values[0])
    cache.set("second", values[1])

    assert len(cache) == 2


def test_contains_checks_cached_keys() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    value = Referent()
    cache.set("present", value)

    assert "present" in cache
    assert "missing" not in cache


def test_iter_yields_cached_keys() -> None:
    cache: WeakrefCache[str, Referent] = WeakrefCache()
    values = [Referent(), Referent()]
    cache.set("first", values[0])
    cache.set("second", values[1])

    assert list(cache) == ["first", "second"]


def test_register_finalizer_fires_when_object_is_collected() -> None:
    callbacks: list[str] = []
    value = Referent()
    register_finalizer(value, callbacks.append, args=("collected",))

    del value
    collect_garbage()

    assert callbacks == ["collected"]


def test_register_finalizer_does_not_fire_while_object_is_alive() -> None:
    callbacks: list[str] = []
    value = Referent()
    finalizer = register_finalizer(value, callbacks.append, args=("collected",))

    collect_garbage()

    assert callbacks == []
    assert finalizer.alive


def test_cleanup_weakrefs_clears_containers_on_exit() -> None:
    values = ["one", "two"]
    mapping = {"key": "value"}

    with cleanup_weakrefs(values, mapping):
        assert values
        assert mapping

    assert values == []
    assert mapping == {}


def test_cleanup_weakrefs_allows_container_without_clear() -> None:
    values = ["still here"]

    with cleanup_weakrefs(NoClear(), values):
        pass

    assert values == []
