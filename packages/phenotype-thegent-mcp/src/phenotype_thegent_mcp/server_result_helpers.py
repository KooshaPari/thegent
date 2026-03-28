"""Shared result helpers for MCP server tool/resource responses (WL-126)."""

from __future__ import annotations

import orjson as json
from typing import Any

from fastmcp.tools.tool import ToolResult


def stable_json(payload: Any) -> str:
    """Serialize dict/list payloads with stable key order for deterministic MCP transport."""
    return json.dumps(payload, sort_keys=True).decode().decode()


def error_result(
    error: str,
    remediation: str,
    exit_code: int = 1,
    extra: dict[str, Any] | None = None,
) -> ToolResult:
    """Return ToolResult with error, remediation, and structured_content (MCP-OPT §5)."""
    payload: dict[str, Any] = {"error": error, "remediation": remediation, "exit_code": exit_code}
    if extra:
        payload.update(extra)
    return ToolResult(
        content=json.dumps(payload).decode().decode(),
        structured_content=payload,
        meta={"execution_time_ms": 0},
    )


__all__ = ["error_result", "stable_json"]
