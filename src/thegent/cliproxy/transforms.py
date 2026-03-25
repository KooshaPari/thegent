"""Pure transformation functions for CLI Proxy operations.

Extractable functions that don't depend on ThegentSettings or external services.
These can be used by both thegent and standalone CLI tools.
"""

import hashlib
from typing import Any, Optional


def transform_models_response(response: dict[str, Any]) -> dict[str, Any]:
    """Transform models API response to standard format."""
    data = response.get("data", [])
    transformed_data = []
    for model in data:
        transformed_model = {
            "id": model.get("id"),
            "object": "model",
            "created": model.get("created", 0),
            "owned_by": model.get("owned_by", "unknown"),
        }
        transformed_data.append(transformed_model)
    return {"object": "list", "data": transformed_data}


def _compute_models_etag(models: list[dict[str, Any]]) -> str:
    """Compute ETag for models list."""
    sorted_ids = sorted(m.get("id", "") for m in models)
    data = ",".join(sorted_ids)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _extract_delta_content(delta: dict[str, Any]) -> str:
    """Extract content from a delta message."""
    return delta.get("content", "")


def _extract_delta_tool_calls(delta: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract tool calls from a delta message."""
    return delta.get("tool_calls", [])


def _extract_usage(completion: dict[str, Any]) -> dict[str, int]:
    """Extract usage statistics from completion response."""
    usage = completion.get("usage", {})
    return {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def _map_model_for_backend(model: str) -> str:
    """Map model name to backend identifier."""
    # Handle common model aliases
    mappings = {
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "claude-3-5-sonnet": "claude-sonnet-20241022",
        "claude-3-5-haiku": "claude-haiku-20240307",
    }
    return mappings.get(model.lower(), model)


def _process_sse_line(line: str) -> Optional[dict[str, Any]]:
    """Process a Server-Sent Events line."""
    if not line.startswith("data: "):
        return None
    data = line[6:].strip()
    if data == "[DONE]":
        return {"done": True}
    import json

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def _responses_to_chat_completions(response: dict[str, Any]) -> dict[str, Any]:
    """Convert responses API format to chat completions format."""
    choices = []
    for i, result in enumerate(response.get("results", [])):
        choice = {
            "index": i,
            "message": {
                "role": "assistant",
                "content": result.get("output", [{}])[0].get("text", ""),
            },
            "finish_reason": result.get("status", "stop"),
        }
        choices.append(choice)
    return {
        "id": response.get("id", "chatcmpl-unknown"),
        "object": "chat.completion",
        "created": response.get("created_at", 0),
        "model": response.get("model", "unknown"),
        "choices": choices,
    }


def extract_websocket_forward_headers(headers: dict[str, str]) -> dict[str, str]:
    """Extract headers to forward for WebSocket connection."""
    forward = {}
    for key in ("authorization", "x-api-key", "x-request-id"):
        if key in headers:
            forward[key] = headers[key]
    return forward


def filter_inbound_response_headers(headers: dict[str, str]) -> dict[str, str]:
    """Filter response headers for outbound forwarding."""
    # Remove hop-by-hop headers
    remove = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
    return {k: v for k, v in headers.items() if k.lower() not in remove}


def sanitize_outbound_request_headers(headers: dict[str, str]) -> dict[str, str]:
    """Sanitize outbound request headers."""
    # Remove headers that should be set by the proxy
    remove = {"host", "connection", "content-length"}
    return {k: v for k, v in headers.items() if k.lower() not in remove}


class ResponsesStreamState:
    """State tracker for responses API streaming."""

    def __init__(self) -> None:
        self.content: str = ""
        self.tool_calls: list[dict[str, Any]] = []
        self.usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def update(self, delta: dict[str, Any]) -> None:
        """Update state with a delta."""
        if text := delta.get("content"):
            self.content += text
        if tc := delta.get("tool_calls"):
            self.tool_calls.extend(tc)
        if usage := delta.get("usage"):
            self.usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            self.usage["completion_tokens"] += usage.get("completion_tokens", 0)
            self.usage["total_tokens"] += usage.get("total_tokens", 0)

    def get_result(self) -> dict[str, Any]:
        """Get final result from state."""
        return {
            "content": self.content,
            "tool_calls": self.tool_calls,
            "usage": self.usage,
        }


__all__ = [
    "ResponsesStreamState",
    "_compute_models_etag",
    "_extract_delta_content",
    "_extract_delta_tool_calls",
    "_extract_usage",
    "_map_model_for_backend",
    "_process_sse_line",
    "_responses_to_chat_completions",
    "extract_websocket_forward_headers",
    "filter_inbound_response_headers",
    "sanitize_outbound_request_headers",
    "transform_models_response",
]
