"""Payload helpers for snapshot CLI commands."""

from __future__ import annotations

import orjson as json
from collections.abc import Iterable
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Protocol, cast


def _normalized_limit(value: int) -> int:
    return max(0, int(value))


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _list_snapshot_paths(
    scraper: Any,
    *,
    limit: int,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> tuple[list[Any], bool]:
    list_snapshots = getattr(scraper, "list_snapshots", None)
    if not callable(list_snapshots):
        return ([], False)

    def _coerce_snapshot_paths(result: object) -> list[Any]:
        if isinstance(result, list):
            return result
        if isinstance(result, Iterable):
            return list(result)
        return []

    kwargs: dict[str, Any] = {
        "limit": _normalized_limit(limit),
        "trigger": trigger,
        "tag": tag,
    }
    if since is not None:
        try:
            return (_coerce_snapshot_paths(list_snapshots(**kwargs, since=since)), True)
        except TypeError:
            pass
    return (_coerce_snapshot_paths(list_snapshots(**kwargs)), False)


def _load_snapshot_like(scraper: Any, path: Any) -> Any | None:
    load_snapshot = getattr(scraper, "load_snapshot", None)
    if callable(load_snapshot):
        return load_snapshot(path)

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return type("SnapshotLike", (), data)()


def snapshot_list_payload(
    scraper: Any,
    limit: int = 50,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    paths, since_applied_by_scraper = _list_snapshot_paths(
        scraper,
        limit=limit,
        trigger=trigger,
        tag=tag,
        since=since,
    )
    since_dt = _parse_iso_datetime(since)
    items: list[dict[str, Any]] = []
    for path in paths:
        snapshot = _load_snapshot_like(scraper, path)
        if snapshot is None:
            continue
        if not since_applied_by_scraper and since_dt is not None:
            captured_at = _parse_iso_datetime(getattr(snapshot, "captured_at", None))
            if captured_at is None or captured_at < since_dt:
                continue
        items.append(
            {
                "path": str(path),
                "trigger": snapshot.trigger,
                "captured_at": snapshot.captured_at,
                "tags": list(snapshot.tags),
            }
        )
    return {"count": len(items), "items": items}


def snapshot_index_payload(scraper: Any, limit: int = 200) -> dict[str, Any]:
    summary = scraper.summarize_snapshots(limit=_normalized_limit(limit))
    tag_counts = summary.get("tag_counts", {})
    ranked_tags = sorted(tag_counts.items(), key=lambda item: (-int(item[1]), str(item[0])))
    summary["top_tags"] = [str(tag) for tag, _count in ranked_tags[:10]]
    return summary


def snapshot_daily_index_payload(
    scraper: Any,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    paths, _ = _list_snapshot_paths(scraper, limit=limit, trigger=trigger, tag=tag, since=since)
    daily_counts_from_scraper: dict[str, dict[str, int]] = {}
    summarize_by_day = getattr(scraper, "summarize_snapshots_by_day", None)
    if callable(summarize_by_day):
        try:
            raw = summarize_by_day(limit=_normalized_limit(limit))
            if isinstance(raw, dict):
                for day, counts in raw.items():
                    if isinstance(counts, dict):
                        daily_counts_from_scraper[str(day)] = {
                            "snapshots": int(counts.get("snapshots", 0) or 0),
                            "prompts": int(counts.get("prompts", 0) or 0),
                            "commands": int(counts.get("commands", 0) or 0),
                            "files": int(counts.get("files", 0) or 0),
                        }
        except TypeError:
            pass

    days_index: dict[str, dict[str, Any]] = {}

    for path in paths:
        snapshot = _load_snapshot_like(scraper, path)
        if snapshot is None:
            continue
        captured_at = str(getattr(snapshot, "captured_at", "") or "")
        day = captured_at[:10] if len(captured_at) >= 10 else Path(path).parent.name
        if not day:
            continue

        day_item = days_index.setdefault(
            day,
            {
                "day": day,
                "count": 0,
                "snapshots": 0,
                "prompts": 0,
                "commands": 0,
                "files": 0,
                "trigger_counts": {},
                "tag_counts": {},
                "latest_captured_at": None,
            },
        )
        day_item["count"] += 1
        day_item["snapshots"] += 1

        snapshot_trigger = str(getattr(snapshot, "trigger", "") or "").strip()
        if snapshot_trigger:
            trigger_counts = day_item["trigger_counts"]
            trigger_counts[snapshot_trigger] = int(trigger_counts.get(snapshot_trigger, 0)) + 1

        for raw_tag in list(getattr(snapshot, "tags", []) or []):
            snapshot_tag = str(raw_tag).strip()
            if not snapshot_tag:
                continue
            tag_counts = day_item["tag_counts"]
            tag_counts[snapshot_tag] = int(tag_counts.get(snapshot_tag, 0)) + 1

        latest_captured_at = day_item["latest_captured_at"]
        if isinstance(latest_captured_at, str):
            day_item["latest_captured_at"] = max(latest_captured_at, captured_at)
        else:
            day_item["latest_captured_at"] = captured_at

    days = sorted(days_index.values(), key=lambda item: str(item.get("day", "")), reverse=True)
    for item in days:
        from_scraper = daily_counts_from_scraper.get(str(item.get("day", "")))
        if from_scraper:
            snapshots_value = from_scraper.get("snapshots")
            item["snapshots"] = int(snapshots_value if snapshots_value is not None else (item.get("count", 0) or 0))
            item["prompts"] = int(from_scraper.get("prompts", 0))
            item["commands"] = int(from_scraper.get("commands", 0))
            item["files"] = int(from_scraper.get("files", 0))
        item["trigger_counts"] = dict(sorted(item["trigger_counts"].items()))
        item["tag_counts"] = dict(sorted(item["tag_counts"].items(), key=lambda kv: (-int(kv[1]), str(kv[0]))))

    daily_summary = {
        "total_snapshots": sum(int(item["count"]) for item in days),
        "total_prompts": sum(int(item.get("prompts", 0) or 0) for item in days),
        "total_commands": sum(int(item.get("commands", 0) or 0) for item in days),
        "total_files": sum(int(item.get("files", 0) or 0) for item in days),
        "total_days": len(days),
        "days_count": len(days),
        "newest_day": days[0]["day"] if days else None,
        "oldest_day": days[-1]["day"] if days else None,
        "generated_at": datetime.now(tz=UTC).isoformat(),
    }
    if trigger is not None or tag is not None or since is not None:
        daily_summary["filters"] = {
            "trigger": trigger,
            "tag": tag,
            "since": since,
        }
    daily_lookup = {
        str(item.get("day")): {
            "snapshots": int(item.get("snapshots", item.get("count", 0)) or 0),
            "prompts": int(item.get("prompts", 0) or 0),
            "commands": int(item.get("commands", 0) or 0),
            "files": int(item.get("files", 0) or 0),
        }
        for item in days
    }
    payload = {"summary": daily_summary, "days": days, "daily": daily_lookup}
    if "filters" in daily_summary:
        payload["applied_filters"] = daily_summary["filters"]
    return payload


def snapshot_daily_totals_payload(
    scraper: Any,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    """Return only daily aggregate totals for lightweight CLI/report views."""
    payload = snapshot_daily_index_payload(scraper=scraper, limit=limit, trigger=trigger, tag=tag, since=since)
    summary = payload.get("summary", {})
    totals = {
        "total_days": int(summary.get("total_days", 0) or 0),
        "total_snapshots": int(summary.get("total_snapshots", 0) or 0),
        "total_prompts": int(summary.get("total_prompts", 0) or 0),
        "total_commands": int(summary.get("total_commands", 0) or 0),
        "total_files": int(summary.get("total_files", 0) or 0),
        "generated_at": summary.get("generated_at"),
    }
    if "filters" in summary:
        totals["filters"] = summary.get("filters")
        totals["applied_filters"] = summary.get("filters")
    return totals


def snapshot_daily_export_payload(
    scraper: Any,
    out_path: str | None = None,
    limit: int = 1000,
    trigger: str | None = None,
    tag: str | None = None,
    since: str | None = None,
) -> dict[str, Any]:
    payload = snapshot_daily_index_payload(scraper=scraper, limit=limit, trigger=trigger, tag=tag, since=since)

    if out_path:
        output_base = Path(out_path)
    else:
        output_base = Path(getattr(scraper, "default_snapshot_dir", Path.cwd())) / "snapshot-daily-index"

    if output_base.suffix:
        json_path = output_base.with_suffix(".json")
        md_path = output_base.with_suffix(".md")
    elif output_base.exists() and output_base.is_dir():
        json_path = output_base / "snapshot-daily-index.json"
        md_path = output_base / "snapshot-daily-index.md"
    else:
        json_path = output_base.with_suffix(".json")
        md_path = output_base.with_suffix(".md")

    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, option=json.OPT_INDENT_2).decode(), encoding="utf-8")

    lines = [
        "# Snapshot Daily Index",
        "",
        f"- Generated at: {payload['summary']['generated_at']}",
        f"- Total snapshots: {payload['summary']['total_snapshots']}",
        f"- Total prompts: {payload['summary']['total_prompts']}",
        f"- Total commands: {payload['summary']['total_commands']}",
        f"- Total files: {payload['summary']['total_files']}",
        f"- Total days: {payload['summary']['total_days']}",
        f"- Newest day: {payload['summary']['newest_day'] or '(none)'}",
        f"- Oldest day: {payload['summary']['oldest_day'] or '(none)'}",
        "",
        "## Days",
    ]
    days = payload.get("days", [])
    if days:
        lines.extend([f"- {item['day']}: {item['count']} snapshot(s)" for item in days])
    else:
        lines.append("- (none)")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    source_json = str(json_path)
    source_md = str(md_path)
    result: dict[str, Any] = {
        "source_json": source_json,
        "source_md": source_md,
        "json_path": source_json,
        "markdown_path": source_md,
    }
    filters = payload.get("summary", {}).get("filters")
    if isinstance(filters, dict):
        result["applied_filters"] = filters
    return result


def snapshot_export_payload(scraper: Any, snapshot_path: str, out_path: str | None = None) -> dict[str, Any]:
    source = Path(snapshot_path)
    try:
        output = scraper.export_snapshot_markdown(source, Path(out_path) if out_path else None)
    except (FileNotFoundError, ValueError, OSError):
        return {"source": str(source), "output": None}
    return {"source": str(source), "output": str(output)}


def snapshot_prune_payload(scraper: Any, max_keep: int = 500) -> dict[str, int]:
    keep = _normalized_limit(max_keep)

    class _PruneSnapshotsCallable(Protocol):
        def __call__(self, *, max_keep: int) -> int: ...

    prune_snapshots = getattr(scraper, "prune_snapshots", None)
    if callable(prune_snapshots):
        prune_snapshots_fn = cast("_PruneSnapshotsCallable", prune_snapshots)
        try:
            return {"deleted": int(prune_snapshots_fn(max_keep=keep))}
        except TypeError:
            pass

    snapshots, _ = _list_snapshot_paths(scraper, limit=1_000_000)
    deleted = 0
    for path in snapshots[keep:]:
        try:
            Path(path).unlink()
            deleted += 1
        except FileNotFoundError:
            continue
        except OSError:
            continue
    return {"deleted": deleted}


def snapshot_triggers_tags_payload(scraper: Any, limit: int = 500) -> dict[str, list[str]]:
    paths, _ = _list_snapshot_paths(scraper, limit=limit)
    triggers: set[str] = set()
    tags: set[str] = set()
    for path in paths:
        snapshot = _load_snapshot_like(scraper, path)
        if snapshot is None:
            continue
        if snapshot.trigger:
            triggers.add(str(snapshot.trigger))
        for tag in snapshot.tags:
            if tag:
                tags.add(str(tag))
    return {"triggers": sorted(triggers), "tags": sorted(tags)}
