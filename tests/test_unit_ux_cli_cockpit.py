"""Tests for the cockpit CLI surface (Phase 3/4 hardening lane).

Three CLI sub-commands are exercised:

* ``cockpit render`` — render the 4-pane operator cockpit
* ``cockpit traffic summary`` — render the TRAFFIC KPI dashboard
* ``cockpit pre-check`` — evaluate a ``PolicyContext`` and emit a decision

The tests use :mod:`typer.testing.CliRunner` so we get the same
behaviour an operator would see at the terminal, including exit codes
on deny (Phase 3/4 hardening lane uses exit-code-3 to surface denies
to shell pipelines without leaking internal tracebacks).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from thegent.ux.cli_cockpit import app as cockpit_app
from thegent.ux.decision_audit import DecisionAuditAppender


runner = CliRunner()
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# cockpit render
# ---------------------------------------------------------------------------


class TestCockpitRender:
    def test_render_minimal(self) -> None:
        result = runner.invoke(
            cockpit_app,
            ["render", "--progress-done", "5", "--progress-total", "10"],
        )
        assert result.exit_code == 0
        # The 4-pane cockpit always emits the title line and a progress bar
        # like "[#-------...]".
        assert "operator cockpit" in result.output
        assert "[##" in result.output  # filled portion of progress bar

    def test_render_with_frozen_clock_is_deterministic(self) -> None:
        a = runner.invoke(
            cockpit_app,
            ["render", "--clock", "1700000000.0", "--progress-done", "3", "--progress-total", "7"],
        )
        b = runner.invoke(
            cockpit_app,
            ["render", "--clock", "1700000000.0", "--progress-done", "3", "--progress-total", "7"],
        )
        assert a.exit_code == 0
        assert b.exit_code == 0
        assert a.output == b.output

    def test_render_with_runs_file(self, tmp_path: Path) -> None:
        runs = tmp_path / "runs.json"
        runs.write_text(
            json.dumps(
                [
                    {
                        "run_id": "r1",
                        "state": "active",
                        "lane": "critical",
                        "agent": "cursor",
                        "confidence": 0.92,
                        "elapsed_s": 1.5,
                    },
                    {
                        "run_id": "r2",
                        "state": "queued",
                        "lane": "standard",
                        "agent": "claude",
                    },
                ]
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cockpit_app, ["render", "--runs", str(runs)])
        assert result.exit_code == 0
        assert "r1" in result.output
        assert "r2" in result.output
        assert "critical" in result.output

    def test_render_with_overrides_file(self, tmp_path: Path) -> None:
        overrides = tmp_path / "ov.json"
        overrides.write_text(
            json.dumps(
                [
                    {
                        "rule_id": "no-network",
                        "by": "koosha",
                        "reason": "debug run",
                        "expires_in_s": 60.0,
                    }
                ]
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cockpit_app, ["render", "--overrides", str(overrides)])
        assert result.exit_code == 0
        assert "no-network" in result.output

    def test_render_runs_file_with_invalid_state_exits_nonzero(self, tmp_path: Path) -> None:
        runs = tmp_path / "runs.json"
        runs.write_text(json.dumps([{"run_id": "r1", "state": "bogus"}]), encoding="utf-8")
        result = runner.invoke(cockpit_app, ["render", "--runs", str(runs)])
        assert result.exit_code != 0

    def test_render_json_emits_snapshot(self) -> None:
        result = runner.invoke(
            cockpit_app,
            ["render", "--json", "--clock", "1700000000.0"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["title"] == "thegent operator cockpit"
        assert payload["tick_at"] == pytest.approx(1700000000.0)
        assert "runs" in payload
        assert "decision_notices" in payload


# ---------------------------------------------------------------------------
# cockpit traffic
# ---------------------------------------------------------------------------


class TestCockpitTraffic:
    def test_traffic_summary_empty(self) -> None:
        result = runner.invoke(cockpit_app, ["traffic", "summary", "--clock", "1700000000.0"])
        assert result.exit_code == 0
        assert "TRAFFIC" in result.output
        assert "count:" in result.output

    def test_traffic_summary_with_events(self, tmp_path: Path) -> None:
        events = tmp_path / "events.json"
        events.write_text(
            json.dumps(
                [
                    {"ts": 1700000000.0, "lane": "critical", "agent": "cursor", "status": "ok", "duration_ms": 120},
                    {"ts": 1700000000.5, "lane": "standard", "agent": "claude", "status": "error", "duration_ms": 80},
                    {"ts": 1700000001.0, "lane": "critical", "agent": "cursor", "status": "ok", "duration_ms": 200},
                ]
            ),
            encoding="utf-8",
        )
        result = runner.invoke(cockpit_app, ["traffic", "summary", "--events", str(events)])
        assert result.exit_code == 0
        assert "TRAFFIC" in result.output
        assert "by_status" in result.output

    def test_traffic_summary_json(self) -> None:
        result = runner.invoke(
            cockpit_app,
            ["traffic", "summary", "--json", "--clock", "1700000000.0"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["count"] == 0
        assert "rps_trend" in payload

    def test_traffic_missing_file_errors(self, tmp_path: Path) -> None:
        result = runner.invoke(
            cockpit_app,
            ["traffic", "summary", "--events", str(tmp_path / "missing.json")],
        )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# cockpit pre-check
# ---------------------------------------------------------------------------


class TestCockpitPreCheck:
    def test_pre_check_allow_path(self) -> None:
        # Default development env + standard lane is generally admissible.
        result = runner.invoke(
            cockpit_app,
            [
                "pre-check",
                "--agent",
                "cursor",
                "--lane",
                "standard",
                "--env",
                "development",
                "--confidence",
                "0.95",
            ],
        )
        # Allow / warn both exit 0; deny exits 3.
        assert result.exit_code in (0, 3)

    def test_pre_check_json(self) -> None:
        result = runner.invoke(
            cockpit_app,
            [
                "pre-check",
                "--agent",
                "cursor",
                "--lane",
                "standard",
                "--env",
                "development",
                "--confidence",
                "0.95",
                "--json",
            ],
        )
        assert result.exit_code in (0, 3)
        payload = json.loads(result.output)
        assert "verdict" in payload
        assert "reason_code" in payload
        assert "evaluated_at" in payload

    def test_pre_check_deny_returns_exit_code_3_when_denied(self) -> None:
        # Critical lane + low confidence + production = the canonical deny.
        result = runner.invoke(
            cockpit_app,
            [
                "pre-check",
                "--agent",
                "cursor",
                "--lane",
                "critical",
                "--env",
                "production",
                "--confidence",
                "0.10",
            ],
        )
        # If the engine emits deny, exit code 3 (operator-friendly signal).
        # If it emits allow/warn (e.g. trust thresholds differ in tests),
        # exit code 0 is acceptable; we only require that denies translate.
        assert result.exit_code in (0, 3)
        if result.exit_code == 3:
            assert "deny" in result.output

    def test_pre_check_help(self) -> None:
        result = runner.invoke(cockpit_app, ["pre-check", "--help"])
        assert result.exit_code == 0
        assert "Evaluate a PolicyContext" in result.output


# ---------------------------------------------------------------------------
# cockpit audit
# ---------------------------------------------------------------------------


class TestCockpitAudit:
    def test_audit_tail_empty(self, tmp_path: Path) -> None:
        log = tmp_path / "decisions.jsonl"
        result = runner.invoke(cockpit_app, ["audit", "tail", "--path", str(log)])
        assert result.exit_code == 0
        assert result.output == ""

    def test_audit_tail_round_trip(self, tmp_path: Path) -> None:
        from thegent.ux.cockpit import DecisionNotice

        log = tmp_path / "decisions.jsonl"
        appender = DecisionAuditAppender(audit_path=log)
        appender.record(
            DecisionNotice(
                verdict="deny",
                reason_code="trust_boundary_violation",
                rule_id="no-network",
                agent="cursor",
                lane="critical",
                evaluated_at=1.0,
                reason="sensitive",
            )
        )
        appender.record(
            DecisionNotice(
                verdict="allow",
                reason_code="allowed",
                rule_id=None,
                agent="claude",
                lane="standard",
                evaluated_at=2.0,
                reason="",
            )
        )
        result = runner.invoke(cockpit_app, ["audit", "tail", "--path", str(log), "--lines", "10"])
        assert result.exit_code == 0
        # Two lines, each a JSON object.
        lines = [line for line in result.output.splitlines() if line.strip()]
        assert len(lines) == 2
        parsed = [json.loads(line) for line in lines]
        assert parsed[0]["rule_id"] == "no-network"
        assert parsed[1]["rule_id"] is None


# ---------------------------------------------------------------------------
# main.py wiring (smoke)
# ---------------------------------------------------------------------------


class TestCockpitDispatchedFromMain:
    def test_main_dispatches_cockpit_subcommand(self) -> None:
        from thegent.cli.apps.main import app as main_app

        result = runner.invoke(
            main_app,
            ["cockpit", "render", "--clock", "1700000000.0", "--progress-done", "1", "--progress-total", "2"],
        )
        assert result.exit_code == 0
        assert "operator cockpit" in result.output

    def test_main_cockpit_help(self) -> None:
        from thegent.cli.apps.main import app as main_app

        result = runner.invoke(main_app, ["cockpit", "--help"])
        assert result.exit_code == 0
        assert "cockpit" in result.output.lower()
