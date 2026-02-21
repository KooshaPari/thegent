"""Helper utilities for session command presentation and shared parsing."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    EXIT_TIMEOUT,
    _export_format_from_suffix,
    _infer_export_format,
    _is_pid_running,
    _safe_dict,
    get_exit_message,
)


def parse_sources_csv(sources: str | None) -> tuple[str, ...]:
    """Parse comma-separated source names into a normalized tuple."""
    raw = sources or "registry,escalation"
    return tuple(s.strip() for s in raw.split(",") if s.strip())


def render_ps_markdown(*, console: Any, rows: list[dict[str, Any]], include_contract: bool) -> None:
    """Render session rows in markdown format."""
    console.print("## Thegent Sessions")
    headers = "| id | agent | owner | pid | status | rss | vsz | prompt |"
    separator = "|----|-------|-------|-----|--------|-----|-----|--------|"
    if include_contract:
        headers = "| id | agent | owner | pid | status | rss | vsz | prompt | route_request | route_contract |"
        separator = "|----|-------|-------|-----|--------|-----|-----|--------|--------------|----------------|"
    console.print(headers)
    console.print(separator)
    for row in rows:
        base = (
            f"| {row['id']} | {row['agent']} | {row['owner']} | {row['pid']} | {row['status']} | "
            f"{row.get('rss', '—')} | {row.get('vsz', '—')} | {row['prompt_preview']} |"
        )
        if include_contract:
            route_request = row.get("route_request")
            route_contract = row.get("route_contract")
            base += f" {json.dumps(route_request) if route_request is not None else '—'} | "
            base += f"{json.dumps(route_contract) if route_contract is not None else '—'} |"
        console.print(base)


def render_ps_rich_table(*, console: Any, rows: list[dict[str, Any]], include_contract: bool) -> None:
    """Render session rows in rich table format."""
    table = Table(title="Thegent Sessions")
    table.add_column("Session")
    table.add_column("Agent")
    table.add_column("Owner")
    table.add_column("PID")
    table.add_column("Status")
    table.add_column("RSS")
    table.add_column("VSZ")
    table.add_column("Prompt")
    table.add_column("Started")
    has_contract_columns = False
    if include_contract and any(
        (row.get("route_contract") is not None or row.get("route_request") is not None) for row in rows
    ):
        table.add_column("Requested Model")
        table.add_column("Requested Provider")
        table.add_column("Resolved Alias")
        has_contract_columns = True

    for row in rows:
        row_data = [
            str(row["id"]),
            str(row["agent"]),
            str(row["owner"]),
            str(row["pid"]),
            str(row["status"]),
            str(row.get("rss", "—")),
            str(row.get("vsz", "—")),
            str(row["prompt_preview"]),
            str(row.get("started_at_utc", "")),
        ]
        if has_contract_columns:
            row_data.extend(["", "", ""])
        table.add_row(*row_data)
        if has_contract_columns:
            route_req: dict[str, Any] = row.get("route_request") or {}
            requested_model = route_req.get("requested_model", "—")
            requested_provider = route_req.get("requested_provider_hint", "—")
            resolved_alias = route_req.get(
                "resolved_model_alias",
                route_req.get("resolved_alias", "—"),
            )
            table.add_row(
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                str(requested_model),
                str(requested_provider),
                str(resolved_alias),
            )
    console.print(table)


def resolve_export_format_with_notice(*, output: Path, export_format: str | None, console: Any) -> str:
    """Infer export format and print extension compatibility note when needed."""
    chosen_format = export_format or _infer_export_format(output, fallback="json")
    if export_format is None and output.suffix and _export_format_from_suffix(output.suffix) is None:
        console.print(
            f"Note: output path extension '{output.suffix}' is not recognized for export; "
            f"defaulting to '{chosen_format}'."
        )
    return chosen_format


def follow_log_stream(*, target: Path, pid: int, timeout: int, poll_seconds: float, console: Any) -> None:
    """Stream log updates with timeout and process-state checks."""
    end_time = time.time() + timeout if timeout > 0 else None
    pos = target.stat().st_size
    while True:
        running = _is_pid_running(pid)
        if (
            (timeout > 0 and end_time is not None and time.time() >= end_time)
            and not running
            and pos >= target.stat().st_size
        ):
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. "
                "Session may have exited; check logs separately.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                pass
            raise typer.Exit(EXIT_TIMEOUT)

        if not target.exists():
            return
        size = target.stat().st_size
        if size < pos:
            pos = 0

        if size > pos:
            with target.open("r", encoding="utf-8", errors="replace") as file_obj:
                file_obj.seek(pos)
                chunk = file_obj.read()
                pos = file_obj.tell()
            if chunk:
                for line in chunk.splitlines():
                    console.print(line)
            continue

        if not running:
            return

        if end_time is not None and time.time() >= end_time:
            console.print(
                f"[yellow]Operation timed out: logs follow exceeded {timeout}s. Session may still be running.[/yellow]"
            )
            if msg := get_exit_message(EXIT_TIMEOUT):
                pass
            raise typer.Exit(EXIT_TIMEOUT)

        time.sleep(poll_seconds)


def print_high_session_count_tip(*, console: Any, rows: list[dict[str, Any]]) -> None:
    """Print operator hint when many sessions are listed."""
    if len(rows) > 5:
        console.print("\n[yellow]Tip: High session count detected.[/yellow]")
        console.print("[dim]Multiple active agent sessions spawn redundant language servers (Node.js).[/dim]")
        console.print(
            "[dim]Use 'thegent stop <session_id>' to kill orphan processes and free up 1-2GB RAM per session.[/dim]"
        )
        console.print("[dim]Run 'thegent mcp spotlight-exclude' to reduce mds_stores overhead on macOS.[/dim]")


def enrich_status_out(
    *,
    session_id: str | None,
    status: str,
    running: bool,
    pid: int,
    meta: dict[str, Any],
    include_contract: bool,
) -> dict[str, Any]:
    """Build status payload dict with optional contract details."""
    out = {
        "session_id": session_id,
        "status": status,
        "running": running,
        "pid": pid,
        "owner": meta.get("owner", ""),
        "host": meta.get("host"),
        "agent": meta.get("agent"),
        "mode": meta.get("mode"),
        "cwd": meta.get("cwd"),
        "started_at_utc": meta.get("started_at_utc"),
        "ended_at_utc": meta.get("ended_at_utc"),
        "duration_seconds": meta.get("duration_seconds"),
        "timed_out": meta.get("timed_out", False),
        "paths": meta.get("paths", {}),
    }
    if include_contract:
        out["route_contract"] = meta.get("route_contract")
        out["route_request"] = meta.get("route_request")
    return out


def latest_issue_types_count(result: dict[str, Any], latest: dict[str, Any] | None) -> int:
    """Compute fallback count for latest issue types."""
    explicit = result.get("latest_issue_types_count")
    if isinstance(explicit, int):
        return explicit
    issue_types = _safe_dict(latest).get("issue_types", [])
    if isinstance(issue_types, list):
        return len(issue_types)
    return 0


__all__ = [
    "enrich_status_out",
    "follow_log_stream",
    "latest_issue_types_count",
    "parse_sources_csv",
    "print_high_session_count_tip",
    "render_ps_markdown",
    "render_ps_rich_table",
    "resolve_export_format_with_notice",
]
