"""Plan commands implementation.

This module contains CLI commands for managing work plans and streams.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer


def dag_validate_cmd(*args: Any, **kwargs: Any) -> int:
    """Validate a DAG. Stub returning 0."""
    return 0


def dag_list_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """List DAGs. Thin shim over dag_list_impl."""
    from .impl import dag_list_impl

    return dag_list_impl(*args, **kwargs)


def dag_add_cmd(*args: Any, **kwargs: Any) -> int:
    """Add a node to a DAG. Stub returning 0."""
    return 0


def dag_remove_cmd(*args: Any, **kwargs: Any) -> int:
    """Remove a node from a DAG. Stub returning 0."""
    return 0


def dag_cancel_cmd(*args: Any, **kwargs: Any) -> int:
    """Cancel a DAG run. Stub returning 0."""
    return 0


def dag_status_cmd(*args: Any, **kwargs: Any) -> int:
    """Show DAG status. Stub returning 0."""
    return 0


def dag_update_cmd(*args: Any, **kwargs: Any) -> int:
    """Update a DAG node. Stub returning 0."""
    return 0


def dag_ready_cmd(*args: Any, **kwargs: Any) -> int:
    """List ready DAG nodes. Stub returning 0."""
    return 0


def dag_reconcile_cmd(*args: Any, **kwargs: Any) -> int:
    """Reconcile a DAG. Stub returning 0."""
    return 0


def plan_incorporate_cmd(*args: Any, **kwargs: Any) -> int:
    """Incorporate a plan. Stub returning 0."""
    return 0


def plan_claim_cmd(*args: Any, **kwargs: Any) -> int:
    """Claim a plan task. Stub returning 0."""
    return 0


def plan_complete_cmd(*args: Any, **kwargs: Any) -> int:
    """Complete a plan task. Stub returning 0."""
    return 0


def plan_wait_next_cmd(*args: Any, **kwargs: Any) -> int:
    """Wait for the next plan task. Stub returning 0."""
    return 0


def plan_do_next_cmd(*args: Any, **kwargs: Any) -> int:
    """Execute the next plan task. Stub returning 0."""
    return 0


def plan_get_next_cmd(*args: Any, **kwargs: Any) -> int:
    """Get the next plan task. Stub returning 0."""
    return 0


def plan_loop_cmd(*args: Any, **kwargs: Any) -> int:
    """Loop through a plan. Stub returning 0."""
    return 0


def plan_progress_cmd(*args: Any, **kwargs: Any) -> int:
    """Show plan progress. Stub returning 0."""
    return 0


def plan_analyze_cmd(*args: Any, **kwargs: Any) -> int:
    """Analyze a plan. Stub returning 0."""
    return 0


def closure_pack_cmd(*args: Any, **kwargs: Any) -> int:
    """Pack a closure. Stub returning 0."""
    return 0


def dag_run_cmd(*args: Any, **kwargs: Any) -> int:
    """Run a DAG. Stub returning 0."""
    return 0


def dag_sync_cmd(*args: Any, **kwargs: Any) -> int:
    """Sync a DAG. Stub returning 0."""
    return 0


def dag_checkpoint_cmd(*args: Any, **kwargs: Any) -> int:
    """Checkpoint a DAG. Stub returning 0."""
    return 0


def dag_rollback_cmd(*args: Any, **kwargs: Any) -> int:
    """Roll back a DAG. Stub returning 0."""
    return 0


def dag_checkpoints_cmd(*args: Any, **kwargs: Any) -> int:
    """List DAG checkpoints. Stub returning 0."""
    return 0


def dag_recover_cmd(*args: Any, **kwargs: Any) -> int:
    """Recover a DAG. Stub returning 0."""
    return 0


def dag_probe_cmd(*args: Any, **kwargs: Any) -> int:
    """Probe a DAG. Stub returning 0."""
    return 0


def workstream_query_cmd(workstream_id: str, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: query a workstream."""
    return {"workstream_id": workstream_id, "errors": [], "warnings": []}


