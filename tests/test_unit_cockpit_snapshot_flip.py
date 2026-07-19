"""``--snapshot-flip`` SOTA canary workflow tests.

Pins the WORKLOG "Unblocked Next" #3 lane: the ``--snapshot-flip
<field>`` flag on both ``cockpit replay`` and ``sota replay`` must
deliberately invert the named field on every loaded snapshot entry so
the replay walks the mismatch path **without the operator having to
hand-edit the ``--compare`` file on disk**.

Coverage scope (deliberately narrow):

* ``verdict`` field — flips ``allow`` ↔ ``deny`` so exit code 4 fires.
* ``override_applied`` field — bool negation; mismatch must be
  recorded on that field.
* Unknown field — best-effort inversion still produces a mismatch
  row, so the canary catches drift in the diff machinery.
* ``--snapshot-flip`` propagates through the cockpit→sota shim
  (``cockpit replay --report-format json --snapshot-flip ...`` must
  exercise the same envelope contract as ``sota replay``).
* The ``--compare`` file on disk is **not** mutated by the flag — we
  hash it before+after to prove the canary is purely in-memory.

Mirror images the ``flip=True`` fixture pattern in
``tests/test_unit_cockpit_sota_json_parity.py`` but asserts the flag
end-to-end through the Typer CLI surface.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from thegent.ux.cli_cockpit import app as cockpit_app
from thegent.ux.cli_sota import app as sota_app


# Per-mismatch sub-keys the JSON envelope MUST expose — shared with the
# parity suite so we don't drift the contract across files.
_MISMATCH_SUBKEYS: tuple[str, ...] = ("index", "fields", "expected", "actual")


def _write_batch(path: Path) -> None:
    """Write a 2-context batch the cockpit/sota replay CLIs accept."""
    context = {
        "agent": "cursor",
        "model": "",
        "lane": "standard",
        "confidence": 0.95,
        "environment": "development",
        "namespace": "global",
        "prompt": "",
        "cost_usd": 0.0,
        "metadata": {},
    }
    path.write_text(json.dumps([context, dict(context)]), encoding="utf-8")


def _harvest_decisions(runner: CliRunner, corpus: Path) -> list[dict]:
    """Run ``cockpit pre-check --batch --json`` and collect produced decisions."""
    result = runner.invoke(
        cockpit_app,
        ["pre-check", "--batch", str(corpus), "--json"],
    )
    assert result.exit_code in (0, 3), result.output  # 3 == at least one deny
    decoder = json.JSONDecoder()
    decisions: list[dict] = []
    text = result.output
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text) or text[idx] != "{":
            break
        obj, end = decoder.raw_decode(text[idx:])
        decisions.append(obj)
        idx += end
    assert decisions, f"no decisions harvested from pre-check output: {text!r}"
    return decisions


def _write_snapshot(decisions: list[dict], path: Path) -> None:
    """Persist a snapshot of decisions verbatim."""
    path.write_text(json.dumps(decisions), encoding="utf-8")


def _sha256(path: Path) -> str:
    """Return the SHA-256 hash of ``path``'s bytes — proves the flag is in-memory only."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_last_json_object(text: str) -> dict:
    """Return the last balanced JSON object embedded in ``text``."""
    decoder = json.JSONDecoder()
    last_obj: dict | None = None
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text) or text[idx] != "{":
            break
        obj, end = decoder.raw_decode(text[idx:])
        last_obj = obj
        idx += end
    assert last_obj is not None, f"no JSON object found in output: {text!r}"
    return last_obj


# ---------------------------------------------------------------------------
# cockpit replay --snapshot-flip
# ---------------------------------------------------------------------------


