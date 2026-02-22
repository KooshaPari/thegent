from __future__ import annotations

import json
from typing import Any

__all__ = [
    "_responses_to_chat_completions",
    "_extract_delta_tool_calls",
    "_extract_usage",
    "_process_sse_line",
    "build_openrouter_passthrough_body",
    "_responses_input_to_messages",
    "_map_model_for_backend",
    "_extract_delta_content",
    "_chat_completions_to_responses",
]

# GW-42: OpenRouter request field passthrough
# @trace FR-REQEXT-042
_OR_PASSTHROUGH_FIELDS: tuple[str, ...] = (
    # OpenRouter routing
    "provider",
    "models",
    "route",
    "transforms",
    # Reasoning
    "reasoning",
    # Plugins (e.g., web search)
    "plugins",
    # Usage controls
    "usage",
    # Special Anthropic headers via body
    "anthropic_beta",
)


def _map_model_for_backend(model: str) -> str:
    """Map Codex/provider model IDs to backend (CLIProxyAPIPlus) model IDs."""
    from thegent.routing.harness_model_mapping import resolve_model_for_backend

    return resolve_model_for_backend(model)


def _responses_input_to_messages(input_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Responses API input items to Chat Completions messages.

    Preserves content arrays (including cache_control, image_url, etc.) — GW-04.
    """
    messages: list[dict[str, Any]] = []
    for item in input_items:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            role = item.get("role", "user")
            content = item.get("content")
            if isinstance(content, list):
                # Preserve full content array so cache_control and other annotations survive
                enriched: list[dict[str, Any]] = []
                for c in content:
                    if isinstance(c, dict):
                        enriched.append(c)
                    elif isinstance(c, str):
                        enriched.append({"type": "text", "text": c})
                content = enriched or [{"type": "text", "text": ""}]
            elif not isinstance(content, str):
                content = str(content) if content else ""
            messages.append({"role": role, "content": content})
    return messages


def _responses_to_chat_completions(body: dict[str, Any]) -> dict[str, Any]:
    """Transform Responses API request to Chat Completions format.

    OR-09: Forwards OpenRouter-specific fields (transforms, provider, route,
    plugins, reasoning, session_id, metadata, trace) when present.
    Only non-None optional fields are included to avoid sending unexpected
    None values to backends.
    """
    input_items = body.get("input", [])
    if not isinstance(input_items, list):
        input_items = []
    messages = _responses_input_to_messages(input_items)
    if not messages:
        messages = [{"role": "user", "content": ""}]
    raw_model = body.get("model", "")
    mapped_model = _map_model_for_backend(raw_model)

    result: dict[str, Any] = {
        "model": mapped_model,
        "messages": messages,
        "stream": body.get("stream", False),
    }

    # Standard optional sampling parameters — only include when explicitly set
    for field in (
        "temperature",
        "top_p",
        "top_k",
        "frequency_penalty",
        "presence_penalty",
        "repetition_penalty",
        "min_p",
        "top_a",
        "seed",
        "stop",
        "logprobs",
        "top_logprobs",
        "logit_bias",
        "user",
    ):
        val = body.get(field)
        if val is not None:
            result[field] = val

    max_tokens = body.get("max_output_tokens") or body.get("max_tokens")
    if max_tokens is not None:
        result["max_tokens"] = max_tokens

    # OR-09: OpenRouter-specific passthrough fields
    for or_field in (
        "transforms",
        "provider",
        "route",
        "plugins",
        "reasoning",
        "session_id",
        "metadata",
        "trace",
        "models",
        "structured_outputs",
        "stream_options",
        "response_format",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
    ):
        val = body.get(or_field)
        if val is not None:
            result[or_field] = val

    return result


def build_openrouter_passthrough_body(body: dict) -> dict:
    """Build a dict of OpenRouter passthrough fields present in body.

    Returns a new dict containing only the OR passthrough fields from _OR_PASSTHROUGH_FIELDS
    that are present in body. Used for documentation and testing purposes.

    # @trace FR-REQEXT-042
    """
    return {field: body[field] for field in _OR_PASSTHROUGH_FIELDS if field in body}


def _extract_delta_content(chunk: dict[str, Any]) -> str | None:
    """Extract text content from a Chat Completions delta chunk. Returns None if no content."""
    choices = chunk.get("choices", [])
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    return content or None


def _extract_delta_tool_calls(chunk: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract tool_calls from a Chat Completions delta chunk — GW-07.

    Returns the tool_calls list if present, else None.
    """
    choices = chunk.get("choices", [])
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    tool_calls = delta.get("tool_calls")
    return tool_calls or None


def _extract_usage(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """Extract usage from a Chat Completions chunk (only present on the final chunk)."""
    return chunk.get("usage") or None


def _chat_completions_to_responses(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """Legacy single-chunk transform — only used by non-streaming paths. Kept for compatibility."""
    content = _extract_delta_content(chunk)
    if not content:
        return None
    return {
        "type": "response.output_text.delta",
        "response_id": "resp_legacy",
        "item_id": "item_legacy",
        "output_index": 0,
        "content_index": 0,
        "delta": content,
    }


def _process_sse_line(line: bytes, transform: bool) -> bytes | None:
    """Process one SSE line. Returns transformed bytes or None to pass through."""
    line = line.strip()
    if not line:
        return None
    # SSE comment lines (e.g. ": OPENROUTER PROCESSING") must be skipped per spec (WL-005)
    if line.startswith(b":"):
        return None
    if not line.startswith(b"data:"):
        return line + b"\n"
    data_part = line[5:].strip()
    if not data_part or data_part == b"[DONE]":
        return line + b"\n"
    if not transform:
        return line + b"\n"
    try:
        obj = json.loads(data_part.decode(errors="replace"))
        transformed = _chat_completions_to_responses(obj)
        if transformed is None:
            return None  # Skip empty deltas; don't emit Chat Completions format to Responses client
        return f"data: {json.dumps(transformed)}\n\n".encode()
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
        return line + b"\n"
