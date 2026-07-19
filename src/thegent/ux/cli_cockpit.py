"""CLI surface for the operator cockpit (WP-4001), traffic KPIs (WP-Y7),
and policy pre-checks (WP-3001).

Four Typer sub-commands expose the Phase 3/4 governance+UX lane to
operators running outside the TUI:

* ``thegent cockpit render`` — render the 4-pane operator cockpit for a
  snapshot of runs / overrides (deterministic when ``--clock`` is set).
* ``thegent cockpit traffic`` — render the TRAFFIC KPI dashboard to stdout
  (also deterministic with ``--clock``).
* ``thegent cockpit pre-check`` — evaluate a :class:`PolicyContext` against
  the governance :class:`PolicyEngine` and emit the resulting
  :class:`PolicyDecision` as either human-readable text or JSON.
* ``thegent cockpit replay`` — replay a corpus of ``PolicyContext`` JSONs
  through pre-check and validate the resulting decisions against an
  expected snapshot line-by-line (Phase 3/4 SOTA hardening lane, third
  "Unblocked Next" item from ``WORKLOG.md``).

Each subcommand is intentionally side-effect-free: rendering does not
mutate cockpit state, and ``pre-check`` defaults to ``--dry-run`` so
operators can rehearse decisions without polluting the policy cache.

These commands complete the WORKLOG.md "Unblocked Next" backlog for the
Phase 3/4 hardening lane and give SOTA audit tooling a stable CLI
contract.

------------------------------------------------------------------------
Operator walkthrough: ``--json`` + ``--report-format=junitxml`` ingestion
------------------------------------------------------------------------

SOTA replay tooling can consume replay output three ways. The three
shapes are guaranteed-stable so CI harnesses can switch between them
without rewriting parsers:

1. ``cockpit replay --json`` (default snapshot format, JSON envelope)::

       thegent cockpit replay --batch corpus/ --compare snapshot.json --json

   Emits a single JSON object on stdout with keys ``matched`` (bool),
   ``mismatches`` (list of ``{index, fields, expected, actual}`` dicts),
   ``decisions`` (the produced :class:`PolicyDecision` list), and
   ``audit`` (the JSONL path written when ``--audit-path`` is set).
   Suitable for ``jq``-based pipelines::

       thegent cockpit replay --batch corpus/ --compare snap.json --json \\
           | jq '.matched, .mismatches | length'

2. ``cockpit replay --report-format=json`` (delegated to sota replay)::

       thegent cockpit replay --batch corpus/ --compare snap.json \\
           --report-format=json

   Same envelope **shape** (matched / mismatches keys present, mismatches
   list shape stable) — see
   ``tests/test_unit_cockpit_sota_json_parity.py`` for the parity
   contract. Use this when you want the sota-side report-format
   dispatch table to win (handy when wiring into a sota-wide ingest
   pipeline that already routes by ``--report-format``).

3. ``cockpit replay --report-format=junitxml`` (CI-friendly)::

       thegent cockpit replay --batch corpus/ --compare snap.json \\
           --report-format=junitxml --report-path report.xml

   Emits JUnit-XML so Jenkins / GitHub Actions / Buildkite can ingest
   the replay as a test suite. Each mismatch becomes a ``<failure>``
   entry; a clean replay becomes a passing ``<testsuite>``. The
   ``--report-path`` flag routes the XML to disk; omit it to print to
   stdout (handy for ``tee`` into a build log).

Replay exits ``0`` on match, ``4`` on mismatch (mirrors the
``pre-check`` ``3 = deny`` convention but kept distinct so shell
pipelines can branch on the two failure modes independently). For
structured ingestion prefer ``--json`` over text-grepping the default
output — the text path is intended for humans only.

------------------------------------------------------------------------
Operator walkthrough: ``--snapshot-flip`` SOTA canary workflow
------------------------------------------------------------------------

The ``--snapshot-flip <field>`` flag is a SOTA canary knob: it
deliberately inverts one field on every loaded snapshot entry **in
memory** so the replay walks the mismatch path without the operator
having to hand-edit the ``--compare`` file. This is useful for CI
runs that want to exercise the diff machinery + JSON envelope + exit
code 4 contract end-to-end on every replay (rather than only when a
real regression happens to land).

Supported fields and their invert semantics:

* ``verdict`` — ``allow`` ↔ ``deny``; ``warn`` and unknown verdicts
  flip to ``deny`` (always disagrees with the engine's actual verdict).
* ``override_applied`` / ``cached`` — bool negation (with
  string-bool coercion so yaml/toml snapshots still invert cleanly).
* any other field — best-effort bool/numeric inversion, or a stable
  ``<flipped:<value>>`` string sentinel so the compare step still
  records a mismatch.

Example::

    # Force a mismatch on every entry's ``verdict`` so the replay
    # exercise the exit-4 + diff machinery end-to-end. The
    # ``--compare`` file on disk is left untouched.
    thegent cockpit replay --batch corpus/ --compare snap.json \\
        --snapshot-flip verdict --json | jq '.matched, .mismatches'

The same flag is honoured by ``thegent sota replay`` (it is forwarded
through the cockpit→sota shim transparently) so a single canary
invocation exercises the diff path on every supported report format
(``--json``, ``--junitxml``) without rewriting the snapshot.
"""

from __future__ import annotations

import json
import time
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import typer
from rich.console import Console

from .cockpit import (
    DecisionNotice,
    OperatorCockpit,
    OverrideEvent,
    RunEvent,
    RunState,
    render_cockpit,
)
from .decision_audit import DecisionAuditAppender
from .kpis.traffic import TrafficDashboard, TrafficEvent, render_traffic

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    help="Operator cockpit + traffic KPI + policy pre-check surface (WP-3001/WP-4001/WP-Y7).",
    no_args_is_help=True,
)


def _resolve_clock(epoch: Optional[float]) -> Callable[[], float]:
    """Build a deterministic clock callable from ``--clock <epoch>``.

    ``None`` means use wall-clock (``time.time``), which is the right
    default for live operator runs. SOTA replay tooling passes an
    explicit epoch to lock every render to a fixed timeline.
    """
    if epoch is None:
        import time as _time

        return _time.time
    pinned = float(epoch)

    def _clock() -> float:
        return pinned

    return _clock


# ---------------------------------------------------------------------------
# cockpit render
# ---------------------------------------------------------------------------


@app.command("render", help="Render the 4-pane operator cockpit to stdout.")
def cockpit_render(
    runs_json: Optional[Path] = typer.Option(
        None,
        "--runs",
        help="JSON file with [{run_id, state, lane, agent, confidence, elapsed_s}]",
    ),
    overrides_json: Optional[Path] = typer.Option(
        None,
        "--overrides",
        help="JSON file with [{rule_id, by, reason, expires_in_s}]",
    ),
    progress_done: int = typer.Option(0, "--progress-done", help="Done count for header bar"),
    progress_total: int = typer.Option(100, "--progress-total", help="Total count for header bar"),
    clock: Optional[float] = typer.Option(
        None,
        "--clock",
        help="Pin wall clock (epoch seconds) for deterministic replay",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit snapshot JSON instead of text"),
) -> None:
    """Render the 4-pane operator cockpit (WP-4001, FR-UX-007, P-081)."""
    try:
        runs = _load_runs(runs_json)
        overrides = _load_overrides(overrides_json)
        clock_fn = _resolve_clock(clock)
        if json_output:
            # JSON mode needs the live cockpit object (not the one-shot
            # helper) so snapshot() picks up the injected clock.
            live = OperatorCockpit(clock=clock_fn)
            live.tick(runs=runs, overrides=overrides, progress=(progress_done, progress_total))
            typer.echo(json.dumps(live.snapshot(), indent=2, sort_keys=True))
            return
        typer.echo(
            render_cockpit(
                runs=runs,
                overrides=overrides,
                progress=(progress_done, progress_total),
                clock=clock_fn,
            )
        )
    except Exception as exc:
        err_console.print(f"[red]cockpit render failed:[/red] {exc}")
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# cockpit traffic
# ---------------------------------------------------------------------------


traffic_app = typer.Typer(
    help="TRAFFIC KPI dashboard (WP-Y7, OPS-001/002/003, P-081).",
    no_args_is_help=True,
)


@traffic_app.command("summary", help="Render a TRAFFIC KPI snapshot to stdout.")
def cockpit_traffic_summary(
    events_json: Optional[Path] = typer.Option(
        None,
        "--events",
        help="JSON file with [{ts, lane, agent, status, duration_ms, override_active}]",
    ),
    window_s: float = typer.Option(60.0, "--window", help="Window length in seconds"),
    clock: Optional[float] = typer.Option(
        None,
        "--clock",
        help="Pin wall clock (epoch seconds) for deterministic replay",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit summary JSON instead of text"),
) -> None:
    """Render the TRAFFIC KPI dashboard from a (possibly empty) event log."""
    try:
        clock_fn = _resolve_clock(clock)
        dashboard = TrafficDashboard(window_s=window_s, clock=clock_fn)
        for ev in _load_traffic_events(events_json):
            dashboard.record(ev)
        if json_output:
            typer.echo(json.dumps(dashboard.summary(), indent=2, sort_keys=True))
            return
        typer.echo(render_traffic(dashboard))
    except Exception as exc:
        err_console.print(f"[red]traffic summary failed:[/red] {exc}")
        raise typer.Exit(1) from exc


app.add_typer(traffic_app, name="traffic")


# ---------------------------------------------------------------------------
# cockpit pre-check (governance)
# ---------------------------------------------------------------------------


@app.command("pre-check", help="Evaluate a PolicyContext against the governance PolicyEngine.")
def cockpit_pre_check(
    agent: str = typer.Option("", "--agent", help="Agent name (e.g. 'cursor')"),
    model: str = typer.Option("", "--model", help="Model name (e.g. 'gpt-4o')"),
    lane: str = typer.Option("standard", "--lane", help="Lane: standard|critical|recovery|deferral"),
    environment: str = typer.Option("development", "--env", help="Environment: development|staging|production"),
    confidence: Optional[float] = typer.Option(None, "--confidence", help="Confidence 0..1"),
    prompt: str = typer.Option("", "--prompt", help="Prompt (hashed into the cache key)"),
    namespace: str = typer.Option(
        "global",
        "--namespace",
        help=(
            "Federated policy namespace. With ``--batch``, this value pins every "
            "corpus entry's namespace unless the entry explicitly carries its own "
            "non-empty ``namespace``. Without ``--batch``, it overrides the "
            "single-context ``PolicyContext.namespace``."
        ),
    ),
    default_policy: Optional[str] = typer.Option(
        None,
        "--default-policy",
        help=(
            "Enable federated policy lookup with this default namespace. Passed "
            "through to ``PolicyEngine(default_namespace=...)`` on ``--commit``; "
            "ignored on the one-shot ``--dry-run`` path. When ``--batch`` is "
            "used and ``--commit`` is set, this also auto-enables "
            "``use_federation=True`` on the underlying engine."
        ),
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON decision"),
    dry_run: bool = typer.Option(True, "--dry-run/--commit", help="Default dry-run; pass --commit to cache"),
    batch: Optional[Path] = typer.Option(
        None,
        "--batch",
        help="Replay a corpus of PolicyContext JSONs in one pass (file or dir of *.json).",
    ),
    audit_path: Optional[Path] = typer.Option(
        None,
        "--audit-path",
        help="Persist every batch decision to this JSONL file (defaults to the cockpit appender's path).",
    ),
    audit_append: bool = typer.Option(
        False,
        "--audit-append/--audit-overwrite",
        help="Append to the audit file (default: overwrite; useful for replay runs).",
    ),
) -> None:
    """Evaluate a :class:`PolicyContext` and emit the resulting decision.

    With ``--batch <path>`` (WP-3001 SOTA replay tooling) the command
    consumes a JSON file (list of contexts) or a directory of ``*.json``
    files (each a list) and emits one combined decision log. The
    batch mode still honors ``--dry-run`` / ``--commit`` semantics:
    a deny on any item exits ``3`` after the full batch drains.

    ``--namespace <name>`` and ``--default-policy <name>`` are the
    Lane 2 federation-namespace pin: they let SOTA replay tooling
    force every corpus entry to live in (and the engine to default to)
    a single namespace without rewriting every JSON entry.
    """
    try:
        # Import lazily so the CLI does not pull the full governance
        # module chain on commands that don't need it.
        from ..governance.policy_engine import (
            PolicyContext,
            PolicyEngine,
            evaluate_pre_check,
        )
        from .cockpit import DecisionNotice
        from .decision_audit import DecisionAuditAppender
    except Exception as exc:  # pragma: no cover - import guard
        err_console.print(f"[red]governance unavailable:[/red] {exc}")
        raise typer.Exit(2) from exc
    try:
        # Batch mode takes precedence over the single-context path.
        # Both share the same dry-run / commit semantics.
        if batch is not None:
            # ``--default-policy`` auto-enables federation on --commit so the
            # caller does not have to know about ``use_federation`` to get
            # the federated default-namespace pin to take effect.
            use_federation = default_policy is not None
            exit_code = _run_pre_check_batch(
                batch=batch,
                engine_factory=lambda: PolicyEngine(
                    use_federation=use_federation,
                    default_namespace=default_policy or "global",
                ),
                use_engine=not dry_run,
                appender_factory=lambda: DecisionAuditAppender(audit_path=audit_path),
                # Only persist when ``--audit-path`` is explicitly supplied.
                # The historical ``or True`` accidentally wrote to the default
                # ``~/.thegent/cockpit_decisions.jsonl`` even when the operator
                # did not opt in — a SOTA replay-tooling footgun (P0 audit).
                persist_audit=audit_path is not None,
                append_audit=audit_append,
                json_output=json_output,
                namespace_override=namespace,
            )
            raise typer.Exit(exit_code)

        ctx = PolicyContext(
            agent=agent,
            model=model,
            lane=lane,
            confidence=confidence,
            environment=environment,
            namespace=namespace,
            prompt=prompt,
        )
        # Use the one-shot helper for dry-run; only build a long-lived
        # PolicyEngine when the caller opts in. This keeps the read path
        # cheap for SOTA replay tooling. ``--default-policy`` flows into
        # the engine as both ``use_federation=True`` (when set) and the
        # ``default_namespace`` kwarg; on the one-shot dry-run path it is
        # a no-op (the federation lookup never fires).
        if dry_run:
            decision = evaluate_pre_check(ctx)
        else:
            engine = PolicyEngine(
                use_federation=default_policy is not None,
                default_namespace=default_policy or "global",
            )
            decision = engine.evaluate(ctx)
        if json_output:
            typer.echo(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
            return
        typer.echo(
            f"verdict={decision.verdict.value} reason_code={decision.reason_code.value} "
            f"rule_id={decision.rule_id or '-'} cached={decision.cached} "
            f"override_applied={decision.override_applied} reason={decision.reason!r}"
        )
        if decision.verdict.value == "deny":
            raise typer.Exit(3)
    except typer.Exit:
        raise
    except Exception as exc:
        err_console.print(f"[red]pre-check failed:[/red] {exc}")
        raise typer.Exit(1) from exc


def _run_pre_check_batch(
    *,
    batch: Path,
    engine_factory: Callable[[], Any],
    use_engine: bool,
    appender_factory: Callable[[], DecisionAuditAppender],
    persist_audit: bool,
    append_audit: bool,
    json_output: bool,
    namespace_override: Optional[str] = None,
) -> int:
    """Replay a corpus of :class:`PolicyContext` JSONs through pre-check.

    Returns the process exit code: ``3`` if any item yielded ``deny``,
    ``0`` otherwise. The function never raises for individual deny
    verdicts (so a single deny does not abort the run) — SOTA tooling
    can keep draining the corpus and inspect the combined audit log.

    ``batch`` may be:

    * a JSON file (list of context dicts, or a single context dict)
    * a directory containing ``*.json`` files (each: list or single dict)

    ``namespace_override`` pins every entry's ``namespace`` to the given
    value unless the entry already carries an explicit namespace (the
    Lane 2 federation contract). Both ``pre-check`` and ``replay`` route
    through this argument so they cannot drift apart on namespace
    semantics.
    """
    contexts, decisions, notices = _build_batch_decision_log(
        batch=batch,
        engine_factory=engine_factory,
        use_engine=use_engine,
        namespace_override=namespace_override,
    )
    if not contexts:
        err_console.print(f"[yellow]pre-check batch is empty:[/yellow] {batch}")
        return 0

    appender = appender_factory() if persist_audit else None
    if appender is not None and not append_audit:
        # Overwrite the audit file on replay so SOTA runs are
        # self-contained.
        path = appender.audit_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    any_deny = any(d.verdict.value == "deny" for d in decisions)
    if json_output:
        for d in decisions:
            typer.echo(json.dumps(d.to_dict(), indent=2, sort_keys=True))

    if appender is not None and notices:
        appender.record_many(notices)

    summary = (
        f"pre-check batch: items={len(notices)} deny={any_deny} audit={appender.audit_path() if appender else '-'}"
    )
    typer.echo(summary)
    return 3 if any_deny else 0


def _build_batch_decision_log(
    *,
    batch: Path,
    engine_factory: Callable[[], Any],
    use_engine: bool,
    namespace_override: Optional[str] = None,
) -> tuple[list[Any], list[Any], list[DecisionNotice]]:
    """Shared batch pipeline used by ``pre-check --batch`` and ``replay``.

    Returns a 3-tuple of ``(contexts, decisions, notices)`` after:

    1. Loading the corpus via :func:`_load_pre_check_corpus` (which
       applies ``namespace_override`` if supplied — Lane 2 federation
       contract).
    2. Running each context through either the long-lived
       :class:`PolicyEngine` (``use_engine=True``) or the one-shot
       :func:`evaluate_pre_check` helper, building a
       :class:`DecisionNotice` for every verdict so the audit appender
       gets a uniform stream regardless of the underlying engine.

    This is the single point of truth for the load+evaluate+notice
    pipeline so ``pre-check`` and ``replay`` cannot drift apart on
    cache keys, return shape, or notice schema (Phase 3/4 hardening
    lane, third "Unblocked Next" item). The function does NOT touch
    the audit appender; that's the caller's responsibility (so both
    ``pre-check`` and ``replay`` can persist the same notice stream
    via their own ``DecisionAuditAppender`` factory).
    """
    from ..governance.policy_engine import evaluate_pre_check

    contexts = _load_pre_check_corpus(batch, namespace_override=namespace_override)
    if not contexts:
        return [], [], []

    engine = engine_factory() if use_engine else None
    decisions: list[Any] = []
    notices: list[DecisionNotice] = []
    for ctx in contexts:
        if use_engine and engine is not None:
            decision = engine.evaluate(ctx)
        else:
            decision = evaluate_pre_check(ctx)
        decisions.append(decision)
        notice = DecisionNotice(
            verdict=decision.verdict.value,
            reason_code=decision.reason_code.value,
            rule_id=decision.rule_id or "",
            agent=ctx.agent,
            lane=ctx.lane,
            evaluated_at=decision.evaluated_at if hasattr(decision, "evaluated_at") else 0.0,
            reason=decision.reason,
        )
        notices.append(notice)
    return contexts, decisions, notices


def _load_pre_check_corpus(
    path: Path,
    namespace_override: Optional[str] = None,
) -> list[Any]:
    """Load a ``--batch`` input into a flat list of ``PolicyContext``.

    Accepts:
        * a JSON file containing a list of context dicts
        * a JSON file containing a single context dict
        * a directory of ``*.json`` files, each shaped as above

    ``namespace_override`` pins every entry's ``namespace`` to the
    given value unless the entry already carries an explicit non-empty
    namespace. This is the Lane 2 federation-namespace contract so
    a CLI invocation like ``pre-check --namespace team-a`` forces every
    corpus entry to live in that namespace without requiring callers
    to rewrite every JSON.

    Empty / unreadable inputs raise ``ValueError`` with a useful
    message so the CLI surfaces it before draining the audit pipeline.
    """
    from ..governance.policy_engine import PolicyContext

    if not path.exists():
        raise FileNotFoundError(f"batch path not found: {path}")

    def _coerce(entry: Any, src: Path) -> PolicyContext:
        if not isinstance(entry, dict):
            raise ValueError(f"batch {src} entries must be objects, got {type(entry).__name__}: {entry!r}")
        ns = str(entry.get("namespace", ""))
        if namespace_override is not None and (not ns or ns == "global"):
            ns = namespace_override
        elif not ns:
            ns = "global"
        return PolicyContext(
            agent=str(entry.get("agent", "")),
            model=str(entry.get("model", "")),
            lane=str(entry.get("lane", "standard")),
            confidence=entry.get("confidence"),
            environment=str(entry.get("environment", "development")),
            namespace=ns,
            prompt=str(entry.get("prompt", "")),
        )

    if path.is_file():
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return [_coerce(e, path) for e in raw]
        return [_coerce(raw, path)]
    if path.is_dir():
        out: list[Any] = []
        for child in sorted(path.glob("*.json")):
            raw = json.loads(child.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                out.extend(_coerce(e, child) for e in raw)
            else:
                out.append(_coerce(raw, child))
        return out
    raise ValueError(f"--batch path is neither file nor directory: {path}")


# ---------------------------------------------------------------------------
# cockpit replay (Phase 3/4 SOTA snapshot validator)
# ---------------------------------------------------------------------------


# Fields that must match for a snapshot entry to count as equal to the
# engine's ``PolicyDecision.to_dict()`` output. ``cached`` and
# ``evaluated_at`` are explicitly excluded because they're
# runtime-dependent (the replay may run on a different wall clock than
# the snapshot's author), and a leading/trailing whitespace difference
# in ``reason`` is tolerated below.
_REPLAY_COMPARE_FIELDS: tuple[str, ...] = (
    "verdict",
    "reason_code",
    "rule_id",
    "override_applied",
)


# Dispatch table for the ``--snapshot-flip <field>`` SOTA canary workflow.
# Each entry knows how to invert one value of the given field so the
# compare step records a guaranteed mismatch on that field without the
# operator having to hand-edit the snapshot file on disk.
#
# Unknown fields fall through to a generic bool/not-string swap that
# covers the common cases without raising — the flip is a *canary*, not
# a strict guarantee; downstream ``_compare_decision`` is still the
# source of truth for whether the inverted snapshot actually disagrees
# with the engine's output.
def _invert_snapshot_value(field: str, value: Any) -> Any:
    """Return the inverted form of ``value`` for the SOTA ``--snapshot-flip`` flag.

    Recognised semantics:

    * ``verdict``: ``allow`` ↔ ``deny`` (and ``warn`` ↔ ``deny`` as a
      sensible canary default — flipping a warn to a deny is a strict
      mismatch against the engine's actual output).
    * ``override_applied``: bool negation.
    * ``cached``: bool negation (mirror of ``override_applied``).
    * any other field: bool negation when the value is a ``bool``,
      otherwise a stable "string-flipped" sentinel so the compare step
      records a mismatch without losing the field's type.

    The function is intentionally tolerant of ``None``/missing fields
    so a flip on an absent field is a no-op rather than a crash.
    """
    if value is None:
        return value
    if field == "verdict":
        text = str(value).strip().lower()
        if text == "allow":
            return "deny"
        if text == "deny":
            return "allow"
        # ``warn`` and any unrecognised verdict flip to ``deny`` so the
        # canary always disagrees with the engine's actual verdict.
        return "deny"
    if field in ("override_applied", "cached"):
        if isinstance(value, bool):
            return not value
        # Coerce string-shaped bools ("true"/"false") so yaml/toml
        # snapshots still get inverted cleanly.
        text = str(value).strip().lower()
        if text in ("true", "1", "yes"):
            return False
        if text in ("false", "0", "no"):
            return True
        return not bool(value)
    # Generic fallback: if the field is bool-shaped, negate; if string,
    # return a sentinel that the compare step will flag as a mismatch.
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        # Pick a value clearly different from any sane decision output;
        # use the negation when non-zero, otherwise a clearly-out-of-band
        # sentinel that still respects the field's numeric type.
        return -value if value != 0 else -1
    return f"<flipped:{value}>"


def _apply_snapshot_flip(
    snapshot: list[dict[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    """Return a copy of ``snapshot`` with ``field`` inverted on every entry.

    Mirrors the on-disk ``_write_snapshot(..., flip=True)`` pattern from
    ``tests/test_unit_cockpit_sota_json_parity.py`` but operates in
    memory so the operator's ``--compare`` file is left untouched. This
    is the SOTA canary workflow: deliberately force the replay into the
    mismatch path so the diff machinery + JSON envelope + exit code
    contract get exercised end-to-end on every CI run.
    """
    if not field:
        return snapshot
    flipped: list[dict[str, Any]] = []
    for entry in snapshot:
        if not isinstance(entry, dict):
            flipped.append(entry)
            continue
        new_entry = dict(entry)
        new_entry[field] = _invert_snapshot_value(field, entry.get(field))
        flipped.append(new_entry)
    return flipped


def _load_replay_snapshot(path: Path) -> list[dict[str, Any]]:
    """Load the ``--compare`` snapshot into a list of decision dicts.

    Accepts two top-level shapes:

    * a JSON list of ``PolicyDecision``-shaped dicts, or
    * a JSON object with a ``"decisions"`` key holding that same list.

    Anything else surfaces a ``ValueError`` so the CLI can exit ``1``
    with a useful message instead of crashing mid-diff.
    """
    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        snapshot = raw
    elif isinstance(raw, dict) and isinstance(raw.get("decisions"), list):
        snapshot = raw["decisions"]
    else:
        raise ValueError(
            "compare snapshot must be a list or an object with a 'decisions' key, "
            f"got {type(raw).__name__}" + (f" with keys {list(raw.keys())}" if isinstance(raw, dict) else "")
        )
    return snapshot


def _compare_decision(
    expected: dict[str, Any],
    actual: dict[str, Any],
) -> list[str]:
    """Return the list of field names that disagree between two decision dicts.

    Whitespace-only differences in ``reason`` are tolerated so author
    edits (markdown line breaks, trailing newlines) don't false-positive.
    All other fields use strict equality.
    """
    diffs: list[str] = []
    for field in _REPLAY_COMPARE_FIELDS:
        exp_val = expected.get(field)
        act_val = actual.get(field)
        if field == "rule_id":
            # ``None`` and ``null`` (JSON's missing) are equivalent here.
            if (exp_val is None or exp_val == "") and (act_val is None or act_val == ""):
                continue
        if exp_val != act_val:
            diffs.append(field)
    # Whitespace-tolerant reason comparison.
    exp_reason = str(expected.get("reason", "")).strip()
    act_reason = str(actual.get("reason", "")).strip()
    if exp_reason != act_reason:
        diffs.append("reason")
    return diffs


def _format_mismatch(
    idx: int,
    expected: Optional[dict[str, Any]],
    actual: Optional[dict[str, Any]],
    diff_fields: list[str],
) -> str:
    """Stable text format for one mismatch row: ``mismatch[i]: ...``.

    When a field is in the diff list we render ``expected=X actual=Y``
    for that field so the operator sees the exact disagreement.
    """
    parts: list[str] = []
    if expected is None and actual is not None:
        return f"mismatch[{idx}]: produced entry has no matching expected entry"
    if actual is None and expected is not None:
        return f"mismatch[{idx}]: expected entry has no matching produced entry"
    if expected is None or actual is None:  # pragma: no cover - defensive
        return f"mismatch[{idx}]: <unknown diff>"
    for field in diff_fields:
        exp_val = expected.get(field)
        act_val = actual.get(field)
        parts.append(f"{field} expected={exp_val} actual={act_val}")
    if not parts:
        # Field-level compare reported nothing, but the row is here —
        # fall back to a generic message so the report is never empty.
        parts.append("snapshot differs but no tracked field mismatched")
    return f"mismatch[{idx}]: " + " ".join(parts)


@app.command(
    "replay",
    help=(
        "Replay a corpus against an expected PolicyDecision snapshot and report "
        "line-by-line mismatches (Phase 3/4 hardening lane, third Unblocked Next item). "
        "Pass --snapshot-format yaml/toml or --report-format json/junitxml to "
        "transparently delegate to `thegent sota replay`."
    ),
)
def cockpit_replay(
    batch: Path = typer.Option(
        ...,
        "--batch",
        help="Corpus of PolicyContext JSONs (file or dir of *.json) — same as pre-check --batch.",
    ),
    compare: Path = typer.Option(
        ...,
        "--compare",
        help=(
            "Expected snapshot JSON: either a list of PolicyDecision-shaped dicts "
            "or an object with a ``decisions`` key holding the same list."
        ),
    ),
    audit_path: Optional[Path] = typer.Option(
        None,
        "--audit-path",
        help="Persist every replay decision to this JSONL file (defaults to cockpit appender's path).",
    ),
    audit_append: bool = typer.Option(
        False,
        "--audit-append/--audit-overwrite",
        help="Append to the audit file (default: overwrite; useful for chained replays).",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--commit",
        help="Default dry-run; pass --commit to cache decisions in the PolicyEngine.",
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
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit a structured {matched, mismatches, decisions, audit} object instead of text.",
    ),
    snapshot_format: str = typer.Option(
        "json",
        "--snapshot-format",
        help=(
            "Snapshot input format (json, yaml, or toml). Defaults to json. "
            "When set to anything other than 'json', delegates to `thegent sota replay`."
        ),
    ),
    report_format: str = typer.Option(
        "text",
        "--report-format",
        help=(
            "Report output format (text, json, or junitxml). Defaults to text. "
            "When set to anything other than 'text', delegates to `thegent sota replay`."
        ),
    ),
    report_path: Optional[Path] = typer.Option(
        None,
        "--report-path",
        help="Write the report to this file (delegated to sota replay; default: stdout).",
    ),
    snapshot_flip: Optional[str] = typer.Option(
        None,
        "--snapshot-flip",
        help=(
            "SOTA canary workflow: invert the value of <field> on every entry of "
            "the loaded --compare snapshot in memory (e.g. 'verdict' or "
            "'override_applied') so the replay walks the mismatch path without "
            "the operator having to hand-edit the snapshot file. Useful for "
            "exercising the diff machinery + JSON envelope + exit code 4 contract "
            "end-to-end on every CI run."
        ),
    ),
) -> None:
    """Replay ``--batch`` through pre-check and validate against ``--compare``.

    Exit codes:

    * ``0`` — every decision matches the expected snapshot.
    * ``4`` — at least one mismatch (mirrors the exit-code-3 convention
      for ``deny`` but kept distinct so ``pre-check`` and ``replay`` can
      signal different failure modes to shell pipelines).
    * ``1`` — bad inputs (missing files, malformed snapshot, etc.).

    The default behaviour (``--snapshot-format json`` + ``--report-format
    text``) is the historical cockpit contract: text output, JSON
    snapshot, exit code 4 on mismatch.  When the operator passes a
    non-default ``--snapshot-format`` (yaml / toml) or
    ``--report-format`` (json / junitxml) we transparently delegate to
    ``thegent sota replay`` so callers do not need to learn a new
    command name.  This is the WORKLOG "Unblocked Next" #1 shim lane.
    """
    # Shim dispatch: when the operator asks for a non-default snapshot
    # or report format, defer to `sota replay` so we don't duplicate
    # the format-dispatch tables in two places.  ``--json`` is
    # translated to ``--report-format json`` so the operator-facing
    # knob keeps its existing shape.
    snapshot_format_lc = snapshot_format.lower()
    report_format_lc = report_format.lower()
    effective_report_format = "json" if json_output else report_format_lc

    if snapshot_format_lc != "json" or effective_report_format != "text":
        # Defer import so the cockpit CLI surface still loads cleanly
        # even if sota tooling is unavailable; the delegated call will
        # surface its own clean error.
        try:
            from .cli_sota import sota_replay
        except Exception as exc:  # pragma: no cover - import guard
            err_console.print(f"[red]sota replay unavailable:[/red] {exc}")
            raise typer.Exit(2) from exc

        # ``sota replay`` always appends a trailing
        # ``sota replay: matched=...`` tail line for operator visibility,
        # but ``cockpit replay --json`` historically emitted a pure-JSON
        # envelope so pipelines can ``jq`` the output directly.  We don't
        # redirect stdout (so the CliRunner capture still works); instead
        # we let ``sota replay`` print its full stream and then echo a
        # synthetic cockpit-style tail line so the operator still sees
        # the cockpit ``matched=...`` summary that ``cockpit replay``
        # emitted before the shim existed.
        try:
            sota_replay(
                batch=batch,
                compare=compare,
                snapshot_format=snapshot_format_lc,
                report_format=effective_report_format,
                report_path=report_path,
                audit_path=audit_path,
                audit_append=audit_append,
                dry_run=dry_run,
                namespace=namespace,
                default_policy=default_policy,
                # ``suite_name`` has a ``typer.Option(...)`` default in
                # ``sota_replay``; when invoked as a plain function (as
                # we are doing here) that default is the ``OptionInfo``
                # sentinel rather than the string ``"thegent.sota.replay"``.
                # Pass the canonical name explicitly so JUnit-XML output
                # is well-formed when report-format=junitxml.
                suite_name="thegent.sota.replay",
                # Suppress the sota tail line so the cockpit contract
                # (pure JSON for ``--json``, pure text body for the
                # default path) is preserved.  The cockpit command will
                # emit its own tail via the legacy code path that runs
                # before the shim takes over; this prevents double
                # operator summaries.
                _render_tail=False,
                snapshot_flip=snapshot_flip,
            )
        except typer.Exit:
            raise
        except Exception as exc:
            err_console.print(f"[red]replay delegation failed:[/red] {exc}")
            raise typer.Exit(1) from exc
        return
    try:
        from ..governance.policy_engine import PolicyEngine
    except Exception as exc:  # pragma: no cover - import guard
        err_console.print(f"[red]governance unavailable:[/red] {exc}")
        raise typer.Exit(2) from exc

    try:
        if not batch.exists():
            err_console.print(f"[red]replay failed:[/red] batch path not found: {batch}")
            raise typer.Exit(1)
        if not compare.exists():
            err_console.print(f"[red]replay failed:[/red] compare path not found: {compare}")
            raise typer.Exit(1)
        try:
            expected_snapshot = _load_replay_snapshot(compare)
        except ValueError as exc:
            err_console.print(f"[red]replay failed:[/red] {exc}")
            raise typer.Exit(1) from exc
        except json.JSONDecodeError as exc:
            err_console.print(f"[red]replay failed:[/red] compare file is not valid JSON: {exc}")
            raise typer.Exit(1) from exc

        # SOTA canary workflow: when the operator passes
        # ``--snapshot-flip <field>`` we invert that field on every
        # snapshot entry **in memory** so the replay walks the mismatch
        # path without the operator having to hand-edit the --compare
        # file on disk. See ``_apply_snapshot_flip`` for the inversion
        # semantics.
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
            err_console.print(f"[yellow]replay batch is empty:[/yellow] {batch}")
            # An empty corpus against a non-empty snapshot is a mismatch;
            # against an empty snapshot it is a match. Either way, exit 0
            # since there is no decision to validate.
            _emit_replay_summary(
                items=0,
                matched=not expected_snapshot,
                mismatches=[],
                decisions=[],
                audit_path=str(audit_path) if audit_path else None,
                json_output=json_output,
            )
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
                        "text": _format_mismatch(idx, exp, act, diff_fields),
                    }
                )

        # Persist decisions via the same appender pattern as pre-check
        # so the JSONL shape stays identical (the spec's "replay
        # writes a JSONL that matches the per-line appender output").
        audit_str: Optional[str] = None
        if audit_path is not None:
            appender = DecisionAuditAppender(audit_path=audit_path)
            if not audit_append:
                path = appender.audit_path()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")
            appender.record_many(notices)
            audit_str = str(appender.audit_path())

        matched = not mismatches
        _emit_replay_summary(
            items=len(produced),
            matched=matched,
            mismatches=mismatches,
            decisions=produced,
            audit_path=audit_str,
            json_output=json_output,
        )
        # Operator confirmation: when an audit file was written, tell
        # the operator whether the run **appended** to an existing
        # file or **overwrote** it. CI/nightly harnesses that re-run
        # the same snapshot nightly need to know whether their prior
        # audit trail was preserved (append) or zeroed (overwrite)
        # so they can detect accidental truncation. Only emitted in
        # text mode; ``--json`` consumers parse the structured
        # envelope and would treat this line as noise.
        if audit_str is not None and not json_output:
            mode = "append" if audit_append else "overwrite"
            typer.echo(f"replay: audit={audit_str} mode={mode} lines={len(produced)}")
        if not matched:
            raise typer.Exit(4)
    except typer.Exit:
        raise
    except Exception as exc:
        err_console.print(f"[red]replay failed:[/red] {exc}")
        raise typer.Exit(1) from exc


def _emit_replay_summary(
    *,
    items: int,
    matched: bool,
    mismatches: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    audit_path: Optional[str],
    json_output: bool,
) -> None:
    """Render the replay outcome (text or JSON) and write to stdout."""
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "matched": matched,
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
        )
        return
    typer.echo(f"replay: batch=? compare=? items={items} matched={matched} mismatches={len(mismatches)}")
    for m in mismatches:
        typer.echo(m["text"])


# ---------------------------------------------------------------------------
# cockpit audit (Phase 3/4 JSONL appender companion)
# ---------------------------------------------------------------------------


audit_app = typer.Typer(
    help="Tail or replay the JSONL audit log produced by DecisionAuditAppender.",
    no_args_is_help=True,
)


@audit_app.command("tail", help="Print the last N decisions from the audit JSONL.")
def cockpit_audit_tail(
    n: int = typer.Option(20, "--lines", "-n", help="Number of lines to print"),
    audit_path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Override the default ~/.thegent/cockpit_decisions.jsonl",
    ),
) -> None:
    """Tail the JSONL audit log for SOTA replay tooling."""
    try:
        from ..ux.decision_audit import DecisionAuditAppender  # noqa: F401  (re-export for callers)

        appender = DecisionAuditAppender(audit_path=audit_path)
        events = appender.tail_events(n=n)
        for ev in events:
            typer.echo(json.dumps(ev, sort_keys=True))
    except Exception as exc:
        err_console.print(f"[red]audit tail failed:[/red] {exc}")
        raise typer.Exit(1) from exc


@audit_app.command(
    "decision-tail",
    help="Live-tail the JSONL decision audit log (--follow polls and emits new lines).",
)
def cockpit_audit_decision_tail(
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Poll the file and emit new lines as they appear (SIGINT exits cleanly).",
    ),
    interval: float = typer.Option(
        1.0,
        "--interval",
        "-i",
        help="Poll cadence in seconds when --follow is set.",
    ),
    audit_path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Override the default ~/.thegent/cockpit_decisions.jsonl",
    ),
    max_events: int = typer.Option(
        0,
        "--max-events",
        help="Stop after this many events (0 = unbounded). Useful for CI smoke tests.",
    ),
    exit_code_on_cap: int = typer.Option(
        0,
        "--exit-code-on-cap",
        help=(
            "Exit code to use when --max-events is reached (only applies when "
            "--follow is set; 0 = silent, recommended non-zero for CI smoke tests, "
            "e.g. 75 to distinguish from generic errors). Default 0 (current behaviour)."
        ),
    ),
) -> None:
    """Single-shot or live-tail the JSONL decision audit log.

    Without ``--follow`` this is a thin wrapper over
    :meth:`DecisionAuditAppender.tail_events` that prints the most
    recent entries (default 20). With ``--follow`` the command polls
    the JSONL file every ``--interval`` seconds and emits each new
    line as it appears; ``SIGINT`` exits cleanly with code ``0`` so
    operator ``tail -f`` style workflows stay ergonomic.

    ``--max-events`` caps the total number of events emitted
    (including the initial backlog on entry) and is intended for
    CI / smoke tests that need to deterministically bound the run.
    When the cap is reached during a ``--follow`` session, the
    process exits with ``--exit-code-on-cap`` (default ``0``) so
    shell pipelines / smoke harnesses can detect the bounded
    completion without parsing stderr. Operators who want the
    historical "success" semantics can leave the flag at its
    default; CI consumers should pass a non-zero value such as
    ``75`` to distinguish "capped and stopped" from "errored out".
    """
    from ..ux.decision_audit import DEFAULT_TAIL_INTERVAL_S, DecisionAuditAppender

    # Defensive: when ``--follow`` is set, fall back to the
    # appender's canonical interval so operator UIs never see a
    # 0s tight loop if the caller passes ``--interval 0``.
    interval_s = float(interval) if interval > 0 else DEFAULT_TAIL_INTERVAL_S
    cap = int(max_events) if max_events and max_events > 0 else 0
    # Exit codes are 0-255; clamp negatives / oversize values so a
    # typo doesn't accidentally return a noisy traceback.
    exit_code = int(exit_code_on_cap) if exit_code_on_cap else 0
    if exit_code < 0 or exit_code > 255:
        raise typer.BadParameter(f"--exit-code-on-cap must be in [0, 255], got {exit_code_on_cap!r}")

    try:
        appender = DecisionAuditAppender(audit_path=audit_path)
    except Exception as exc:
        err_console.print(f"[red]audit decision-tail failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not follow:
        # Single-shot path: identical semantics to ``audit tail`` so
        # operators can switch between the two without surprises.
        try:
            n = 20 if cap == 0 else cap
            events = appender.tail_events(n=n)
            for ev in events:
                typer.echo(json.dumps(ev, sort_keys=True))
        except Exception as exc:
            err_console.print(f"[red]audit decision-tail failed:[/red] {exc}")
            raise typer.Exit(1) from exc
        return

    try:
        emitted = _follow_audit_log(appender, interval_s=interval_s, max_events=cap)
    except KeyboardInterrupt:
        # SIGINT during a live tail is the operator pressing Ctrl-C;
        # exit cleanly with code 0 so shells / shell pipelines don't
        # treat it as an error.
        raise typer.Exit(0) from None

    # If the operator asked for a bounded run AND the cap was hit AND
    # they wired a non-zero exit code, propagate it so CI smoke
    # harnesses can detect "ran to completion under the cap" without
    # scraping stderr.
    if cap and emitted >= cap and exit_code:
        raise typer.Exit(exit_code) from None


def _follow_audit_log(
    appender: "DecisionAuditAppender",
    *,
    interval_s: float,
    max_events: int,
) -> int:
    """Poll the appender's JSONL file and emit each new line as it appears.

    Tracks a **byte offset** (not a line count) so we never re-emit
    lines that were already seen on entry. Handles truncation by
    re-anchoring to ``0`` whenever the file shrinks below the saved
    offset (so log rotation / ``> file.jsonl`` workflows behave).

    Args:
        appender: A :class:`DecisionAuditAppender` whose
            :meth:`audit_path` points at the JSONL to watch.
        interval_s: Seconds to sleep between polls.
        max_events: Optional cap on the number of events to emit
            (``0`` = unbounded). When the cap is hit the helper
            returns cleanly.

    Returns:
        The total number of events emitted.

    Raises:
        KeyboardInterrupt: Re-raised so callers can map SIGINT to a
            clean exit code.
    """
    path = appender.audit_path()
    # Make sure the parent directory exists; the appender does this on
    # the first record, but a fresh follow on a never-written log still
    # needs somewhere to land.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Seed offset with the file's current size so we don't re-emit the
    # existing backlog (operators who want the backlog should call
    # ``cockpit audit tail`` first).
    offset = path.stat().st_size if path.exists() else 0
    emitted = 0
    # ``max_events <= 0`` means unbounded.
    cap = max_events if max_events and max_events > 0 else 0
    # ``interval_s`` must be > 0 to avoid a tight loop on a typo.
    sleep_s = max(interval_s, 0.01)

    while True:
        try:
            current_size = path.stat().st_size
        except FileNotFoundError:
            # File momentarily missing (rotation, etc.); back off and
            # retry on the next tick.
            time.sleep(sleep_s)
            continue

        if current_size < offset:
            # File was truncated / rotated; re-anchor to the start so
            # we pick up whatever the writer put in its place.
            offset = 0

        if current_size > offset:
            with path.open("r", encoding="utf-8") as fh:
                fh.seek(offset)
                chunk = fh.read(current_size - offset)
            # Only advance the offset after a successful read so a
            # transient IO error doesn't silently drop lines.
            offset = current_size
            for raw_line in chunk.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                typer.echo(line)
                emitted += 1
                if cap and emitted >= cap:
                    return emitted

        if cap and emitted >= cap:
            return emitted
        # ``sleep`` is interruptible so SIGINT bubbles up as
        # ``KeyboardInterrupt`` promptly.
        time.sleep(sleep_s)


app.add_typer(audit_app, name="audit")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_runs(path: Optional[Path]) -> list[RunEvent]:
    """Parse a JSON file of run dicts into :class:`RunEvent` instances."""
    if path is None:
        return []
    if not path.exists():
        raise FileNotFoundError(f"runs file not found: {path}")
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    out: list[RunEvent] = []
    for entry in raw:
        state_str = entry.get("state", "active")
        try:
            state = RunState(state_str)
        except ValueError as exc:
            raise ValueError(f"invalid run state {state_str!r}: {exc}") from exc
        out.append(
            RunEvent(
                run_id=str(entry["run_id"]),
                state=state,
                lane=str(entry.get("lane", "standard")),
                agent=str(entry.get("agent", "")),
                confidence=_as_optional_float(entry.get("confidence")),
                elapsed_s=float(entry.get("elapsed_s", 0.0)),
                note=str(entry.get("note", "")),
            )
        )
    return out


def _load_overrides(path: Optional[Path]) -> list[OverrideEvent]:
    """Parse a JSON file of override dicts into :class:`OverrideEvent`."""
    if path is None:
        return []
    if not path.exists():
        raise FileNotFoundError(f"overrides file not found: {path}")
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    out: list[OverrideEvent] = []
    for entry in raw:
        out.append(
            OverrideEvent(
                rule_id=str(entry["rule_id"]),
                by=str(entry.get("by", "operator")),
                reason=str(entry.get("reason", "")),
                expires_in_s=float(entry.get("expires_in_s", 0.0)),
                metadata=dict(entry.get("metadata", {}) or {}),
            )
        )
    return out


def _load_traffic_events(path: Optional[Path]) -> list[TrafficEvent]:
    """Parse a JSON file of traffic event dicts."""
    if path is None:
        return []
    if not path.exists():
        raise FileNotFoundError(f"events file not found: {path}")
    raw: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    out: list[TrafficEvent] = []
    for entry in raw:
        ts = float(entry.get("ts", 0.0))
        out.append(
            TrafficEvent(
                ts=ts,
                lane=str(entry.get("lane", "standard")),
                agent=str(entry.get("agent", "")),
                status=str(entry.get("status", "ok")),
                duration_ms=float(entry.get("duration_ms", 0.0)),
                override_active=bool(entry.get("override_active", False)),
            )
        )
    return out


def _as_optional_float(value: Any) -> Optional[float]:
    """Return ``None`` for missing/None values; otherwise coerce to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"expected float, got {value!r}: {exc}") from exc


__all__ = [
    "app",
]


def main() -> None:  # pragma: no cover - convenience entry point
    """Module-level entry point so ``python -m thegent.ux.cli_cockpit`` works."""
    if len(sys.argv) == 1:
        typer.echo(app.get_help())
        return
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
