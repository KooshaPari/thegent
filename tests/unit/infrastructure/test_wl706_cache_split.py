"""Hardening tests for the WL706 ``infra/cache`` split.

These tests pin the canonical TGNT-P9.x cache surface after the WL706 L1
Architecture hardening pass that split the legacy 419-LOC single-file
``infra/cache_v2.py`` into a 5-submodule package + 30-LOC back-compat
shim. The split closed a real test-coverage gap (the legacy module
shipped with **0 tests**) and reduced cognitive complexity of the two
fan-out hot paths via extracted helpers:

* ``CrossProcessSingleflight.do`` CC reduced via ``_try_acquire_lock`` /
  ``_wait_for_result`` / ``_persist_result`` (three helpers).
* ``MultiTierCache.get`` CC reduced via ``_check_l1`` /
  ``_check_l2_promote_to_l1`` / ``_check_l3_promote_to_l2_and_l1``
  (three helpers).

Coverage shape:

* Canonical resolution (5 tests) — package + sub-module shape.
* ``CacheV2`` surface (5 tests) — TTL round-trip / miss / expiry.
* ``Singleflight`` surface (4 tests) — coalescing semantics.
* ``CrossProcessSingleflight`` surface (3 tests, tmp_path) — file-lock
  happy path + cache hit + lazy mkdir.
* ``HeatBasedLRU`` surface (4 tests) — get/put round-trip + capacity.
* ``CacheInvalidator`` surface (2 tests) — graceful watchdog absence.
* ``MultiTierCache`` surface (7 tests) — L1 hit / miss / fetch /
  delete / clear / stats.
* Back-compat shim (3 tests) — legacy import path resolves to the
  canonical package surface (identity check).
* AST purity (2 tests) — shim LOC ≤ 35, no class definitions inside
  the shim body.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import time
from pathlib import Path

import pytest

from thegent.infra.cache import (
    CacheInvalidator,
    CacheV2,
    CrossProcessSingleflight,
    HAS_WATCHDOG,
    HeatBasedLRU,
    MultiTierCache,
    Singleflight,
    get_cache,
)

PACKAGE = "thegent.infra.cache"
TTL_MODULE = "thegent.infra.cache.ttl"
SINGLEFLIGHT_MODULE = "thegent.infra.cache.singleflight"
HEAT_LRU_MODULE = "thegent.infra.cache.heat_lru"
INVALIDATOR_MODULE = "thegent.infra.cache.invalidator"
MULTI_TIER_MODULE = "thegent.infra.cache.multi_tier"
SHIM_MODULE = "thegent.infra.cache_v2"


# ---------------------------------------------------------------------------
# Canonical resolution (5 tests)
# ---------------------------------------------------------------------------


def test_cache_package_imports_clean() -> None:
    """``thegent.infra.cache`` imports cleanly as a package."""
    pkg = importlib.import_module(PACKAGE)
    pkg_file = Path(pkg.__file__).as_posix()
    assert pkg_file.endswith("/infra/cache/__init__.py"), (
        f"package __file__ should point at /infra/cache/__init__.py, got {pkg_file}"
    )


def test_cache_package_exposes_canonical_surface() -> None:
    """All 7 canonical symbols are reachable from ``thegent.infra.cache``."""
    pkg = importlib.import_module(PACKAGE)
    for name in (
        "CacheV2",
        "Singleflight",
        "CrossProcessSingleflight",
        "HeatBasedLRU",
        "CacheInvalidator",
        "MultiTierCache",
        "get_cache",
    ):
        assert hasattr(pkg, name), f"{name} missing from thegent.infra.cache"


def test_cache_package_all_pins_surface() -> None:
    """``__all__`` pins the canonical surface (8 entries)."""
    pkg = importlib.import_module(PACKAGE)
    assert sorted(pkg.__all__) == sorted(
        (
            "CacheInvalidator",
            "CacheV2",
            "CrossProcessSingleflight",
            "HAS_WATCHDOG",
            "HeatBasedLRU",
            "MultiTierCache",
            "Singleflight",
            "get_cache",
        )
    )


def test_shim_identity_matches_canonical_classes() -> None:
    """The back-compat shim re-exports the canonical classes (identity check)."""
    pkg = importlib.import_module(PACKAGE)
    shim = importlib.import_module(SHIM_MODULE)
    for cls_name in (
        "CacheV2",
        "Singleflight",
        "CrossProcessSingleflight",
        "HeatBasedLRU",
        "CacheInvalidator",
        "MultiTierCache",
    ):
        canonical = getattr(pkg, cls_name)
        shim_obj = getattr(shim, cls_name)
        assert canonical is shim_obj, f"{cls_name}: canonical != shim"
    # get_cache is a function (not a class); identity check is still valid.
    assert pkg.get_cache is shim.get_cache


def test_cache_package_docstring_cites_tgnt_p9() -> None:
    """The package docstring cites the TGNT-P9.x origin (sanity)."""
    pkg = importlib.import_module(PACKAGE)
    assert "TGNT-P9" in (pkg.__doc__ or ""), "package docstring should cite TGNT-P9.x lineage"


# ---------------------------------------------------------------------------
# CacheV2 surface (5 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_v2_set_then_get_roundtrip(tmp_path: Path) -> None:
    """CacheV2: ``set`` then ``get`` returns the value (round-trip)."""
    cache = CacheV2(tmp_path, namespace="roundtrip")
    await cache.set("k", "v")
    assert await cache.get("k") == "v"


@pytest.mark.asyncio
async def test_cache_v2_get_missing_returns_none(tmp_path: Path) -> None:
    """CacheV2: ``get`` for missing key returns ``None``."""
    cache = CacheV2(tmp_path, namespace="miss")
    assert await cache.get("nonexistent") is None


@pytest.mark.asyncio
async def test_cache_v2_ttl_expiry(tmp_path: Path) -> None:
    """CacheV2: expired key returns ``None`` and is removed."""
    cache = CacheV2(tmp_path, namespace="ttl")
    await cache.set("ephemeral", "v", ttl=1)
    # Force expiry without sleeping
    cache._store["ephemeral"] = (time.time() - 1, "v")
    assert await cache.get("ephemeral") is None
    assert "ephemeral" not in cache._store


@pytest.mark.asyncio
async def test_cache_v2_no_ttl_means_no_expiry(tmp_path: Path) -> None:
    """CacheV2: ``ttl=None`` stores without expiry."""
    cache = CacheV2(tmp_path, namespace="nottl")
    await cache.set("forever", "v")
    # Even after manipulating the stored expiry_at to a past time,
    # an entry with expires_at=None must not be evicted.
    cache._store["forever"] = (None, "v")
    assert await cache.get("forever") == "v"


@pytest.mark.asyncio
async def test_cache_v2_clear_expired_evicts_only_expired(tmp_path: Path) -> None:
    """CacheV2: ``clear_expired`` evicts only entries whose TTL elapsed."""
    cache = CacheV2(tmp_path, namespace="mix")
    # An entry already expired, an entry with no TTL, and an entry in the future.
    cache._store["old"] = (time.time() - 5, "old-val")
    cache._store["forever"] = (None, "forever-val")
    cache._store["future"] = (time.time() + 999, "future-val")
    await cache.clear_expired()
    assert "old" not in cache._store
    assert "forever" in cache._store
    assert "future" in cache._store


# ---------------------------------------------------------------------------
# Singleflight surface (4 tests)
# ---------------------------------------------------------------------------


def test_singleflight_first_call_executes_func() -> None:
    """Singleflight: first call invokes the callable."""
    sf = Singleflight()
    assert sf.do("k", lambda: 42) == 42


def test_singleflight_second_call_re_executes_sequentially() -> None:
    """Singleflight: sequential calls re-execute (results cache is concurrent-only).

    The legacy ``infra/cache_v2`` ``Singleflight`` only dedupes *concurrent*
    calls (it removes the key from ``self.calls`` immediately after execution).
    Sequential calls therefore re-execute the callable — only the
    in-process cross-call *wait* path consults ``self.results``. This is a
    documented divergence from the parallel ``mesh/cache.Singleflight``
    implementation (which checks ``results`` first).
    """
    sf = Singleflight()
    call_count = 0

    def work() -> str:
        nonlocal call_count
        call_count += 1
        return "done"

    assert sf.do("k", work) == "done"
    assert sf.do("k", work) == "done"
    assert call_count == 2  # sequential = re-execution; cf. concurrent dedup


def test_singleflight_different_keys_independent() -> None:
    """Singleflight: different keys execute independently."""
    sf = Singleflight()
    assert sf.do("a", lambda: "alpha") == "alpha"
    assert sf.do("b", lambda: "beta") == "beta"


def test_singleflight_exception_propagates() -> None:
    """Singleflight: ``do()`` propagates exceptions to the caller."""
    sf = Singleflight()

    def boom() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        sf.do("fail", boom)


# ---------------------------------------------------------------------------
# CrossProcessSingleflight surface (3 tests)
# ---------------------------------------------------------------------------


def test_cross_process_singleflight_first_call_executes(tmp_path: Path) -> None:
    """CrossProcessSingleflight: first call executes the callable and persists."""
    sf = CrossProcessSingleflight(tmp_path / "coord")
    counter = {"n": 0}

    def work() -> int:
        counter["n"] += 1
        return counter["n"]

    assert sf.do("key-a", work) == 1
    # Lock should be released after execution.
    coord = tmp_path / "coord"
    leftover_locks = list(coord.glob("*.lock"))
    assert leftover_locks == [], f"lock files left behind: {leftover_locks}"
    # Result should be persisted on disk.
    result_files = list(coord.glob("*.result"))
    assert len(result_files) == 1, f"expected 1 result file, got {result_files}"


def test_cross_process_singleflight_second_call_returns_cached(tmp_path: Path) -> None:
    """CrossProcessSingleflight: second call within TTL returns the cached result."""
    sf = CrossProcessSingleflight(tmp_path / "coord")
    counter = {"n": 0}

    def work() -> int:
        counter["n"] += 1
        return counter["n"]

    first = sf.do("key-b", work)
    second = sf.do("key-b", work, ttl=300)
    assert first == 1
    assert second == 1
    assert counter["n"] == 1  # second call did not re-execute


def test_cross_process_singleflight_creates_coordination_dir(tmp_path: Path) -> None:
    """CrossProcessSingleflight: missing coordination dir is created on construction."""
    coord = tmp_path / "fresh"
    assert not coord.exists()
    CrossProcessSingleflight(coord)
    assert coord.is_dir()


# ---------------------------------------------------------------------------
# HeatBasedLRU surface (4 tests)
# ---------------------------------------------------------------------------


def test_heat_lru_get_missing_returns_none(tmp_path: Path) -> None:  # tmp_path for parity with mesh/cache
    """HeatBasedLRU: missing key returns ``None``."""
    del tmp_path  # unused; capacity-based cache, no directory needed
    lru = HeatBasedLRU(capacity=10)
    assert lru.get("nonexistent") is None


def test_heat_lru_put_then_get_roundtrip() -> None:
    """HeatBasedLRU: ``put`` then ``get`` round-trip."""
    lru = HeatBasedLRU(capacity=10)
    lru.put("k", "v")
    assert lru.get("k") == "v"


def test_heat_lru_put_overwrites_existing() -> None:
    """HeatBasedLRU: ``put`` on an existing key updates the value."""
    lru = HeatBasedLRU(capacity=10)
    lru.put("k", "old")
    lru.put("k", "new")
    assert lru.get("k") == "new"


def test_heat_lru_capacity_enforced() -> None:
    """HeatBasedLRU: inserting beyond capacity evicts an entry."""
    lru = HeatBasedLRU(capacity=3)
    lru.put("a", 1)
    lru.put("b", 2)
    lru.put("c", 3)
    # Raise the heat of b and c so a is the eviction victim.
    lru.get("b")
    lru.get("c")
    lru.put("d", 4)
    # Some entry was evicted; a (coldest) should be gone.
    assert lru.get("a") is None
    assert lru.get("d") == 4


# ---------------------------------------------------------------------------
# CacheInvalidator surface (2 tests)
# ---------------------------------------------------------------------------


def test_cache_invalidator_watch_noop_without_watchdog(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """CacheInvalidator: ``watch()`` is a silent no-op when watchdog is missing."""
    from thegent.infra.cache import invalidator as invalidator_mod

    monkeypatch.setattr(invalidator_mod, "HAS_WATCHDOG", False)
    cache = MultiTierCache()  # bare cache, just needs a .clear() method
    inv = CacheInvalidator(cache)
    inv.observer = None  # force
    # Must not raise.
    inv.watch(tmp_path)


def test_cache_invalidator_stop_safe_without_watchdog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CacheInvalidator: ``stop()`` is safe to call when watchdog is missing."""
    from thegent.infra.cache import invalidator as invalidator_mod

    monkeypatch.setattr(invalidator_mod, "HAS_WATCHDOG", False)
    cache = MultiTierCache()
    inv = CacheInvalidator(cache)
    inv.observer = None
    # Must not raise.
    inv.stop()


