"""CLI surface for SOTA audit-replay tooling (Phase 3/4 hardening lane).

The ``thegent sota`` sub-app exposes a richer variant of
``thegent cockpit replay`` that SOTA audit tooling and CI pipelines
ingest directly.  Where ``cockpit replay`` is operator-focused (text
output, JSON envelope, 4 exit codes), ``sota replay`` adds:

* ``--snapshot-format`` — accept the expected-snapshot file in
  ``json`` (default), ``yaml``, or ``toml`` so operators can author
  snapshots in whichever format the upstream SOTA tooling emits.
* ``--report-format`` — emit the diff report as ``text`` (default),
  ``json``, or ``junitxml``.  ``junitxml`` produces a JUnit XML
  document (one ``<testcase>`` per corpus entry; ``<failure>`` on
  mismatch) so CI runners like Jenkins / GitHub Actions / Buildkite
  can ingest the report as a native test result.

The two commands share the same evaluation + compare pipeline
(``_build_batch_decision_log`` + ``_compare_decision``); only the
**inputs** and **report rendering** differ.  Keeping the
``cockpit replay`` CLI contract unchanged is part of the Phase 3/4
back-compat promise.

Exit codes match ``cockpit replay``:

* ``0`` — every decision matches.
* ``4`` — at least one mismatch.
* ``1`` — bad inputs.
* ``2`` — governance unavailable.
* ``3`` — at least one deny (also propagates as a mismatch in junitxml).
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path
from typing import Any, Optional

import typer

from .cli_cockpit import (
    _apply_snapshot_flip,
    _build_batch_decision_log,
    _compare_decision,
    _load_replay_snapshot,
    err_console,
)

app = typer.Typer(
    help="SOTA audit-replay tooling (Phase 3/4 hardening lane).",
    no_args_is_help=True,
    add_completion=False,
)


# A no-op callback forces Typer to keep ``app`` as a ``TyperGroup``
# even when only one sub-command (``replay``) is registered.  Without
# this, Typer collapses single-command apps into a ``TyperCommand``
# and ``runner.invoke(app, ["replay", ...])`` interprets the second
# ``replay`` as an extra positional argument.
@app.callback()
def _sota_root() -> None:
    """SOTA audit-replay tooling root (see ``replay`` sub-command)."""


# ---------------------------------------------------------------------------
# Snapshot-format dispatch
# ---------------------------------------------------------------------------


_SNAPSHOT_LOADERS: dict[str, Any] = {}


def _load_snapshot_json(path: Path) -> list[dict[str, Any]]:
    """JSON snapshot loader — delegates to the cockpit replay helper."""
    return _load_replay_snapshot(path)


def _load_snapshot_yaml(path: Path) -> list[dict[str, Any]]:
    """YAML snapshot loader.

    Accepted shapes mirror ``_load_replay_snapshot``:

    * a top-level list of decision dicts, or
    * a top-level object with a ``decisions`` key holding that list.

    Requires ``PyYAML`` (already a transitive dep of thegent).  If
    the import fails we surface a clean error to the operator
    instead of crashing mid-replay.
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "yaml snapshot-format requested but PyYAML is not installed. "
            "Install with `uv add pyyaml` or use --snapshot-format json."
        ) from exc
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("decisions"), list):
        return raw["decisions"]
    raise ValueError(f"yaml snapshot must be a list or an object with a 'decisions' key, got {type(raw).__name__}")


def _load_snapshot_toml(path: Path) -> list[dict[str, Any]]:
    """TOML snapshot loader (Python 3.11+ stdlib ``tomllib``).

    Accepted shapes mirror ``_load_replay_snapshot``.  Note that
    TOML's top level is always a dict, so the ``decisions`` key form
    is the natural representation; a bare list is rejected.
    """
    try:
        import tomllib  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - 3.11+ only
        raise RuntimeError(
            "toml snapshot-format requested but tomllib is not available (requires Python 3.11+)."
        ) from exc
    raw: Any = tomllib.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("decisions"), list):
        return raw["decisions"]
    raise ValueError(
        "toml snapshot must be an object with a 'decisions' key (TOML "
        "top level is always a table); got "
        f"{type(raw).__name__}"
    )


_SNAPSHOT_LOADERS["json"] = _load_snapshot_json
_SNAPSHOT_LOADERS["yaml"] = _load_snapshot_yaml
_SNAPSHOT_LOADERS["yml"] = _load_snapshot_yaml
_SNAPSHOT_LOADERS["toml"] = _load_snapshot_toml


# ---------------------------------------------------------------------------
# Report-format dispatch
# ---------------------------------------------------------------------------


def _render_report_text(
    *,
    items: int,
    matched: bool,
    mismatches: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    audit_path: Optional[str],
) -> str:
    """Plain-text report — identical contract to ``cockpit replay``."""
    out: list[str] = [f"sota replay: items={items} matched={matched} mismatches={len(mismatches)}"]
    for m in mismatches:
        out.append(m["text"])
    if audit_path:
        out.append(f"audit: {audit_path}")
    return "\n".join(out)


def _render_report_json(
    *,
    items: int,
    matched: bool,
    mismatches: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    audit_path: Optional[str],
) -> str:
    """JSON envelope — same shape as ``cockpit replay --json``."""
    return json.dumps(
        {
            "matched": matched,
            "items": items,
            "mismatches": [
                {
                    "index": m["index"],
                    "fields": m["fields"],
                    "expected": m["expected"],
                    "actual": m["actual"],
                }
                for m in mismatches
            ],
            "decisions": decisions,
            "audit": audit_path,
        },
        indent=2,
        sort_keys=True,
    )


def _render_report_junitxml(
    *,
    items: int,
    matched: bool,
    mismatches: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    audit_path: Optional[str],
    suite_name: str,
) -> str:
    """JUnit-XML report for CI ingestion.

    One ``<testcase>`` per corpus entry, named ``decision[i]``.
    On mismatch the testcase carries a ``<failure>`` element with
    the diff text.  Aggregate counters (``tests``, ``failures``,
    ``errors``) let CI runners show a single badge instead of
    parsing individual cases.

    The output is pretty-printed so operators can ``cat`` the
    report and read it; CI runners parse the XML, not the text, so
    the indentation is purely cosmetic.
    """
    testsuite = ET.Element(
        "testsuite",
        attrib={
            "name": suite_name,
            "tests": str(items),
            "failures": str(len(mismatches)),
            "errors": "0",
        },
    )
    # Index mismatches by ordinal for O(1) lookup.
    mismatch_by_idx: dict[int, dict[str, Any]] = {m["index"]: m for m in mismatches}

    for idx in range(items):
        case = ET.SubElement(
            testsuite,
            "testcase",
            attrib={
                "classname": suite_name,
                "name": f"decision[{idx}]",
            },
        )
        # Surface a short summary so CI logs show the verdict
        # without expanding the fullcase XML.
        if idx < len(decisions):
            verdict = decisions[idx].get("verdict", "unknown")
            rule_id = decisions[idx].get("rule_id") or "-"
            case.set("verdict", str(verdict))
            case.set("rule_id", str(rule_id))
        if idx in mismatch_by_idx:
            m = mismatch_by_idx[idx]
            failure = ET.SubElement(
                case,
                "failure",
                attrib={
                    "type": "policy_mismatch",
                    "message": f"decision[{idx}] mismatch on fields: {','.join(m['fields'])}",
                },
            )
            failure.text = m["text"]

    # Root-level <testsuites> wrapper so multiple suites can be
    # concatenated later if we add more reporters.
    testsuites = ET.Element(
        "testsuites",
        attrib={
            "name": suite_name,
            "tests": str(items),
            "failures": str(len(mismatches)),
            "errors": "0",
        },
    )
    testsuites.append(testsuite)

    raw = ET.tostring(testsuites, encoding="unicode")
    # Pretty-print so the report is human-readable; CI parsers handle
    # both compact and pretty-printed XML.
    # The input is ``raw`` (built by ``ET.tostring`` directly above) — not
    # operator-supplied data — so the standard-library ``minidom`` is
    # safe here.  ``S318`` is silenced with a scope comment.
    pretty = xml.dom.minidom.parseString(raw).toprettyxml(indent="  ")  # noqa: S318
    # Drop the XML declaration line; the CLI caller writes the
    # report to a file (or stdout) and we want the document to start
    # with ``<?xml ...?>`` from the stdlib, not a duplicate.
    pretty_lines = [line for line in pretty.splitlines() if line.strip()]
    return "\n".join(pretty_lines)


_REPORT_RENDERERS: dict[str, Any] = {
    "text": _render_report_text,
    "json": _render_report_json,
    "junitxml": _render_report_junitxml,
}


# ---------------------------------------------------------------------------
# thegent sota replay
# ---------------------------------------------------------------------------


@app.command(
    "replay",
    help=(
        "Replay a corpus against an expected PolicyDecision snapshot and emit "
        "a structured report (text / json / junitxml). SOTA audit hardening lane."
    ),
)
def sota_replay(
    batch: Path = typer.Option(
        ...,
        "--batch",
        help="Corpus of PolicyContext JSONs (file or dir of *.json).",
    ),
    compare: Path = typer.Option(
        ...,
        "--compare",
        help="Expected snapshot file (format controlled by --snapshot-format).",
    ),
    snapshot_format: str = typer.Option(
        "json",
        "--snapshot-format",
        help="Format of --compare: json, yaml, or toml.",
    ),
    report_format: str = typer.Option(
        "text",
        "--report-format",
        help="Output report format: text, json, or junitxml.",
    ),
    report_path: Optional[Path] = typer.Option(
        None,
        "--report-path",
        help="Write the report to this file (default: stdout).",
    ),
    audit_path: Optional[Path] = typer.Option(
        None,
        "--audit-path",
        help="Persist every replay decision to this JSONL file.",
    ),
    audit_append: bool = typer.Option(
        False,
        "--audit-append/--audit-overwrite",
        help="Append to the audit file (default: overwrite).",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--commit",
        help="Default dry-run; pass --commit to cache decisions in the engine.",
    ),
    namespace: str = typer.Option(
        "global",
        "--namespace",
        help="Federated policy namespace (pinned unless an entry declares its own).",
    ),
    default_policy: Optional[str] = typer.Option(
        None,
        "--default-policy",
        help="Enable federated policy lookup with this default namespace on --commit.",
    ),
    suite_name: str = typer.Option(
        "thegent.sota.replay",
        "--suite-name",
        help="JUnit-XML testsuite name (only used for junitxml report-format).",
    ),
    snapshot_flip: Optional[str] = typer.Option(
        None,
        "--snapshot-flip",
        help=(
            "SOTA canary workflow: invert the value of <field> on every entry of "
            "the loaded --compare snapshot in memory (e.g. 'verdict' or "
            "'override_applied') so the replay walks the mismatch path without "
            "the operator having to hand-edit the snapshot file. Useful for "
            "exercising the diff machinery + report formats + exit code 4 contract "
            "end-to-end on every CI run."
        ),
    ),
    _render_tail: bool = True,  # noqa: ANN001  - internal flag for cockpit shim
) -> None:
    """Replay ``--batch`` through pre-check and validate against ``--compare``.

    Unlike ``cockpit replay``, this command supports multi-format
    snapshot ingestion (json / yaml / toml) and structured report
    emission (text / json / junitxml) so SOTA tooling and CI
    pipelines can consume the diff natively.

    Exit codes match ``cockpit replay``:

    * ``0`` — every decision matches the expected snapshot.
    * ``4`` — at least one mismatch.
    * ``1`` — bad inputs (missing files, malformed snapshot, etc.).
    * ``2`` — governance unavailable.
    * ``3`` — at least one deny (propagates as a mismatch in junitxml).
    """
    snapshot_format_lc = snapshot_format.lower()
    if snapshot_format_lc not in _SNAPSHOT_LOADERS:
        err_console.print(
            f"[red]sota replay failed:[/red] unknown --snapshot-format {snapshot_format!r}; "
            f"supported: {sorted(_SNAPSHOT_LOADERS.keys())}"
        )
        raise typer.Exit(1)

    report_format_lc = report_format.lower()
    if report_format_lc not in _REPORT_RENDERERS:
        err_console.print(
            f"[red]sota replay failed:[/red] unknown --report-format {report_format!r}; "
            f"supported: {sorted(_REPORT_RENDERERS.keys())}"
        )
        raise typer.Exit(1)

    # Defer governance import so a missing module surfaces as exit 2.
    try:
        from ..governance.policy_engine import PolicyEngine
    except Exception as exc:  # pragma: no cover - import guard
        err_console.print(f"[red]governance unavailable:[/red] {exc}")
        raise typer.Exit(2) from exc

    try:
        if not batch.exists():
            err_console.print(f"[red]sota replay failed:[/red] batch path not found: {batch}")
            raise typer.Exit(1)
        if not compare.exists():
            err_console.print(f"[red]sota replay failed:[/red] compare path not found: {compare}")
            raise typer.Exit(1)

        try:
            expected_snapshot = _SNAPSHOT_LOADERS[snapshot_format_lc](compare)
        except (ValueError, RuntimeError) as exc:
            err_console.print(f"[red]sota replay failed:[/red] {exc}")
            raise typer.Exit(1) from exc
        except json.JSONDecodeError as exc:
            err_console.print(f"[red]sota replay failed:[/red] compare file is not valid JSON: {exc}")
            raise typer.Exit(1) from exc

        # SOTA canary workflow: ``--snapshot-flip <field>`` inverts the
        # named field on every snapshot entry **in memory** so the replay
        # walks the mismatch path without the operator having to
        # hand-edit the --compare file. The flag is honoured on every
        # snapshot format (json / yaml / toml) because the flip is
        # applied after the format loader returns.
        if snapshot_flip:
            expected_snapshot = _apply_snapshot_flip(expected_snapshot, snapshot_flip)

        use_federation = default_policy is not None
        contexts, decisions, notices = _build_batch_decision_log(
            batch=batch,
            engine_factory=lambda: PolicyEngine(
                use_federation=use_federation,
                default_namespace=default_policy or "global",
            ),
            use_engine=not dry_run,
            namespace_override=namespace,
        )
        if not contexts:
            # Mirror ``cockpit replay`` empty-corpus semantics.
            err_console.print(f"[yellow]sota replay batch is empty:[/yellow] {batch}")
            matched_empty = not expected_snapshot
            renderer = _REPORT_RENDERERS[report_format_lc]
            if report_format_lc == "junitxml":
                report = renderer(
                    items=0,
                    matched=matched_empty,
                    mismatches=[],
                    decisions=[],
                    audit_path=None,
                    suite_name=suite_name,
                )
            else:
                report = renderer(
                    items=0,
                    matched=matched_empty,
                    mismatches=[],
                    decisions=[],
                    audit_path=None,
                )
            if report_path is not None:
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(report, encoding="utf-8")
                typer.echo(f"sota replay: report written to {report_path}")
            else:
                typer.echo(report)
            if not matched_empty:
                raise typer.Exit(4)
            raise typer.Exit(0)

        produced = [d.to_dict() for d in decisions]
        mismatches: list[dict[str, Any]] = []
        max_len = max(len(produced), len(expected_snapshot))
        for idx in range(max_len):
            exp = expected_snapshot[idx] if idx < len(expected_snapshot) else None
            act = produced[idx] if idx < len(produced) else None
            if exp is None or act is None:
                mismatches.append(
                    {
                        "index": idx,
                        "fields": ["length"],
                        "expected": exp,
                        "actual": act,
                        "text": (f"mismatch[{idx}]: length expected={len(expected_snapshot)} actual={len(produced)}"),
                    }
                )
                continue
            diff_fields = _compare_decision(exp, act)
            if diff_fields:
                mismatches.append(
                    {
                        "index": idx,
                        "fields": diff_fields,
                        "expected": exp,
                        "actual": act,
                        "text": _format_sota_mismatch(idx, exp, act, diff_fields),
                    }
                )

        # Persist decisions via the same appender pattern as
        # ``cockpit replay`` so the JSONL shape stays identical.
        audit_str: Optional[str] = None
        if audit_path is not None:
            from .decision_audit import DecisionAuditAppender

            appender = DecisionAuditAppender(audit_path=audit_path)
            if not audit_append:
                p = appender.audit_path()
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("", encoding="utf-8")
            appender.record_many(notices)
            audit_str = str(appender.audit_path())

        matched = not mismatches
        renderer = _REPORT_RENDERERS[report_format_lc]
        if report_format_lc == "junitxml":
            report = renderer(
                items=len(produced),
                matched=matched,
                mismatches=mismatches,
                decisions=produced,
                audit_path=audit_str,
                suite_name=suite_name,
            )
        else:
            report = renderer(
                items=len(produced),
                matched=matched,
                mismatches=mismatches,
                decisions=produced,
                audit_path=audit_str,
            )
        if report_path is not None:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report, encoding="utf-8")
            typer.echo(f"sota replay: report written to {report_path}")
        else:
            typer.echo(report)

        # Always print the cockpit-style envelope to stdout too,
        # so operator terminals see the same "matched=N mismatches=M"
        # line regardless of the report format. This keeps the
        # cockpit vs sota UX consistent.
        if _render_tail:
            typer.echo(f"sota replay: matched={matched} items={len(produced)} mismatches={len(mismatches)}")

        if not matched:
            raise typer.Exit(4)
    except typer.Exit:
        raise
    except Exception as exc:
        err_console.print(f"[red]sota replay failed:[/red] {exc}")
        raise typer.Exit(1) from exc


