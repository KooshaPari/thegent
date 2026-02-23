"""Session resource handlers for MCP server."""

from __future__ import annotations

import orjson as json
from typing import Any, Callable


def resource_sessions_impl(
    *,
    include_contract: bool,
    ps_impl: Callable[..., list[dict[str, Any]]],
) -> str:
    return json.dumps(ps_impl(owner=None, all=True, include_contract=include_contract).decode())


def resource_session_meta_impl(
    *,
    session_id: str,
    include_contract: bool,
    status_impl: Callable[..., dict[str, Any]],
) -> str:
    return json.dumps(status_impl(session_id=session_id, include_contract=include_contract).decode())


def resource_session_logs_impl(
    *,
    session_id: str,
    stderr: bool,
    tail: int | None,
    logs_impl: Callable[..., str | None],
) -> str:
    return logs_impl(session_id=session_id, tail=tail, stderr=stderr) or ""