class TestCockpitReplaySnapshotFlip:
    """``cockpit replay --snapshot-flip <field>`` forces the mismatch path."""

    def test_snapshot_flip_verdict_forces_mismatch(self, tmp_path: Path) -> None:
        """Flipping ``verdict`` on every entry walks the mismatch path."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)
        before_hash = _sha256(compare)

        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-flip",
                "verdict",
            ],
        )
        assert result.exit_code == 4, result.output
        assert "matched=False" in result.output
        assert "verdict" in result.output
        # ``--compare`` file on disk MUST be left untouched.
        assert _sha256(compare) == before_hash, "snapshot-flip must not mutate --compare"

    def test_snapshot_flip_verdict_json_envelope_shows_mismatch(self, tmp_path: Path) -> None:
        """``cockpit replay --snapshot-flip verdict --json`` emits matched=False envelope."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)

        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-flip",
                "verdict",
                "--json",
            ],
        )
        assert result.exit_code == 4, result.output
        envelope = json.loads(result.output.strip())
        assert envelope["matched"] is False
        assert envelope["mismatches"], "expected at least one mismatch row"
        for row in envelope["mismatches"]:
            assert set(row.keys()) >= set(_MISMATCH_SUBKEYS)
            assert "verdict" in row["fields"]

    def test_snapshot_flip_override_applied_forces_mismatch(self, tmp_path: Path) -> None:
        """Bool negation on ``override_applied`` still triggers exit code 4."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)

        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-flip",
                "override_applied",
            ],
        )
        # If the engine's ``override_applied`` is uniformly False (likely
        # in a baseline corpus) the flip to True MUST disagree.
        assert result.exit_code == 4, result.output
        assert "matched=False" in result.output

    def test_no_snapshot_flip_still_matches(self, tmp_path: Path) -> None:
        """Without the flag the existing happy-path contract is unchanged."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)

        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "matched=True" in result.output

    def test_snapshot_flip_unknown_field_still_records_mismatch(self, tmp_path: Path) -> None:
        """A non-compare-table field still walks the mismatch path via the sentinel."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)

        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-flip",
                "reason",
            ],
        )
        # ``reason`` is whitespace-tolerant in ``_compare_decision``, but
        # the flip emits ``<flipped:...>`` so the post-strip strings
        # disagree. Exit 4 + matched=False.
        assert result.exit_code == 4, result.output
        assert "matched=False" in result.output
        assert "reason" in result.output


# ---------------------------------------------------------------------------
# sota replay --snapshot-flip (direct + via cockpit shim)
# ---------------------------------------------------------------------------


class TestSotaReplaySnapshotFlip:
    """``sota replay --snapshot-flip <field>`` honours the same contract."""

    def test_sota_snapshot_flip_via_shim_propagates_flag(self, tmp_path: Path) -> None:
        """Cockpit shim must forward ``--snapshot-flip`` to sota replay."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)
        before_hash = _sha256(compare)

        # This invocation exercises the shim path: ``--report-format json``
        # is non-default, so ``cockpit replay`` defers to ``sota replay``
        # while forwarding ``--snapshot-flip`` transparently.
        result = runner.invoke(
            cockpit_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-flip",
                "verdict",
                "--report-format",
                "json",
            ],
        )
        assert result.exit_code == 4, result.output
        envelope = _extract_last_json_object(result.output)
        assert envelope["matched"] is False
        assert envelope["mismatches"], "expected at least one mismatch row"
        for row in envelope["mismatches"]:
            assert set(row.keys()) >= set(_MISMATCH_SUBKEYS)
            assert "verdict" in row["fields"]
        # The cockpit-side shim must NOT mutate the snapshot file.
        assert _sha256(compare) == before_hash, "shim must not mutate --compare"

    def test_sota_replay_direct_snapshot_flip_json(self, tmp_path: Path) -> None:
        """``sota replay --snapshot-flip verdict --report-format json`` direct call."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)

        result = runner.invoke(
            sota_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-format",
                "json",
                "--report-format",
                "json",
                "--snapshot-flip",
                "verdict",
            ],
        )
        assert result.exit_code == 4, result.output
        envelope = _extract_last_json_object(result.output)
        assert envelope["matched"] is False
        assert envelope["mismatches"], "expected at least one mismatch row"
        assert all("verdict" in row["fields"] for row in envelope["mismatches"])

    def test_sota_replay_snapshot_flip_junitxml_records_failure(self, tmp_path: Path) -> None:
        """The JUnit-XML report-format emits a ``<failure>`` on every flipped entry."""
        runner = CliRunner()
        batch = tmp_path / "batch.json"
        compare = tmp_path / "compare.json"
        _write_batch(batch)
        decisions = _harvest_decisions(runner, batch)
        _write_snapshot(decisions, compare)
        report = tmp_path / "report.xml"

        result = runner.invoke(
            sota_app,
            [
                "replay",
                "--batch",
                str(batch),
                "--compare",
                str(compare),
                "--snapshot-format",
                "json",
                "--report-format",
                "junitxml",
                "--report-path",
                str(report),
                "--snapshot-flip",
                "verdict",
            ],
        )
        assert result.exit_code == 4, result.output
        xml_text = report.read_text(encoding="utf-8")
        assert "<failure" in xml_text, xml_text
        # Every decision produced by the corpus becomes a testcase; on
        # mismatch at least one carries a ``<failure>`` element.
        assert xml_text.count("<testcase") >= 2
        assert xml_text.count("<failure") >= 1


# ---------------------------------------------------------------------------
# In-process helper coverage
# ---------------------------------------------------------------------------


class TestSnapshotFlipHelpers:
    """Direct coverage of the ``_apply_snapshot_flip`` / ``_invert_snapshot_value`` helpers."""

    def test_invert_verdict_allow_to_deny(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        assert _invert_snapshot_value("verdict", "allow") == "deny"

    def test_invert_verdict_deny_to_allow(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        assert _invert_snapshot_value("verdict", "deny") == "allow"

    def test_invert_verdict_warn_collapses_to_deny(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        # ``warn`` flips to ``deny`` so the canary always disagrees.
        assert _invert_snapshot_value("verdict", "warn") == "deny"

    def test_invert_override_applied_bool_negation(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        assert _invert_snapshot_value("override_applied", True) is False
        assert _invert_snapshot_value("override_applied", False) is True

    def test_invert_override_applied_string_bool_coercion(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        # yaml/toml snapshots sometimes ship bools as strings.
        assert _invert_snapshot_value("override_applied", "true") is False
        assert _invert_snapshot_value("override_applied", "false") is True

    def test_invert_none_is_noop(self) -> None:
        from thegent.ux.cli_cockpit import _invert_snapshot_value

        assert _invert_snapshot_value("verdict", None) is None

    def test_apply_snapshot_flip_returns_copy(self) -> None:
        from thegent.ux.cli_cockpit import _apply_snapshot_flip

        original = [{"verdict": "allow", "rule_id": "r1"}]
        flipped = _apply_snapshot_flip(original, "verdict")
        assert flipped == [{"verdict": "deny", "rule_id": "r1"}]
        # Original list must NOT be mutated.
        assert original[0]["verdict"] == "allow"

    def test_apply_snapshot_flip_empty_field_returns_input(self) -> None:
        from thegent.ux.cli_cockpit import _apply_snapshot_flip

        original = [{"verdict": "allow"}]
        assert _apply_snapshot_flip(original, "") is original

    def test_apply_snapshot_flip_skips_non_dict_entries(self) -> None:
        from thegent.ux.cli_cockpit import _apply_snapshot_flip

        snapshot = [{"verdict": "allow"}, "not-a-dict", 42, {"verdict": "deny"}]
        flipped = _apply_snapshot_flip(snapshot, "verdict")
        assert flipped[0]["verdict"] == "deny"
        assert flipped[1] == "not-a-dict"
        assert flipped[2] == 42
        assert flipped[3]["verdict"] == "allow"
