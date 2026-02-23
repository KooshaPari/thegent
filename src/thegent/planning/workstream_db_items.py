"""Item transformation helpers for workstream DB."""

import contextlib
import orjson as json
from typing import Any


def parse_meta_json(meta_json: str | None) -> dict[str, Any]:
    """Parse metadata JSON payload into a dict."""
    meta: dict[str, Any] = {}
    if meta_json:
        with contextlib.suppress(Exception):
            meta = json.loads(meta_json) or {}
    return meta


def build_prompt_suggestion(source_system: str, item_id: str, title: str, meta: dict[str, Any]) -> str:
    """Build prompt suggestion string from canonical source metadata."""
    if source_system == "PROMPT_QUEUE":
        return title
    if source_system == "ESCALATION":
        return f"Resolve escalation {meta.get('run_id', item_id)}: {meta.get('reason', '')}"
    if source_system == "DEFERRAL":
        return f"Resume deferred {meta.get('run_id', meta.get('task_id', item_id))}"
    if source_system == "AGILEPLUS":
        return f"Address finding {meta.get('finding_id', '')}: {title}"
    return f"Complete {item_id}: {title}"


def build_next_item(
    item_id: str,
    title: str,
    source_system: str,
    priority: str,
    meta: dict[str, Any],
) -> dict[str, Any]:
    """Build do_next payload shape for queue/workstream consumers."""
    item = {
        "id": item_id,
        "description": title[:80] + ("..." if len(title) > 80 else ""),
        "source": source_system,
        "priority": priority,
        "prompt_suggestion": build_prompt_suggestion(source_system, item_id, title, meta),
        **{k: v for k, v in meta.items() if k in ("queue_item_id", "run_id", "task_id", "project", "backlog_item_id")},
    }
    if meta.get("queue_item_id") is not None:
        item["queue_item_id"] = meta["queue_item_id"]
    if meta.get("run_id"):
        item["run_id"] = meta["run_id"]
    if meta.get("task_id"):
        item["task_id"] = meta["task_id"]
    if meta.get("finding_id"):
        item["backlog_item_id"] = item_id.replace("backlog-", "")
    return item