# ---------------------------------------------------------------------------
# MultiTierCache surface (7 tests)
# ---------------------------------------------------------------------------


def test_multi_tier_cache_set_get_l1_hit() -> None:
    """MultiTierCache: ``set`` then ``get`` round-trip (l1 hit)."""
    cache = MultiTierCache(l1_size=10, l2_size=100)
    cache.set("k", "v")
    assert cache.get("k") == "v"


def test_multi_tier_cache_get_missing_returns_none() -> None:
    """MultiTierCache: missing key returns ``None``."""
    cache = MultiTierCache()
    assert cache.get("nonexistent") is None


def test_multi_tier_cache_get_with_fetch_populates_on_miss() -> None:
    """MultiTierCache: ``get_with_fetch`` populates on miss."""
    cache = MultiTierCache()
    counter = {"n": 0}

    def fetch() -> int:
        counter["n"] += 1
        return 99

    value = cache.get_with_fetch("k", fetch)
    assert value == 99
    assert counter["n"] == 1
    # Second call returns the cached value without re-fetching.
    assert cache.get_with_fetch("k", fetch) == 99
    assert counter["n"] == 1


def test_multi_tier_cache_get_with_fetch_returns_cached_on_hit() -> None:
    """MultiTierCache: ``get_with_fetch`` returns the cached value on hit."""
    cache = MultiTierCache()
    cache.set("pre", "cached")

    def fetch() -> str:
        raise AssertionError("fetch must not be called on a cache hit")

    assert cache.get_with_fetch("pre", fetch) == "cached"


def test_multi_tier_cache_delete_removes_from_all_tiers() -> None:
    """MultiTierCache: ``delete(key)`` removes the key from every tier."""
    cache = MultiTierCache()
    cache.set("k", "v")
    assert "k" in cache.l1
    assert "k" in cache.l2
    cache.delete("k")
    assert "k" not in cache.l1
    assert "k" not in cache.l2


def test_multi_tier_cache_clear_empties_all_tiers() -> None:
    """MultiTierCache: ``clear()`` empties every tier."""
    cache = MultiTierCache()
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert len(cache.l1) == 0
    assert len(cache.l2) == 0


def test_multi_tier_cache_stats_canonical_shape() -> None:
    """MultiTierCache: ``stats()`` returns the canonical shape."""
    cache = MultiTierCache(l1_size=10, l2_size=100)
    stats = cache.stats()
    expected_keys = {"l1_size", "l1_max", "l2_size", "l2_max", "l3_size", "l3_volume"}
    assert expected_keys.issubset(set(stats.keys())), f"missing: {expected_keys - set(stats.keys())}"
    assert stats["l1_max"] == 10
    assert stats["l2_max"] == 100


# ---------------------------------------------------------------------------
# Back-compat surface (3 tests)
# ---------------------------------------------------------------------------


def test_shim_re_exports_multi_tier_cache_identity() -> None:
    """Back-compat: ``MultiTierCache`` from the shim IS the canonical class."""
    from thegent.infra.cache_v2 import MultiTierCache as ShimMTC

    assert ShimMTC is MultiTierCache


