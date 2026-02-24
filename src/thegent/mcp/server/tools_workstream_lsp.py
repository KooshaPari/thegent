"""Workstream and LSP tool handlers for MCP server."""

from __future__ import annotations

import orjson as json
import time
from collections.abc import Callable
from typing import Any

from fastmcp.tools.tool import ToolResult

_BACKEND_UNAVAILABLE_PREFIX = "LSP_BACKEND_UNAVAILABLE:"


def _lsp_error_remediation(error_message: str, default: str) -> str:
    if error_message.startswith(_BACKEND_UNAVAILABLE_PREFIX):
        lowered = error_message.lower()
        if "unsupported" in lowered:
            return (
                "THGENT_LSP_ADAPTER is set to an unsupported value. "
                "Set THGENT_LSP_ADAPTER=python-ast for Python files, or unset the variable to use default detection."
            )
        return (
            "No LSP backend is available for this request. Configure THGENT_LSP_ADAPTER=python-ast for Python files, "
            "or provision/register an adapter for this file type. If this is a non-Python file, verify your backend "
            "supports the language and that the file extension is recognized."
        )
    return default


def workstream_claim_tool_impl(
    *,
    item_id: str,
    agent_id: str,
    claim_impl: Callable[[str, str], dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = claim_impl(item_id, agent_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


def lsp_diagnostics_tool_impl(
    *,
    file_path: str,
    diagnostics_impl: Callable[[str], dict[str, Any]],
    error_result: Callable[..., ToolResult],
) -> ToolResult:
    started = time.time()
    try:
        payload = diagnostics_impl(file_path)
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": int((time.time() - started) * 1000)},
        )
    except Exception as exc:
        error_message = str(exc)
        remediation = _lsp_error_remediation(error_message, "Provide a valid file path and configure an LSP adapter.")
        return error_result(error_message, remediation)


def lsp_symbol_lookup_tool_impl(
    *,
    symbol_name: str,
    file_path: str | None,
    symbol_lookup_impl: Callable[[str, str | None], dict[str, Any]],
    error_result: Callable[..., ToolResult],
) -> ToolResult:
    started = time.time()
    try:
        payload = symbol_lookup_impl(symbol_name, file_path)
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": int((time.time() - started) * 1000)},
        )
    except Exception as exc:
        error_message = str(exc)
        remediation = _lsp_error_remediation(error_message, "Provide a non-empty symbol and optional valid file path.")
        return error_result(error_message, remediation)


def lsp_hover_tool_impl(
    *,
    file_path: str,
    line: int,
    character: int,
    hover_impl: Callable[[str, int, int], dict[str, Any]],
    error_result: Callable[..., ToolResult],
) -> ToolResult:
    started = time.time()
    try:
        payload = hover_impl(file_path, line, character)
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": int((time.time() - started) * 1000)},
        )
    except Exception as exc:
        error_message = str(exc)
        remediation = _lsp_error_remediation(
            error_message,
            "Provide a valid file path and non-negative line/character coordinates.",
        )
        return error_result(
            error_message,
            remediation,
        )


def workstream_complete_tool_impl(
    *,
    item_id: str,
    agent_id: str,
    complete_impl: Callable[[str, str], dict[str, Any]],
) -> ToolResult:
    start_time = time.perf_counter()
    result = complete_impl(item_id, agent_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )
