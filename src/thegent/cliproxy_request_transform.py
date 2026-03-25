# MIGRATION NOTE: Migrate to cliproxyapi-plusplus Go SDK
from __future__ import annotations

import orjson as json
from typing import Any

__all__ = [
    "_chat_completions_to_responses",
    "_extract_delta_content",
    "_extract_delta_tool_calls",
    "_extract_usage",
    "_map_model_for_backend",
    "_process_sse_line",
    "_responses_input_to_messages",
    "_responses_to_chat_completions",
    "build_openrouter_passthrough_body",
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
_THINKING_SIGNATURE_KEYS: frozenset[str] = frozenset({"signature", "thought_signature", "metadata"})

_UNSUPPORTED_SCHEMA_KEYS: frozenset[str] = frozenset({"$id", "patternProperties"})


def _normalize_schema_for_provider(value: Any) -> Any:
    """Normalize tool schema payloads for provider compatibility."""
    if isinstance(value, list):
        return [_normalize_schema_for_provider(item) for item in value]
    if not isinstance(value, dict):
        return value

    normalized: dict[str, Any] = {}
    for key, raw in value.items():
        if key in _UNSUPPORTED_SCHEMA_KEYS:
            continue
        normalized[key] = _normalize_schema_for_provider(raw)

    schema_type = normalized.get("type")
    if isinstance(schema_type, list):
        string_types = [entry for entry in schema_type if isinstance(entry, str)]
        non_null_types = [entry for entry in string_types if entry != "null"]
        has_null = "null" in string_types
        if has_null and len(non_null_types) == 1:
            normalized["type"] = non_null_types[0]
            normalized["nullable"] = True
        elif non_null_types:
            normalized.pop("type", None)
            any_of = [{"type": entry} for entry in non_null_types]
            if has_null:
                any_of.append({"type": "null"})
            normalized["anyOf"] = any_of
        else:
            normalized.pop("type", None)
    return normalized


def _normalize_tool(tool: dict[str, Any]) -> dict[str, Any]:
    """Normalize OpenAI Responses-style tool definitions for Chat Completions."""
    tool_type = tool.get("type")
    if tool_type == "custom":
        function_name = tool.get("name")
        if not isinstance(function_name, str) or not function_name:
            return tool
        function: dict[str, Any] = {
            "name": function_name,
            "parameters": _normalize_schema_for_provider(tool.get("input_schema") or {}),
        }
        description = tool.get("description")
        if isinstance(description, str) and description:
            function["description"] = description
        converted: dict[str, Any] = {"type": "function", "function": function}
        if "strict" in tool:
            converted["strict"] = tool["strict"]
        return converted
    if tool_type == "function":
        function_payload = tool.get("function")
        if isinstance(function_payload, dict) and "parameters" in function_payload:
            converted = dict(tool)
            converted_function = dict(function_payload)
            converted_function["parameters"] = _normalize_schema_for_provider(function_payload.get("parameters"))
            converted["function"] = converted_function
            return converted
    return tool


def _normalize_tool_choice(chat_body: dict[str, Any]) -> None:
    """Normalize tool_choice payloads before name-alignment logic."""
    tool_choice = chat_body.get("tool_choice")
    if not isinstance(tool_choice, dict):
        return
    if tool_choice.get("type") == "custom":
        name = tool_choice.get("name")
        if isinstance(name, str) and name:
            chat_body["tool_choice"] = {"type": "function", "function": {"name": name}}


def _map_model_for_backend(model: str) -> str:
    """Map Codex/provider model IDs to backend (CLIProxyAPIPlus) model IDs."""
    from thegent.utils.routing_impl.harness_model_mapping import resolve_model_for_backend

    return resolve_model_for_backend(model)


def _strip_thinking_signatures(content: Any) -> Any:
    """Strip provider-specific thinking signatures from message content blocks."""
    if not isinstance(content, list):
        return content

    sanitized: list[dict[str, Any]] = []
    for part in content:
        if isinstance(part, dict):
            sanitized_part = {k: v for k, v in part.items() if k not in _THINKING_SIGNATURE_KEYS}
            sanitized.append(sanitized_part)
            continue
        if isinstance(part, str):
            sanitized.append({"type": "text", "text": part})
    return sanitized or [{"type": "text", "text": ""}]


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
                # Preserve content arrays while dropping stale provider signatures.
                content = _strip_thinking_signatures(content)
            elif not isinstance(content, str):
                content = str(content) if content else ""
            messages.append({"role": role, "content": content})
    return messages


def _normalize_tool_choice_name(chat_body: dict[str, Any]) -> None:
    """Align tool_choice name with declared tools when proxy_ prefix drifts.

    CLIP-BUG-12: some upstream OAuth paths prefix tool_choice name with ``proxy_``
    while tool declarations remain unprefixed. This normalizes only the mismatched
    name path and leaves tool definitions untouched.
    """
    tools = chat_body.get("tools")
    tool_choice = chat_body.get("tool_choice")
    if not isinstance(tools, list) or not isinstance(tool_choice, dict):
        return

    declared_names: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        fn = tool.get("function")
        if isinstance(fn, dict):
            name = fn.get("name")
            if isinstance(name, str) and name:
                declared_names.add(name)
                continue
        raw_name = tool.get("name")
        if isinstance(raw_name, str) and raw_name:
            declared_names.add(raw_name)

    if not declared_names:
        return

    fn_choice = tool_choice.get("function")
    if isinstance(fn_choice, dict):
        choice_name = fn_choice.get("name")
        if isinstance(choice_name, str) and choice_name.startswith("proxy_"):
            unprefixed = choice_name.removeprefix("proxy_")
            if unprefixed in declared_names:
                fn_choice["name"] = unprefixed
        return

    choice_name = tool_choice.get("name")
    if isinstance(choice_name, str) and choice_name.startswith("proxy_"):
        unprefixed = choice_name.removeprefix("proxy_")
        if unprefixed in declared_names:
            tool_choice["name"] = unprefixed


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
    messages: list[dict[str, Any]] = _responses_input_to_messages(input_items)
    if not messages and isinstance(body.get("messages"), list):
        # CLIP-BUG-11: preserve existing chat envelope payloads (including
        # thinking/signature blocks) when callers provide messages directly.
        raw_messages = body.get("messages")
        if isinstance(raw_messages, list):
            messages = [item for item in raw_messages if isinstance(item, dict)]
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
        "thinking",
        "output_config",
    ):
        val = body.get(or_field)
        if val is not None:
            result[or_field] = val

    tools = result.get("tools")
    if isinstance(tools, list):
        result["tools"] = [_normalize_tool(tool) for tool in tools if isinstance(tool, dict)]

    response_format = result.get("response_format")
    if isinstance(response_format, dict):
        updated_response_format = dict(response_format)
        json_schema = updated_response_format.get("json_schema")
        if isinstance(json_schema, dict) and "schema" in json_schema:
            updated_json_schema = dict(json_schema)
            updated_json_schema["schema"] = _normalize_schema_for_provider(json_schema.get("schema"))
            updated_response_format["json_schema"] = updated_json_schema
        result["response_format"] = updated_response_format

    if "structured_outputs" in result:
        result["structured_outputs"] = _normalize_schema_for_provider(result["structured_outputs"])

    _normalize_tool_choice(result)
    _normalize_tool_choice_name(result)
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
        "type": "response.output_item.added",
        "response_id": "resp_legacy",
        "item_id": "item_legacy",
        "output_index": 0,
        "item": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
        },
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
    try:
        obj = json.loads(data_part.decode(errors="replace"))
        if not transform:
            usage = obj.get("usage")
            choices = obj.get("choices")
            has_finish_reason = isinstance(choices, list) and any(
                isinstance(choice, dict) and choice.get("finish_reason") is not None for choice in choices
            )
            if usage is not None and has_finish_reason:
                chunk_without_usage = dict(obj)
                chunk_without_usage.pop("usage", None)

                usage_chunk = {k: v for k, v in obj.items() if k != "choices"}
                usage_chunk["choices"] = []
                usage_chunk["usage"] = usage

                first = f"data: {json.dumps(chunk_without_usage).decode()}\n\n".encode()
                second = f"data: {json.dumps(usage_chunk).decode()}\n\n".encode()
                return first + second
            return line + b"\n"
        transformed = _chat_completions_to_responses(obj)
        if transformed is None:
            return None  # Skip empty deltas; don't emit Chat Completions format to Responses client
        return f"data: {json.dumps(transformed).decode()}\n\n".encode()
    except json.JSONDecodeError, KeyError, UnicodeDecodeError:
        return line + b"\n"
