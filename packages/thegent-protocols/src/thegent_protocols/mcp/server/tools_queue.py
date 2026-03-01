"""Queue tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
from pathlib import Path

from fastmcp.tools.tool import ToolResult


def queue_list_impl(
    *,
    session_dir: Path,
    include_done: bool,
    include_expired: bool,
    limit: int | None,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    items = pq.list_all(include_done=include_done, include_expired=include_expired, limit=limit)
    return ToolResult(
        content=json.dumps(items).decode(),
        structured_content=items,
        meta={"count": len(items)},
    )


def queue_claim_impl(
    *,
    session_dir: Path,
    claimer_id: str,
    project: str | None,
    lease_seconds: int,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    claimed = pq.claim(claimer_id=claimer_id, lease_seconds=lease_seconds, project=project)
    if claimed is None:
        return ToolResult(
            content=json.dumps({"claimed": None}).decode(),
            structured_content={"claimed": None},
            meta={"error": "No pending items"},
        )
    return ToolResult(
        content=json.dumps(claimed).decode(),
        structured_content=claimed,
        meta={"claimed": True},
    )


def queue_done_impl(
    *,
    session_dir: Path,
    item_id: int,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    ok = pq.done(item_id)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}).decode(),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


def queue_add_impl(
    *,
    session_dir: Path,
    prompt: str,
    project: str,
    agent: str | None,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    count = pq.append(prompt=prompt, project=project, agent=agent)
    return ToolResult(
        content=json.dumps({"success": True, "pending_count": count}).decode(),
        structured_content={"success": True, "pending_count": count},
        meta={},
    )


def queue_edit_impl(
    *,
    session_dir: Path,
    item_id: int,
    prompt: str,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    ok = pq.edit(item_id=item_id, prompt=prompt)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}).decode(),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


def queue_release_impl(
    *,
    session_dir: Path,
    item_id: int,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    ok = pq.release(item_id)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}).decode(),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


def queue_extend_lease_impl(
    *,
    session_dir: Path,
    item_id: int,
    lease_seconds: int,
) -> ToolResult:
    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(session_dir)
    ok = pq.extend_lease(item_id=item_id, lease_seconds=lease_seconds)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}).decode(),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )
