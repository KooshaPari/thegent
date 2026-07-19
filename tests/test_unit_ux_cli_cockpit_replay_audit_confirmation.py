"""Direct tests for ``cockpit replay`` audit-mode confirmation line.

Operators that re-run replay nightly against the same snapshot need a
deterministic signal about whether the audit trail was preserved
(``--audit-append``) or zeroed (``--audit-overwrite``). Without an
explicit confirmation line, a CI harness that toggles the flag
accidentally will silently truncate the previous run's audit history.

This suite pins:

* The new ``replay: audit=… mode=append|overwrite lines=N`` confirmation
  line is emitted on the text-mode path only.
* ``--audit-append`` reports ``mode=append``; the default
  ``--audit-overwrite`` reports ``mode=overwrite``.
* The line is suppressed in ``--json`` mode so structured-output
  consumers don't see it as noise.
* The confirmation is suppressed when ``--audit-path`` is omitted
  (no audit file was written; no confirmation to emit).
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from thegent.ux.cli_cockpit import app


def _write_batch(path: Path) -> None:
    """Write a 2-context batch file the cockpit replay CLI will accept."""
    contexts = [
        {
            "agent": "cursor",
            "model": "",
            "lane": "standard",
            "confidence": 0.95,
            "environment": "development",
            "namespace": "global",
            "prompt": "",
            "cost_usd": 0.0,
            "metadata": {},
        },
        {
            "agent": "cursor",
            "model": "",
            "lane": "standard",
            "confidence": 0.95,
            "environment": "development",
            "namespace": "global",
            "prompt": "",
            "cost_usd": 0.0,
            "metadata": {},
        },
    ]
    path.write_text(json.dumps(contexts), encoding="utf-8")


def _write_compare(path: Path, *, allow: bool = True) -> None:
    """Write a compare snapshot matching the 2-context batch above."""
    if allow:
        # Match the 2 batch items so the replay is a clean match.
        decisions = [
            {
                "verdict": "allow",
                "reason": "allowed by local policy",
                "reason_code": "allowed",
                "rule_id": "local.default.allow",
                "override_applied": False,
                "cached": False,
                "evaluated_at": 0.0,
            },
            {
                "verdict": "allow",
                "reason": "allowed by local policy",
                "reason_code": "allowed",
                "rule_id": "local.default.allow",
                "override_applied": False,
                "cached": False,
                "evaluated_at": 0.0,
            },
        ]
    else:
        decisions = []
    path.write_text(json.dumps(decisions), encoding="utf-8")


# ---------------------------------------------------------------------------
# Text-mode confirmation
# ---------------------------------------------------------------------------


class TestReplayAuditConfirmationText:
    """Text mode emits ``replay: audit=… mode=… lines=…``."""

    def test_overwrite_mode_default(self, tmp_path: Path) -> None:
        """Default ``--audit-overwrite`` reports ``mode=overwrite``."""
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        audit = tmp_path / "audit.jsonl"
        _write_batch(batch)
        _write_compare(compare, allow=True)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--audit-path",
                str(audit),
            ],
        )
        assert result.exit_code == 0, result.output
        assert f"audit={audit}" in result.output
        assert "mode=overwrite" in result.output
        assert "lines=2" in result.output

    def test_append_mode_explicit(self, tmp_path: Path) -> None:
        """``--audit-append`` reports ``mode=append`` and preserves prior bytes."""
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        audit = tmp_path / "audit.jsonl"
        # Pre-seed the audit file with a sentinel byte so we can
        # assert append vs overwrite behaviour on disk.
        audit.write_text('{"sentinel": true}\n', encoding="utf-8")
        _write_batch(batch)
        _write_compare(compare, allow=True)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--audit-path",
                str(audit),
                "--audit-append",
            ],
        )
        assert result.exit_code == 0, result.output
        assert f"audit={audit}" in result.output
        assert "mode=append" in result.output
        # The pre-seeded sentinel must still be present (append).
        on_disk = audit.read_text(encoding="utf-8")
        assert '"sentinel": true' in on_disk
        assert "lines=2" in result.output

    def test_overwrite_truncates_prior_bytes(self, tmp_path: Path) -> None:
        """Default ``--audit-overwrite`` zeros prior bytes (the documented semantics)."""
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        audit = tmp_path / "audit.jsonl"
        audit.write_text('{"sentinel": true}\n', encoding="utf-8")
        _write_batch(batch)
        _write_compare(compare, allow=True)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--audit-path",
                str(audit),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "mode=overwrite" in result.output
        on_disk = audit.read_text(encoding="utf-8")
        assert '"sentinel": true' not in on_disk


# ---------------------------------------------------------------------------
# JSON-mode suppression
# ---------------------------------------------------------------------------


class TestReplayAuditConfirmationJson:
    """``--json`` mode suppresses the confirmation line."""

    def test_json_mode_omits_audit_confirmation(self, tmp_path: Path) -> None:
        """Structured-output consumers don't see the human confirmation line."""
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        audit = tmp_path / "audit.jsonl"
        _write_batch(batch)
        _write_compare(compare, allow=True)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--audit-path",
                str(audit),
                "--json",
            ],
        )
        assert result.exit_code == 0, result.output
        # Structured envelope is present.
        parsed = json.loads(result.output)
        assert parsed["matched"] is True
        # Confirmation line must NOT pollute the JSON output.
        assert "mode=overwrite" not in result.output
        assert "mode=append" not in result.output


# ---------------------------------------------------------------------------
# No audit path = no confirmation
# ---------------------------------------------------------------------------


class TestReplayNoAuditPath:
    """When ``--audit-path`` is omitted, no audit work happens and no line is emitted."""

    def test_no_audit_path_no_confirmation(self, tmp_path: Path) -> None:
        """Without ``--audit-path`` there's no confirmation line."""
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        _write_compare(compare, allow=True)

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "audit=" not in result.output
        assert "mode=overwrite" not in result.output
        assert "mode=append" not in result.output
