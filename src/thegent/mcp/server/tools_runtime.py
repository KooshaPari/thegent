"""Runtime/config/status tool handlers for MCP server."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable

from fastmcp.tools.tool import ToolResult


def _sanitize_config_value(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sanitize_config_value(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_config_value(i) for i in obj]
    if hasattr(obj, "__str__") and not isinstance(obj, (int, float, bool, str, type(None))):
        return str(obj)
    return obj


def config_resolve_impl(
    *,
    tenant_id: str | None,
    session_id: str | None,
    overrides: dict[str, Any] | None,
    keys: list[str] | None,
) -> str:
    from thegent.config_provider import get_config_provider

    provider = get_config_provider()
    config = provider.resolve(tenant_id=tenant_id, session_id=session_id, request_overrides=overrides, keys=keys)
    return json.dumps(_sanitize_config_value(config), indent=2)


def negotiate_contract_impl(
    *,
    contract_id: str,
    supported_versions: list[str],
    session_contract_negotiate_impl: Callable[[str, list[str]], dict[str, Any]],
) -> str:
    res = session_contract_negotiate_impl(contract_id, supported_versions)
    return json.dumps(res, indent=2)


def ps_tool_impl(
    *,
    owner: str | None,
    all: bool,
    include_contract: bool,
    ps_impl: Callable[..., list[dict[str, Any]]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = ps_impl(owner=owner, all=all, include_contract=include_contract)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content={"sessions": result},
        meta={"execution_time_ms": elapsed_ms},
    )


def status_tool_impl(
    *,
    session_id: str,
    include_contract: bool,
    status_impl: Callable[..., dict[str, Any]],
    log: logging.Logger,
) -> ToolResult:
    log.info("thegent_status session_id=%s", session_id)
    start_time = time.perf_counter()
    result = status_impl(session_id=session_id, include_contract=include_contract)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


def logs_tool_impl(
    *,
    session_id: str,
    tail: int | None,
    stderr: bool,
    logs_impl: Callable[..., str],
    log: logging.Logger,
) -> ToolResult:
    log.info("thegent_logs session_id=%s tail=%s", session_id, tail)
    start_time = time.perf_counter()
    result = logs_impl(session_id=session_id, tail=tail, stderr=stderr)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=result,
        structured_content={"logs": result, "session_id": session_id, "tail": tail, "stderr": stderr},
        meta={"execution_time_ms": elapsed_ms},
    )
