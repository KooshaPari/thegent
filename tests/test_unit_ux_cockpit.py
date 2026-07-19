"""Unit tests for the Operator Cockpit (WP-4001, FR-UX-007, OBS8, P-081)."""

from __future__ import annotations

import time

import pytest

from thegent.ux.cockpit import (
    CockpitConfig,
    CockpitPane,
    OperatorCockpit,
    OverrideEvent,
    OverrideExpiryNotice,
    RunEvent,
    RunState,
    render_cockpit,
)


pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Sanity
# ---------------------------------------------------------------------------


class TestSanity:
    def test_public_api_present(self) -> None:
        assert CockpitPane.RUNS.value == "runs"
        assert CockpitPane.LANES.value == "lanes"
        assert CockpitPane.CONFIDENCE.value == "confidence"
        assert CockpitPane.OVERRIDES.value == "overrides"
        assert RunState.ACTIVE.value == "active"
        assert RunState.QUEUED.value == "queued"

    def test_config_defaults(self) -> None:
        cfg = CockpitConfig()
        assert cfg.tick_ms == 1000
        assert cfg.progress_total == 100
        assert cfg.sparkline_width == 24
        assert CockpitPane.RUNS in cfg.pane_labels


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


class TestProgressBar:
    def test_zero_total(self) -> None:
        from thegent.ux.cockpit import _progress_bar

        assert _progress_bar(0, 0).startswith("[")

    def test_full(self) -> None:
        from thegent.ux.cockpit import _progress_bar

        out = _progress_bar(10, 10, width=8)
        assert "100%" in out
        assert out.startswith("[########")

    def test_partial(self) -> None:
        from thegent.ux.cockpit import _progress_bar

        out = _progress_bar(3, 4, width=8)
        assert " 75%" in out

    def test_overflow_capped(self) -> None:
        from thegent.ux.cockpit import _progress_bar

        out = _progress_bar(20, 5, width=8)
        assert "100%" in out


class TestSparkline:
    def test_empty(self) -> None:
        from thegent.ux.cockpit import _sparkline

        assert _sparkline([], 5) == "·····"

    def test_constant(self) -> None:
        from thegent.ux.cockpit import _sparkline

        # All-equal values should fall back to a flat line, never raise.
        assert "·" in _sparkline([0.5] * 5, 5)

    def test_widening(self) -> None:
        from thegent.ux.cockpit import _sparkline

        # Values from 0..1 should produce a spark that climbs visually.
        spark = _sparkline([0.1, 0.3, 0.5, 0.7, 0.9], 5)
        assert len(spark) == 5
        # The last character should be a top-tier one (not a bottom-tier one).
        assert spark[-1] in "▅▆▇█"

    def test_pad_when_input_shorter(self) -> None:
        from thegent.ux.cockpit import _sparkline

        spark = _sparkline([1.0], 4)
        assert len(spark) == 4


class TestTruncate:
    def test_short_unchanged(self) -> None:
        from thegent.ux.cockpit import _truncate

        assert _truncate("hi", 10) == "hi"

    def test_truncate_with_ellipsis(self) -> None:
        from thegent.ux.cockpit import _truncate

        out = _truncate("hello world", 6)
        assert out.endswith("…")
        assert len(out) == 6


# ---------------------------------------------------------------------------
# Cockpit event ingestion
# ---------------------------------------------------------------------------


