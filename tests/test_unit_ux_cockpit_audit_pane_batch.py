"""Tests for the operator cockpit's audit wiring + decision-history pane + CLI batch.

These tests cover the third iteration of the Phase 3/4 hardening lane:

1. ``OperatorCockpit(audit_appender=..., auto_tail=True)`` — production
   deployments get free JSONL persistence for every
   :meth:`record_decision` call without manual wiring, and the cockpit
   owns / stops the background :class:`DecisionAuditTailer` via
   :meth:`shutdown`.
2. The new decision-history pane appears at the bottom of the cockpit
   render with verdict glyph, rule_id, agent, lane, age, and reason
   code. It mirrors the existing override-history UX (different stream).
3. ``thegent cockpit pre-check --batch <path>`` replays a JSON corpus
   (file or directory of ``*.json``) and persists a combined audit
   log; deny verdicts surface via exit code ``3`` so shell pipelines
   can react.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from thegent.ux.cli_cockpit import app, _load_pre_check_corpus
from thegent.ux.cockpit import (
    DecisionNotice,
    MAX_DECISION_PANE_ROWS,
    OperatorCockpit,
    _decision_glyph,
    _format_decision_row,
)
from thegent.ux.decision_audit import DecisionAuditAppender, DecisionAuditTailer


pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FrozenClock:
    """Mutable wall-clock callable for deterministic replays."""

    def __init__(self, start: float = 1_700_000_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make_notice(
    *,
    verdict: str = "deny",
    rule_id: str = "no-network",
    agent: str = "cursor",
    lane: str = "critical",
    evaluated_at: float = 0.0,
) -> DecisionNotice:
    return DecisionNotice(
        verdict=verdict,
        reason_code="trust_boundary_violation",
        rule_id=rule_id,
        agent=agent,
        lane=lane,
        evaluated_at=evaluated_at,
        reason="",
    )


# ---------------------------------------------------------------------------
# 1. OperatorCockpit(audit_appender=..., auto_tail=...) wiring
# ---------------------------------------------------------------------------


class TestOperatorCockpitAuditAppenderWiring:
    """``audit_appender`` + ``auto_tail`` constructor wiring + lifecycle."""

    def test_default_constructor_has_no_appender(self, tmp_path: Path) -> None:
        # Default construction is unchanged: no appender / no background threads.
        cockpit = OperatorCockpit()
        assert cockpit.audit_appender() is None
        assert cockpit._audit_tailer is None  # noqa: SLF001
        cockpit.shutdown()

    def test_constructor_accepts_appender_without_auto_tail(self, tmp_path: Path) -> None:
        # Supplying an appender without ``auto_tail`` keeps the cockpit
        # synchronous (tests and short scripts can opt in explicitly).
        log = tmp_path / "decisions.jsonl"
        appender = DecisionAuditAppender(audit_path=log)
        cockpit = OperatorCockpit(audit_appender=appender)
        assert cockpit.audit_appender() is appender
        # No tailer spawned -> drain is the caller's responsibility.
        assert cockpit._audit_tailer is None  # noqa: SLF001
        cockpit.shutdown()

    def test_auto_tail_spins_up_background_drainer(self, tmp_path: Path) -> None:
        log = tmp_path / "decisions.jsonl"
        appender = DecisionAuditAppender(audit_path=log)
        cockpit = OperatorCockpit(
            audit_appender=appender,
            auto_tail=True,
            tail_interval_s=0.05,
        )
        try:
            assert cockpit._audit_tailer is not None  # noqa: SLF001
            assert isinstance(  # noqa: SLF001
                cockpit._audit_tailer,
                DecisionAuditTailer,  # noqa: SLF001
            )
            cockpit.record_decision(
                _make_notice(evaluated_at=time.time()),
            )
            # Poll for file existence (the drain thread may not have
            # materialised the file when this test starts) AND for
            # non-zero size; using a bare ``log.stat()`` here would
            # raise FileNotFoundError on slow runners.
            deadline = time.time() + 5.0
            while time.time() < deadline:
                try:
                    if log.stat().st_size > 0:
                        break
                except FileNotFoundError:
                    pass
                time.sleep(0.05)
            tail = appender.tail_events(n=10)
            assert len(tail) == 1
            assert tail[0]["rule_id"] == "no-network"
        finally:
            cockpit.shutdown(timeout_s=2.0)

    def test_shutdown_is_idempotent_and_stops_tailer(self, tmp_path: Path) -> None:
        log = tmp_path / "decisions.jsonl"
        appender = DecisionAuditAppender(audit_path=log)
        cockpit = OperatorCockpit(
            audit_appender=appender,
            auto_tail=True,
            tail_interval_s=0.05,
        )
        tailer = cockpit._audit_tailer  # noqa: SLF001
        assert tailer is not None
        first_thread = tailer._thread  # noqa: SLF001
        assert first_thread is not None
        assert first_thread.is_alive()
        # Shutdown twice — second call must be a no-op (idempotent).
        cockpit.shutdown(timeout_s=2.0)
        cockpit.shutdown(timeout_s=2.0)
        assert cockpit._audit_tailer is None  # noqa: SLF001
        # Tailer thread exits within the timeout.
        first_thread.join(timeout=2.0)
        assert not first_thread.is_alive()

    def test_context_manager_stops_tailer(self, tmp_path: Path) -> None:
        log = tmp_path / "decisions.jsonl"
        appender = DecisionAuditAppender(audit_path=log)
        thread_ref: dict[str, threading.Thread | None] = {"t": None}
        with OperatorCockpit(
            audit_appender=appender,
            auto_tail=True,
            tail_interval_s=0.05,
        ) as cockpit:
            thread_ref["t"] = cockpit._audit_tailer._thread  # noqa: SLF001
            assert thread_ref["t"] is not None
        # ``with`` exit triggers shutdown; thread should be gone.
        assert thread_ref["t"] is not None
        thread_ref["t"].join(timeout=2.0)  # noqa: SLF001
        assert not thread_ref["t"].is_alive()  # noqa: SLF001

    def test_frozen_clock_propagates_through_auto_tail(self, tmp_path: Path) -> None:
        # Determinism: the cockpit's injected clock determines
        # ``emitted_at`` JSONL stamps when the appender's clock is the
        # same callable, so SOTA replay tooling can reproduce a run.
        log = tmp_path / "decisions.jsonl"
        clk = _FrozenClock(start=1_700_000_000.0)
        appender = DecisionAuditAppender(audit_path=log, clock=clk)
        cockpit = OperatorCockpit(
            audit_appender=appender,
            auto_tail=True,
            tail_interval_s=0.05,
            clock=clk,
        )
        try:
            cockpit.record_decision(
                _make_notice(evaluated_at=clk.now),
            )
            deadline = time.time() + 5.0
            while time.time() < deadline:
                try:
                    if log.stat().st_size > 0:
                        break
                except FileNotFoundError:
                    pass
                time.sleep(0.05)
            tail = appender.tail_events(n=5)
            assert len(tail) == 1
            assert tail[0]["emitted_at"] == pytest.approx(1_700_000_000.0)
        finally:
            cockpit.shutdown(timeout_s=2.0)


# ---------------------------------------------------------------------------
# 2. Decision-history pane
# ---------------------------------------------------------------------------


class TestDecisionHistoryPane:
    """The new full-width decision-history pane (WP-3001 -> WP-4001)."""

    def test_empty_decision_history_renders_neutral_pane(self) -> None:
        cockpit = OperatorCockpit()
        rendered = cockpit.render()
        # Always present in the rendered output, even when there are no
        # recorded notices.
        assert "Decision History" in rendered
        assert "(no policy decisions recorded yet)" in rendered
        cockpit.shutdown()

    def test_single_deny_renders_with_ballot_x_glyph(self) -> None:
        clk = _FrozenClock(start=1_700_000_000.0)
        cockpit = OperatorCockpit(clock=clk)
        try:
            cockpit.record_decision(_make_notice(verdict="deny", rule_id="crit.lane", evaluated_at=clk.now))
            rendered = cockpit.render()
            assert "Decision History" in rendered
            # Glyph + rule_id present.
            assert "\u2717 crit.lane" in rendered
        finally:
            cockpit.shutdown()

    def test_allow_uses_check_mark(self) -> None:
        cockpit = OperatorCockpit(clock=_FrozenClock())
        try:
            cockpit.record_decision(
                _make_notice(
                    verdict="allow",
                    rule_id="std.allow",
                    lane="standard",
                    evaluated_at=time.time(),
                )
            )
            rendered = cockpit.render()
            assert "\u2713 std.allow" in rendered
        finally:
            cockpit.shutdown()

    def test_warn_uses_bang(self) -> None:
        cockpit = OperatorCockpit(clock=_FrozenClock())
        try:
            cockpit.record_decision(
                _make_notice(
                    verdict="warn",
                    rule_id="cost.warn",
                    lane="standard",
                    evaluated_at=time.time(),
                )
            )
            rendered = cockpit.render()
            assert "! cost.warn" in rendered
        finally:
            cockpit.shutdown()

    def test_zero_evaluated_at_renders_dash_glyph(self) -> None:
        cockpit = OperatorCockpit()
        try:
            # No clock provided; ``evaluated_at`` stays 0.
            cockpit.record_decision(_make_notice(verdict="allow"))
            rendered = cockpit.render()
            assert "-" in rendered
            # The pane shows the placeholder age when the notice hasn't
            # been clocked yet.
            assert "   -" in rendered
        finally:
            cockpit.shutdown()

    def test_pane_respects_max_rows_with_ellipsis(self) -> None:
        clk = _FrozenClock(start=1_700_000_000.0)
        cockpit = OperatorCockpit(clock=clk)
        try:
            for i in range(MAX_DECISION_PANE_ROWS + 3):
                cockpit.record_decision(
                    _make_notice(
                        verdict="allow",
                        rule_id=f"rule.{i:03d}",
                        evaluated_at=clk.now,
                    )
                )
            rendered = cockpit.render()
            assert "older decisions hidden" in rendered
        finally:
            cockpit.shutdown()

    def test_decision_glyph_helper_classifies_verdicts(self) -> None:
        assert _decision_glyph(_make_notice(verdict="deny")) == "\u2717"
        assert _decision_glyph(_make_notice(verdict="warn")) == "!"
        assert _decision_glyph(_make_notice(verdict="allow", evaluated_at=1.0)) == "\u2713"
        # No clock yet -> dash (no fake age).
        assert _decision_glyph(_make_notice(verdict="allow", evaluated_at=0.0)) == "-"

    def test_format_decision_row_layout_is_stable(self) -> None:
        notice = _make_notice(
            verdict="allow",
            rule_id="std.allow",
            agent="cursor",
            lane="standard",
            evaluated_at=1_700_000_000.0,
        )
        row = _format_decision_row(notice, age=12.0)
        # Columns in order: rule_id, agent, lane, age, reason_code.
        assert row.startswith("std.allow")
        assert "cursor" in row
        assert "standard" in row
        assert "12s" in row
        # ``reason_code`` is truncated to 16 chars by the formatter;
        # assert the prefix so the test does not depend on the
        # truncation policy.
        assert "trust_boundary" in row


# ---------------------------------------------------------------------------
# 3. ``cockpit pre-check --batch`` (SOTA replay corpus)
# ---------------------------------------------------------------------------


class TestPreCheckBatchCLI:
    """``thegent cockpit pre-check --batch`` replay tooling."""

    def test_batch_file_overwrite_audit_default(self, tmp_path: Path) -> None:
        corpus = tmp_path / "corpus.json"
        corpus.write_text(
            json.dumps(
                [
                    {
                        "agent": "cursor",
                        "lane": "critical",
                        "confidence": 0.5,
                        "environment": "production",
                    },
                    {
                        "agent": "cursor",
                        "lane": "standard",
                        "confidence": 0.95,
                        "environment": "development",
                    },
                ]
            )
        )
        audit = tmp_path / "audit.jsonl"
        # Pre-seed with stale content to prove overwrite semantics.
        audit.write_text('{"stale":true}\n')
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["pre-check", "--batch", str(corpus), "--audit-path", str(audit)],
        )
        # The corpus contains a deny (critical lane + low confidence),
        # so the command must surface exit code 3.
        assert result.exit_code == 3, result.output
        assert "pre-check batch: items=2 deny=True" in result.output
        lines = audit.read_text().strip().splitlines()
        # Overwrite: only the two fresh decisions remain.
        assert len(lines) == 2
        joined = "\n".join(lines)
        assert "stale" not in joined
        assert '"verdict":"deny"' in joined
        assert '"verdict":"allow"' in joined

    def test_batch_file_append_audit_keeps_prior_lines(self, tmp_path: Path) -> None:
        corpus = tmp_path / "corpus.json"
        corpus.write_text(
            json.dumps(
                [
                    {
                        "agent": "cursor",
                        "lane": "standard",
                        "confidence": 0.9,
                        "environment": "development",
                    }
                ]
            )
        )
        audit = tmp_path / "audit.jsonl"
        audit.write_text('{"prior":"line"}\n')
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "pre-check",
                "--batch",
                str(corpus),
                "--audit-path",
                str(audit),
                "--audit-append",
            ],
        )
        assert result.exit_code == 0
        lines = audit.read_text().strip().splitlines()
        assert any('"prior":"line"' in line for line in lines)
        assert any('"verdict":"allow"' in line for line in lines)
        assert len(lines) == 2

    def test_batch_directory_globs_json_files(self, tmp_path: Path) -> None:
        d = tmp_path / "corpus"
        d.mkdir()
        (d / "a.json").write_text(
            json.dumps(
                [
                    {
                        "agent": "a",
                        "lane": "standard",
                        "confidence": 0.9,
                        "environment": "development",
                    }
                ]
            )
        )
        (d / "b.json").write_text(
            json.dumps(
                [
                    {
                        "agent": "b",
                        "lane": "critical",
                        "confidence": 0.1,
                        "environment": "production",
                    }
                ]
            )
        )
        # Non-JSON files are ignored.
        (d / "README.txt").write_text("skip me")
        audit = tmp_path / "audit.jsonl"
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["pre-check", "--batch", str(d), "--audit-path", str(audit)],
        )
        # Critical lane + low confidence + production -> deny.
        assert result.exit_code == 3
        lines = audit.read_text().strip().splitlines()
        assert len(lines) == 2
        agents = {json.loads(line)["agent"] for line in lines}
        assert agents == {"a", "b"}

    def test_batch_single_context_object_in_file(self, tmp_path: Path) -> None:
        # Single JSON object (not a list) is also accepted.
        corpus = tmp_path / "single.json"
        corpus.write_text(
            json.dumps(
                {
                    "agent": "cursor",
                    "lane": "standard",
                    "confidence": 0.95,
                    "environment": "development",
                }
            )
        )
        audit = tmp_path / "audit.jsonl"
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["pre-check", "--batch", str(corpus), "--audit-path", str(audit)],
        )
        assert result.exit_code == 0
        lines = audit.read_text().strip().splitlines()
        assert len(lines) == 1
        assert '"verdict":"allow"' in lines[0]

    def test_batch_empty_corpus_reports_quietly(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.json"
        empty.write_text("[]")
        runner = CliRunner()
        result = runner.invoke(app, ["pre-check", "--batch", str(empty)])
        # Empty corpus is a no-op success; no deny => exit 0.
        assert result.exit_code == 0
        assert "pre-check batch is empty" in result.output

    def test_batch_missing_path_surfaces_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.json"
        runner = CliRunner()
        result = runner.invoke(app, ["pre-check", "--batch", str(missing)])
        assert result.exit_code == 1
        assert "not found" in result.output or "nope" in result.output

    def test_load_corpus_rejects_non_object_entries(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps([123, 456]))
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "pre-check",
                "--batch",
                str(bad),
                "--audit-path",
                str(tmp_path / "audit.jsonl"),
            ],
        )
        # Bad entries surface a useful error and exit code 1.
        assert result.exit_code == 1
        assert "must be objects" in result.output


class TestLoadPreCheckCorpus:
    """Direct unit tests for the corpus loader (no CLI round-trip)."""

    def test_load_file_list(self, tmp_path: Path) -> None:
        p = tmp_path / "x.json"
        p.write_text(json.dumps([{"agent": "a"}, {"agent": "b"}]))
        out = _load_pre_check_corpus(p)
        assert [c.agent for c in out] == ["a", "b"]

    def test_load_file_single_object(self, tmp_path: Path) -> None:
        p = tmp_path / "x.json"
        p.write_text(json.dumps({"agent": "x", "lane": "standard"}))
        out = _load_pre_check_corpus(p)
        assert len(out) == 1
        assert out[0].agent == "x"

    def test_load_directory_concatenates(self, tmp_path: Path) -> None:
        d = tmp_path / "c"
        d.mkdir()
        (d / "1.json").write_text(json.dumps([{"agent": "1"}]))
        (d / "2.json").write_text(json.dumps({"agent": "2"}))
        out = _load_pre_check_corpus(d)
        assert sorted(c.agent for c in out) == ["1", "2"]

    def test_missing_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _load_pre_check_corpus(tmp_path / "missing")