def workstream_stats_cmd(workstream_id: str, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: workstream stats."""
    return {"workstream_id": workstream_id, "normalized": True, "changes": []}


def workstream_dashboard_cmd(*args: Any, **kwargs: Any) -> int:
    """Show workstream dashboard. Stub returning 0."""
    return 0


def workstream_launch_cmd(*args: Any, **kwargs: Any) -> int:
    """Launch a workstream. Stub returning 0."""
    return 0


def workstream_dependencies_cmd(*args: Any, **kwargs: Any) -> int:
    """Show workstream dependencies. Stub returning 0."""
    return 0


_WORK_STREAM_FILENAME = "WORK_STREAM.md"


def _resolve_work_stream_path(cd: Path | None) -> Path:
    """Resolve the canonical WORK_STREAM.md location for a verify/lint/normalize call."""
    base = Path(cd) if cd is not None else Path.cwd()
    return base / "docs" / "reference" / _WORK_STREAM_FILENAME


def _split_work_stream_sections(text: str) -> list[tuple[str, list[list[str]]]]:
    """Parse WORK_STREAM.md into (heading, rows) tuples per ## section.

    Headings come from ``^## `` lines. Each subsequent pipe-table row until the
    next ``## `` heading or EOF contributes one list of ``|``-split cell strings.
    """
    lines = text.splitlines()
    sections: list[tuple[str, list[list[str]]]] = []
    current_heading: str | None = None
    current_rows: list[list[str]] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, current_rows))
            current_heading = line[3:].strip()
            current_rows = []
            continue
        if current_heading is None:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if set(stripped.replace("|", "").replace(":", "").replace(" ", "")) <= {"-"}:
            # markdown separator row (---|---|) — skip
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        current_rows.append(cells)
    if current_heading is not None:
        sections.append((current_heading, current_rows))
    return sections


def _work_stream_id_column(rows: list[list[str]]) -> int | None:
    """Return the column index that looks like an ``ID`` header, or None."""
    for row in rows[:1]:
        for cell_idx, cell in enumerate(row):
            if cell.strip().lower() == "id":
                return cell_idx
    return None


def _collect_work_stream_ids(rows: list[list[str]]) -> list[str]:
    """Collect all ID cell values from a single section's rows (excluding header)."""
    if not rows:
        return []
    id_col = _work_stream_id_column(rows)
    if id_col is None:
        id_col = 0
    body = rows[1:] if len(rows) >= 1 and any(c.lower() == "id" for c in rows[0]) else rows
    ids: list[str] = []
    for row in body:
        if id_col < len(row):
            ids.append(row[id_col])
    return ids


def _lint_work_stream_text(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for WORK_STREAM.md content."""
    errors: list[str] = []
    warnings: list[str] = []
    sections = _split_work_stream_sections(text)
    if not sections:
        errors.append("no ## sections found in WORK_STREAM.md")
        return errors, warnings
    seen_ids: dict[str, str] = {}
    for heading, rows in sections:
        for work_id in _collect_work_stream_ids(rows):
            if not work_id:
                continue
            if work_id in seen_ids and seen_ids[work_id] != heading:
                errors.append(f"id '{work_id}' appears in both '{seen_ids[work_id]}' and '{heading}'")
            seen_ids.setdefault(work_id, heading)
        if not rows:
            warnings.append(f"section '{heading}' has no rows")
    return errors, warnings


def _verify_work_stream(cd: Path | None = None) -> list[str]:
    """Verify invariants in WORK_STREAM.md; return the list of errors (empty = OK)."""
    path = _resolve_work_stream_path(cd)
    if not path.exists():
        return [f"work-stream document not found: {path}"]
    text = path.read_text(encoding="utf-8")
    errors, _ = _lint_work_stream_text(text)
    return errors


def _normalize_work_stream_text(text: str) -> tuple[str, list[str]]:
    """Return (rewritten-text, list-of-changes) for WORK_STREAM.md.

    The current contract is idempotent: dedupe consecutive blank lines so that
    each ``## `` section boundary is followed by exactly one blank line.
    """
    lines = text.splitlines()
    rewritten: list[str] = []
    changes: list[str] = []
    blank_streak = False
    for line in lines:
        if line.strip() == "":
            if not blank_streak:
                rewritten.append(line)
            blank_streak = True
            continue
        blank_streak = False
        rewritten.append(line)
    new_text = "\n".join(rewritten)
    if new_text != text:
        changes.append("collapsed consecutive blank lines")
    return new_text, changes


def plan_verify_workstream_cmd(cd: Path | None = None, **_kwargs: Any) -> None:
    """WL-224: verify WORK_STREAM.md invariants (raise typer.Exit(1) on violations)."""
    errors = _verify_work_stream(cd)
    if errors:
        for err in errors:
            typer.echo(f"verify-workstream: {err}", err=True)
        raise typer.Exit(1) from None
    typer.echo("verify-workstream: OK")


def plan_lint_workstream_cmd(cd: Path | None = None, **_kwargs: Any) -> None:
    """WL-224: lint WORK_STREAM.md schema (errors exit 1, warnings report)."""
    path = _resolve_work_stream_path(cd)
    if not path.exists():
        typer.echo(f"lint-workstream: file not found: {path}", err=True)
        raise typer.Exit(1) from None
    text = path.read_text(encoding="utf-8")
    errors, warnings = _lint_work_stream_text(text)
    for warn in warnings:
        typer.echo(f"lint-workstream: warning: {warn}")
    if errors:
        for err in errors:
            typer.echo(f"lint-workstream: error: {err}", err=True)
        raise typer.Exit(1) from None
    typer.echo("lint-workstream: OK")


def plan_normalize_workstream_cmd(cd: Path | None = None, **_kwargs: Any) -> None:
    """WL-225: normalize WORK_STREAM.md (idempotent; reports changes)."""
    path = _resolve_work_stream_path(cd)
    if not path.exists():
        typer.echo(f"normalize-workstream: file not found: {path}", err=True)
        raise typer.Exit(1) from None
    text = path.read_text(encoding="utf-8")
    new_text, changes = _normalize_work_stream_text(text)
    if changes:
        path.write_text(new_text, encoding="utf-8")
    for change in changes:
        typer.echo(f"normalize-workstream: {change}")
    typer.echo("normalize-workstream: done")


__all__ = [
    "dag_validate_cmd",
    "dag_list_cmd",
    "dag_add_cmd",
    "dag_remove_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_update_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "plan_incorporate_cmd",
    "plan_claim_cmd",
    "plan_complete_cmd",
    "plan_wait_next_cmd",
    "plan_do_next_cmd",
    "plan_get_next_cmd",
    "plan_lint_workstream_cmd",
    "plan_loop_cmd",
    "plan_normalize_workstream_cmd",
    "plan_progress_cmd",
    "plan_verify_workstream_cmd",
    "plan_wait_next_cmd",
    "closure_pack_cmd",
    "dag_run_cmd",
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
    "workstream_query_cmd",
    "workstream_stats_cmd",
    "workstream_dashboard_cmd",
    "workstream_launch_cmd",
    "workstream_dependencies_cmd",
]  # noqa: E501