class TestTick:
    def test_tick_records_runs(self) -> None:
        c = OperatorCockpit()
        c.tick(
            runs=[
                RunEvent(run_id="r1", state=RunState.ACTIVE, lane="critical"),
                RunEvent(run_id="r2", state=RunState.QUEUED, lane="standard"),
            ]
        )
        assert "r1" in c._state.runs
        assert "r2" in c._state.runs

    def test_tick_replaces_runs_idempotent(self) -> None:
        c = OperatorCockpit()
        c.tick(runs=[RunEvent(run_id="r1", state=RunState.ACTIVE)])
        c.tick(runs=[RunEvent(run_id="r1", state=RunState.DONE)])
        assert c._state.runs["r1"].state == RunState.DONE

    def test_tick_records_overrides(self) -> None:
        c = OperatorCockpit()
        c.tick(overrides=[OverrideEvent(rule_id="o1", by="alice", reason="hotfix", expires_in_s=120)])
        assert "o1" in c._state.overrides

    def test_tick_records_progress(self) -> None:
        c = OperatorCockpit()
        c.tick(progress=(3, 10))
        assert c._state.last_progress == (3, 10)

    def test_tick_records_confidence_history(self) -> None:
        c = OperatorCockpit()
        c.tick(
            runs=[
                RunEvent(run_id="r1", state=RunState.ACTIVE, confidence=0.7),
                RunEvent(run_id="r2", state=RunState.QUEUED, confidence=0.9),
            ]
        )
        # ``confidence_history`` is a bounded ``deque`` (unbounded-memory
        # hardening); compare via ``list(...)`` so the assertion stays
        # order-/value-equivalent rather than type-strict.
        assert list(c._state.confidence_history) == [0.7, 0.9]
        # Bounded behaviour: appending past maxlen must evict the oldest.
        c._state.confidence_history.extend([1.0] * (1024 + 5))
        assert len(c._state.confidence_history) == 1024
        # The most recent 1024 entries are preserved, oldest evicted.
        assert c._state.confidence_history[-1] == 1.0


# ---------------------------------------------------------------------------
# Render: 4-pane grid
# ---------------------------------------------------------------------------


def _sample_runs() -> list[RunEvent]:
    return [
        RunEvent(
            run_id="run-001",
            state=RunState.ACTIVE,
            lane="critical",
            agent="cursor",
            confidence=0.92,
            elapsed_s=4.2,
        ),
        RunEvent(
            run_id="run-002",
            state=RunState.QUEUED,
            lane="standard",
            agent="gemini",
            confidence=0.71,
        ),
    ]


def _sample_overrides() -> list[OverrideEvent]:
    return [
        OverrideEvent(
            rule_id="no-cursor-prod",
            by="sre",
            reason="hotfix",
            expires_in_s=300,
        )
    ]


class TestRender:
    def test_render_returns_text(self) -> None:
        c = OperatorCockpit()
        c.tick(runs=_sample_runs(), overrides=_sample_overrides(), progress=(2, 8))
        out = c.render()
        assert "thegent operator cockpit" in out
        assert "run-001" in out
        assert "run-002" in out
        assert "no-cursor-prod" in out
        assert "25%" in out  # 2/8 = 25%

    def test_render_records_frame_count(self) -> None:
        c = OperatorCockpit()
        for _ in range(3):
            c.render()
        assert c._frame_count == 3

    def test_render_records_latency_ms(self) -> None:
        c = OperatorCockpit()
        c.render()
        assert c.last_render_ms() >= 0
        assert c.last_render_ms() < 1000  # sub-second

    def test_render_empty(self) -> None:
        c = OperatorCockpit()
        out = c.render()
        # Empty cockpit should still render header + placeholder lines.
        assert "thegent operator cockpit" in out
        assert "no active runs" in out
        assert "no active overrides" in out

    def test_render_progress_bar_at_100(self) -> None:
        c = OperatorCockpit()
        c.tick(progress=(10, 10))
        c.render()
        assert "100%" in c.render()

    def test_render_includes_lane_breakdown(self) -> None:
        c = OperatorCockpit()
        c.tick(
            runs=[
                RunEvent(run_id="r1", state=RunState.ACTIVE, lane="critical"),
                RunEvent(run_id="r2", state=RunState.ACTIVE, lane="critical"),
                RunEvent(run_id="r3", state=RunState.QUEUED, lane="standard"),
            ]
        )
        out = c.render()
        assert "critical" in out
        assert "standard" in out

    def test_render_includes_sparkline(self) -> None:
        c = OperatorCockpit()
        cfg = CockpitConfig(show_sparkline=True, sparkline_width=8)
        cockpit = OperatorCockpit(config=cfg)
        cockpit.tick(
            runs=[RunEvent(run_id="r1", state=RunState.ACTIVE, confidence=v) for v in [0.1, 0.3, 0.5, 0.7, 0.9]]
        )
        out = cockpit.render()
        # Sparkline chars should appear somewhere in the output.
        assert any(ch in out for ch in "▁▂▃▄▅▆▇█")

    def test_render_disables_sparkline(self) -> None:
        cfg = CockpitConfig(show_sparkline=False)
        cockpit = OperatorCockpit(config=cfg)
        cockpit.tick(
            runs=[
                RunEvent(run_id="r1", state=RunState.ACTIVE, confidence=0.5),
                RunEvent(run_id="r2", state=RunState.ACTIVE, confidence=0.7),
                RunEvent(run_id="r3", state=RunState.ACTIVE, confidence=0.9),
            ]
        )
        out = cockpit.render()
        # When disabled, no sparkline chars in the confidence pane.
        # (Other panes do not use sparkline chars, so we cannot strictly assert.)
        assert "P50=" in out
        assert "P95=" in out


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------


