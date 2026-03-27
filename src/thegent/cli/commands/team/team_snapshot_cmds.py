"""Thegent CLI session snapshot commands (extracted from team_cmds.py)."""

# @trace WL-124
from __future__ import annotations

import inspect
import orjson as json
import sys
import typing
from pathlib import Path
from typing import Any, cast


from thegent.cli.commands._cli_shared import (
    _normalize_output_format,
    console,
)


def _snapshot_payload_kwargs(
    payload_fn: typing.Callable[..., dict[str, object]],  # noqa: ANN001
    *,
    scraper: object,
    limit: int,
    out_path: Path | None = None,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> dict[str, object]:
    """Build a compatible kwargs dict from a payload function signature."""
    signature = inspect.signature(payload_fn)
    params = signature.parameters

    payload_kwargs: dict[str, object] = {}
    if "limit" in params:
        payload_kwargs["limit"] = int(limit)
    if "out_path" in params:
        payload_kwargs["out_path"] = str(out_path) if out_path is not None else None
    if "trigger" in params:
        payload_kwargs["trigger"] = trigger
    if "tag" in params:
        payload_kwargs["tag"] = tag
    if "since" in params:
        payload_kwargs["since"] = since

    return payload_fn(scraper, **payload_kwargs)


def snapshot_list_cmd(
    project: Path | None = None,
    limit: int = 50,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
    format: str | None = None,
) -> None:
    """List persisted session snapshots with optional filters."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_list_payload

    project_path = project or Path.cwd()
    payload = snapshot_list_payload(
        SessionScraper(project_path),
        limit=limit,
        trigger=trigger,
        tag=tag,
        since=since,
    )

    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[bold cyan]Snapshots[/bold cyan]: {payload.get('count', 0)}")
    for item in payload.get("items", []):
        console.print(f"- {item.get('captured_at', '?')} [{item.get('trigger', '?')}] {item.get('path')}")


def snapshot_index_cmd(
    project: Path | None = None,
    limit: int = 200,
    format: str | None = None,
) -> None:
    """Show snapshot index analytics payload."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_index_payload

    project_path = project or Path.cwd()
    payload = snapshot_index_payload(SessionScraper(project_path), limit=limit)
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[bold cyan]Snapshot Index[/bold cyan]: {payload.get('total_snapshots', 0)} snapshots")
    console.print(f"[dim]Top tags: {', '.join(payload.get('top_tags', [])) or '(none)'}[/dim]")


def snapshot_export_cmd(
    snapshot_path: Path,
    project: Path | None = None,
    out_path: Path | None = None,
    format: str | None = None,
) -> None:
    """Export one snapshot JSON to markdown."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_export_payload

    project_path = project or Path.cwd()
    payload = snapshot_export_payload(
        SessionScraper(project_path),
        snapshot_path=str(snapshot_path),
        out_path=str(out_path) if out_path else None,
    )
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[green]Exported[/green] {payload['source']} -> {payload['output']}")


def snapshot_prune_cmd(
    project: Path | None = None,
    max_keep: int = 500,
    format: str | None = None,
) -> None:
    """Prune old snapshots beyond the keep limit."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_prune_payload

    project_path = project or Path.cwd()
    payload = snapshot_prune_payload(SessionScraper(project_path), max_keep=max_keep)
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[yellow]Pruned[/yellow] {payload.get('deleted', 0)} snapshot(s)")


def snapshot_meta_cmd(
    project: Path | None = None,
    limit: int = 500,
    format: str | None = None,
) -> None:
    """Show available trigger and tag metadata from snapshots."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_triggers_tags_payload

    project_path = project or Path.cwd()
    payload = snapshot_triggers_tags_payload(SessionScraper(project_path), limit=limit)
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(f"[bold]Triggers[/bold]: {', '.join(payload.get('triggers', [])) or '(none)'}")
    console.print(f"[bold]Tags[/bold]: {', '.join(payload.get('tags', [])) or '(none)'}")


def snapshot_daily_index_cmd(
    project: Path | None = None,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
    format: str | None = None,
) -> None:
    """Show daily snapshot aggregation payload."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_daily_index_payload

    project_path = project or Path.cwd()
    scraper = SessionScraper(project_path)
    payload_raw = _snapshot_payload_kwargs(
        snapshot_daily_index_payload,
        scraper=scraper,
        limit=limit,
        trigger=trigger,
        tag=tag,
        since=since,
    )
    payload = cast("dict[str, typing.Any]", payload_raw)
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    days_list = cast("list[Any]", payload.get("days", []))
    console.print(f"[bold cyan]Snapshot Daily Index[/bold cyan]: {len(days_list)} day(s)")
    for day_payload in days_list:
        snapshots = day_payload.get("snapshots") if "snapshots" in day_payload else day_payload.get("count", 0)
        console.print(
            f"- {day_payload.get('day')}: snapshots={snapshots} latest={day_payload.get('latest_captured_at') or '?'}"
        )


def snapshot_daily_totals_cmd(
    project: Path | None = None,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
    format: str | None = None,
) -> None:
    """Show lightweight daily aggregate totals for snapshots."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_daily_totals_payload

    project_path = project or Path.cwd()
    scraper = SessionScraper(project_path)
    payload = _snapshot_payload_kwargs(
        snapshot_daily_totals_payload,
        scraper=scraper,
        limit=limit,
        trigger=trigger,
        tag=tag,
        since=since,
    )
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    payload_dict = cast("dict[str, Any]", payload)
    console.print(
        "[bold cyan]Snapshot Daily Totals[/bold cyan] "
        f"days={payload_dict.get('total_days', 0)} snapshots={payload_dict.get('total_snapshots', 0)} "
        f"prompts={payload_dict.get('total_prompts', 0)} commands={payload_dict.get('total_commands', 0)} "
        f"files={payload_dict.get('total_files', 0)}"
    )
    if payload_dict.get("filters"):
        console.print(f"[dim]Filters:[/dim] {payload_dict['filters']}")
    if payload_dict.get("generated_at"):
        console.print(f"[dim]Generated:[/dim] {payload_dict['generated_at']}")


def snapshot_daily_export_cmd(
    project: Path | None = None,
    out_dir: Path | None = None,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
    format: str | None = None,
) -> None:
    """Export daily snapshot index (JSON + Markdown)."""
    from thegent.orchestration.state.session_scraper import SessionScraper
    from thegent.orchestration.state.session_snapshot_cli_helpers import snapshot_daily_export_payload

    project_path = project or Path.cwd()
    scraper = SessionScraper(project_path)
    payload = _snapshot_payload_kwargs(
        snapshot_daily_export_payload,
        scraper=scraper,
        limit=limit,
        out_path=out_dir,
        trigger=trigger,
        tag=tag,
        since=since,
    )
    if _normalize_output_format(format) == "json":
        sys.stdout.write(json.dumps(payload).decode() + "\n")
        return
    console.print(
        f"[green]Daily index exported[/green] json={payload.get('source_json')} md={payload.get('source_md')}"
    )


__all__ = [
    "snapshot_daily_export_cmd",
    "snapshot_daily_index_cmd",
    "snapshot_daily_totals_cmd",
    "snapshot_export_cmd",
    "snapshot_index_cmd",
    "snapshot_list_cmd",
    "snapshot_meta_cmd",
    "snapshot_prune_cmd",
]