def _format_sota_mismatch(
    idx: int,
    expected: Optional[dict[str, Any]],
    actual: Optional[dict[str, Any]],
    diff_fields: list[str],
) -> str:
    """Stable text format for one mismatch row (mirrors ``cockpit replay``)."""
    if expected is None and actual is not None:
        return f"mismatch[{idx}]: produced entry has no matching expected entry"
    if actual is None and expected is not None:
        return f"mismatch[{idx}]: expected entry has no matching produced entry"
    if expected is None or actual is None:  # pragma: no cover - defensive
        return f"mismatch[{idx}]: <unknown diff>"
    parts: list[str] = []
    for field in diff_fields:
        exp_val = expected.get(field)
        act_val = actual.get(field)
        parts.append(f"{field} expected={exp_val} actual={act_val}")
    if not parts:
        parts.append("snapshot differs but no tracked field mismatched")
    return f"mismatch[{idx}]: " + " ".join(parts)


def main() -> None:  # pragma: no cover - convenience entry point
    """Module-level entry point so ``python -m thegent.ux.cli_sota`` works."""
    if len(sys.argv) == 1:
        typer.echo(app.get_help())
        return
    app()


__all__ = ["app", "sota_replay"]


if __name__ == "__main__":  # pragma: no cover
    main()