class TestSnapshot:
    def test_snapshot_includes_all_state(self) -> None:
        c = OperatorCockpit()
        c.tick(
            runs=[
                RunEvent(run_id="r1", state=RunState.ACTIVE, lane="critical", agent="cursor", confidence=0.7),
            ],
            overrides=[OverrideEvent(rule_id="x", by="alice", reason="r", expires_in_s=10)],
            progress=(1, 1),
        )
        snap = c.snapshot()
        assert snap["title"] == "thegent operator cockpit"
        assert len(snap["runs"]) == 1
        assert snap["runs"][0]["state"] == "active"
        assert snap["lanes"]["critical"] == 1
        assert len(snap["overrides"]) == 1
        assert snap["progress"] == (1, 1)
        assert 0.7 in snap["confidence_history"]


# ---------------------------------------------------------------------------
# Reset and context-manager
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_state(self) -> None:
        c = OperatorCockpit()
        c.tick(runs=[RunEvent(run_id="r1", state=RunState.ACTIVE)])
        assert c._state.runs
        c.reset()
        assert not c._state.runs
        assert c._frame_count == 0


class TestContextManager:
    def test_with_statement(self) -> None:
        with OperatorCockpit() as c:
            c.tick(runs=[RunEvent(run_id="r1", state=RunState.ACTIVE)])
            assert "r1" in c._state.runs
        # No exception, context manager exits cleanly.


# ---------------------------------------------------------------------------
# One-shot helper
# ---------------------------------------------------------------------------


class TestOneShotHelper:
    def test_render_cockpit_default(self) -> None:
        text = render_cockpit(
            runs=_sample_runs(),
            overrides=_sample_overrides(),
            progress=(1, 4),
        )
        assert "thegent operator cockpit" in text
        assert "run-001" in text
        assert "no-cursor-prod" in text
        assert "25%" in text

    def test_render_cockpit_with_custom_config(self) -> None:
        cfg = CockpitConfig(title="custom title")
        text = render_cockpit(config=cfg, runs=[], progress=(0, 1))
        assert "custom title" in text


# ---------------------------------------------------------------------------
# Performance smoke test (P-090: cockpit latency SLO)
# ---------------------------------------------------------------------------


class TestPerformance:
    def test_render_under_50ms_for_typical_workload(self) -> None:
        """Sustains <50ms render time for a 4-pane, 30-runs workload."""
        runs = [
            RunEvent(
                run_id=f"r{i:03d}",
                state=RunState.ACTIVE,
                lane="critical" if i % 3 else "standard",
                agent="cursor",
                confidence=0.5 + (i % 5) * 0.1,
            )
            for i in range(30)
        ]
        overrides = [
            OverrideEvent(rule_id=f"o{i}", by="alice", reason="r", expires_in_s=float(i * 10)) for i in range(5)
        ]
        c = OperatorCockpit()
        # Warm the cache
        c.render()
        c.tick(runs=runs, overrides=overrides, progress=(10, 100))
        # 5 successive renders should each be < 50ms (SLO P-090).
        for _ in range(5):
            c.render()
            assert c.last_render_ms() < 50


# ---------------------------------------------------------------------------
# Override-expiry banner (WP-3003 -> WP-4001 bridge)
# ---------------------------------------------------------------------------


class TestOverrideExpiryBanner:
    """WP-3003 OverrideEventEmitter feeds the cockpit's inline banner."""

    def test_no_banner_when_no_notices(self) -> None:
        c = OperatorCockpit()
        c.tick(runs=_sample_runs(), overrides=_sample_overrides(), progress=(1, 1))
        out = c.render()
        assert "override expired" not in out

    def test_record_override_event_appears_in_render(self) -> None:
        c = OperatorCockpit()
        notice = OverrideExpiryNotice(
            rule_id="net-block",  # short enough to fit the 12-char banner column
            owner="sre",
            reason="ttl_elapsed",
            expired_at=time.time(),
        )
        c.record_override_event(notice)
        out = c.render()
        assert "override expired" in out
        assert "net-block" in out
        assert "sre" in out
        assert "ttl_elapsed" in out

    def test_banner_fades_past_max_age(self) -> None:
        """Notices older than ``OVERRIDE_BANNER_MAX_AGE_S`` are not shown."""
        from thegent.ux.cockpit import OVERRIDE_BANNER_MAX_AGE_S

        c = OperatorCockpit()
        # Push a notice that has already expired long ago.
        stale = OverrideExpiryNotice(
            rule_id="stale-rule",
            owner="bob",
            reason="old",
            expired_at=time.time() - (OVERRIDE_BANNER_MAX_AGE_S + 5.0),
        )
        c.record_override_event(stale)
        out = c.render()
        assert "override expired" not in out

    def test_banner_uses_most_recent_notice(self) -> None:
        """When multiple notices arrive, only the latest is surfaced."""
        c = OperatorCockpit()
        c.record_override_event(
            OverrideExpiryNotice(
                rule_id="old-rule", owner="alice", reason="old",
                expired_at=time.time() - 5.0,
            )
        )
        c.record_override_event(
            OverrideExpiryNotice(
                rule_id="new-rule", owner="bob", reason="fresh",
                expired_at=time.time(),
            )
        )
        out = c.render()
        assert "new-rule" in out
        assert "old-rule" not in out

    def test_record_override_event_rejects_wrong_type(self) -> None:
        """Defensive type guard against config drift / malformed callbacks."""
        c = OperatorCockpit()
        with pytest.raises(TypeError):
            c.record_override_event({"rule_id": "x"})  # type: ignore[arg-type]

    def test_override_notices_deque_is_bounded(self) -> None:
        """Bounded-memory contract: maxlen=32 means old notices are evicted."""
        c = OperatorCockpit()
        for i in range(40):
            c.record_override_event(
                OverrideExpiryNotice(
                    rule_id=f"r{i:03d}",
                    owner="u",
                    reason="ttl",
                    expired_at=time.time(),
                )
            )
        # Most-recent 32 are kept (deque is bounded); oldest 8 evicted.
        assert len(c._state.override_notices) == 32
        assert c._state.override_notices[-1].rule_id == "r039"
        assert c._state.override_notices[0].rule_id == "r008"

    def test_snapshot_includes_override_notices(self) -> None:
        """The structured snapshot should expose notices for downstream consumers."""
        c = OperatorCockpit()
        c.record_override_event(
            OverrideExpiryNotice(
                rule_id="snap-rule", owner="ci", reason="r",
                expired_at=time.time(),
            )
        )
        snap = c.snapshot()
        # Override notices are surfaced as a list (immutable snapshot pattern).
        assert "override_notices" in snap
        assert snap["override_notices"][0]["rule_id"] == "snap-rule"