def test_shim_re_exports_get_cache_identity() -> None:
    """Back-compat: ``get_cache`` from the shim IS the canonical function."""
    from thegent.infra.cache_v2 import get_cache as shim_get_cache

    assert shim_get_cache is get_cache


def test_shim_class_source_file_is_split_target() -> None:
    """Back-compat: ``MultiTierCache`` source file is the post-split canonical module."""
    from thegent.infra.cache_v2 import MultiTierCache as ShimMTC

    src = inspect.getsourcefile(ShimMTC)
    assert src is not None
    assert src.endswith("/infra/cache/multi_tier.py"), (
        f"MultiTierCache source should be /infra/cache/multi_tier.py, got {src}"
    )


# ---------------------------------------------------------------------------
# AST purity (2 tests)
# ---------------------------------------------------------------------------


def test_shim_loc_is_within_target() -> None:
    """Back-compat shim LOC ≤ 35 (target ~30)."""
    from thegent.infra.cache_v2 import __file__ as shim_file

    content = Path(shim_file).read_text()
    loc = sum(1 for line in content.splitlines() if line.strip() and not line.lstrip().startswith("#"))
    assert loc <= 35, f"shim LOC = {loc}, expected ≤ 35"


def test_shim_contains_no_class_or_function_definitions() -> None:
    """Back-compat shim contains only re-exports (no ``class`` / ``def`` bodies)."""
    from thegent.infra.cache_v2 import __file__ as shim_file

    content = Path(shim_file).read_text()
    # Strip the future-import line which mentions "import" and "annotations"
    # but does not define a class or function. Then assert no class/def blocks.
    banned_markers = ("class ", "\ndef ", "    def ", "def get_cache", "async def ")
    for marker in banned_markers:
        assert marker not in content, f"shim must not contain '{marker}' — got: {content[:600]!r}"
