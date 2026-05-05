"""Server dispatch helpers for ACP request parsing and response formatting.

Provides utilities for parsing ACP payloads and formatting ACP responses.
"""

from __future__ import annotations

from typing import Any

import orjson


def parse_acp_payload(payload: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse an ACP payload JSON string.

    Args:
        payload: The JSON string payload to parse.

    Returns:
        A tuple of (context_dict, error). If parsing succeeds, error is None.
        If parsing fails, context is None and error contains the error message.
        Empty string returns an empty dict with no error.
    """
    if not payload:
        return {}, None

    try:
        data = orjson.loads(payload)
    except orjson.JSONDecodeError:
        return None, "Invalid payload JSON"

    if not isinstance(data, dict):
        return None, "expected object"

    return data, None


def format_acp_response(
    success: bool,
    agent_url: str,
    elapsed_ms: float,
    result: str = "",
    error: str | None = None,
) -> str:
    """Format an ACP response as JSON.

    Args:
        success: Whether the operation was successful.
        agent_url: URL of the agent that processed the request.
        elapsed_ms: Time taken to process in milliseconds.
        result: The result text (only used when success=True).
        error: Error message (only used when success=False).

    Returns:
        JSON string representing the ACP response.
    """
    response: dict[str, Any] = {
        "success": success,
        "agent_url": agent_url,
        "elapsed_ms": elapsed_ms,
    }

    response["result"] = result
    if not success:
        response["error"] = error or "Unknown error"

    return orjson.dumps(response).decode("utf-8")
