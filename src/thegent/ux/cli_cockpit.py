"""CLI surface for the operator cockpit (WP-4001), traffic KPIs (WP-Y7),
and policy pre-checks (WP-3001).

Three Typer sub-commands expose the Phase 3/4 governance+UX lane to
operators running outside the TUI:

* ``thegent cockpit render`` — render the 4-pane operator cockpit for a
  snapshot of runs / overrides (deterministic when ``--clock`` is set).
* ``thegent cockpit traffic`` — render the TRAFFIC KPI dashboard to stdout
  (also deterministic with ``--clock``).
* ``thegent cockpit pre-check`` — evaluate a :class:`PolicyContext` against
  the governance :class:`PolicyEngine` and emit the resulting
  :class:`PolicyDecision` as either human-readable text or JSON.

Each subcommand is intentionally side-effect-free: rendering does not
mutate cockpit state, and ``pre-check`` defaults to ``--dry-run`` so
operators can rehearse decisions without polluting the policy cache.

These commands complete the WORKLOG.md "Unblocked Next" backlog for the
Phase 3/4 hardening lane and give SOTA audit tooling a stable CLI
contract.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import typer
from rich.console import Console

from .cockpit import (
    OperatorCockpit,
    OverrideEvent,
    RunEvent,
    RunState,
    render_cockpit,
)
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
    namespace: str = typer.Option("global", "--namespace", help="Federated policy namespace"),
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
            exit_code = _run_pre_check_batch(
                batch=batch,
                engine_factory=lambda: PolicyEngine(),
                use_engine=not dry_run,
                appender_factory=lambda: DecisionAuditAppender(audit_path=audit_path),
                persist_audit=audit_path is not None or True,
                append_audit=audit_append,
                json_output=json_output,
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
        # cheap for SOTA replay tooling.
        if dry_run:
            decision = evaluate_pre_check(ctx)
        else:
            engine = PolicyEngine()
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
) -> int:
    """Replay a corpus of :class:`PolicyContext` JSONs through pre-check.

    Returns the process exit code: ``3`` if any item yielded ``deny``,
    ``0`` otherwise. The function never raises for individual deny
    verdicts (so a single deny does not abort the run) — SOTA tooling
    can keep draining the corpus and inspect the combined audit log.

    ``batch`` may be:

    * a JSON file (list of context dicts, or a single context dict)
    * a directory containing ``*.json`` files (each: list or single dict)
    """
    from ..governance.policy_engine import (
        PolicyContext,
        evaluate_pre_check,
    )
    from .cockpit import DecisionNotice

    contexts = _load_pre_check_corpus(batch)
    if not contexts:
        err_console.print(f"[yellow]pre-check batch is empty:[/yellow] {batch}")
        return 0

    engine = engine_factory() if use_engine else None
    appender = appender_factory() if persist_audit else None
    if appender is not None and not append_audit:
        # Overwrite the audit file on replay so SOTA runs are
        # self-contained.
        path = appender.audit_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    notices: list[DecisionNotice] = []
    any_deny = False
    for ctx in contexts:
        if use_engine and engine is not None:
            decision = engine.evaluate(ctx)
        else:
            decision = evaluate_pre_check(ctx)
        if decision.verdict.value == "deny":
            any_deny = True
        # Always feed the audit pipeline so SOTA replay tooling sees
        # the full decision stream regardless of verdict.
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
        if json_output:
            typer.echo(json.dumps(decision.to_dict(), indent=2, sort_keys=True))

    if appender is not None and notices:
        # Validate-then-append (matches ``record_many`` semantics).
        appender.record_many(notices)

    summary = (
        f"pre-check batch: items={len(notices)} deny={any_deny} audit={appender.audit_path() if appender else '-'}"
    )
    typer.echo(summary)
    return 3 if any_deny else 0


def _load_pre_check_corpus(path: Path) -> list[Any]:
    """Load a ``--batch`` input into a flat list of ``PolicyContext``.

    Accepts:
        * a JSON file containing a list of context dicts
        * a JSON file containing a single context dict
        * a directory of ``*.json`` files, each shaped as above

    Empty / unreadable inputs raise ``ValueError`` with a useful
    message so the CLI surfaces it before draining the audit pipeline.
    """
    from ..governance.policy_engine import PolicyContext

    if not path.exists():
        raise FileNotFoundError(f"batch path not found: {path}")

    def _coerce(entry: Any, src: Path) -> PolicyContext:
        if not isinstance(entry, dict):
            raise ValueError(f"batch {src} entries must be objects, got {type(entry).__name__}: {entry!r}")
        return PolicyContext(
            agent=str(entry.get("agent", "")),
            model=str(entry.get("model", "")),
            lane=str(entry.get("lane", "standard")),
            confidence=entry.get("confidence"),
            environment=str(entry.get("environment", "development")),
            namespace=str(entry.get("namespace", "global")),
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
