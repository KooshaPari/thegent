"""LiteLLM Router Responses API handler for Codex CLI compatibility."""

import json
import logging
from typing import Any

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.websockets import WebSocket

from thegent.routing.litellm_router import get_litellm_router

_log = logging.getLogger(__name__)

# Map litellm/provider error substrings to HTTP status codes.
_ERROR_STATUS_MAP: list[tuple[str, int]] = [
    ("rate limit", 429),
    ("ratelimit", 429),
    ("too many requests", 429),
    ("invalid model", 400),
    ("model not found", 400),
    ("invalid request", 400),
    ("bad request", 400),
    ("authentication", 401),
    ("unauthorized", 401),
    ("permission", 403),
    ("forbidden", 403),
    ("context_length_exceeded", 400),
    ("context length", 400),
]


def _error_status_code(exc: Exception) -> int:
    """Return an appropriate HTTP status code for a given exception."""
    msg = str(exc).lower()
    for fragment, code in _ERROR_STATUS_MAP:
        if fragment in msg:
            return code
    return 500


def _error_response(exc: Exception) -> Response:
    """Build a structured JSON error Response from an exception."""
    status = _error_status_code(exc)
    body = json.dumps({"error": {"message": str(exc), "type": type(exc).__name__}})
    return Response(
        content=body,
        status_code=status,
        headers={"Content-Type": "application/json"},
    )


def _responses_input_to_messages(input_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Responses API input items to Chat Completions messages."""
    messages: list[dict[str, Any]] = []
    for item in input_items:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            role = item.get("role", "user")
            content = item.get("content")
            if isinstance(content, list):
                parts = []
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        parts.append(c.get("text", ""))
                content = "\n".join(parts) if parts else ""
            elif not isinstance(content, str):
                content = str(content) if content else ""
            messages.append({"role": role, "content": content})
    return messages


def _responses_to_chat_completions(body: dict[str, Any]) -> dict[str, Any]:
    """Transform Responses API request to Chat Completions format.

    Only non-None optional fields are included so downstream LiteLLM
    calls don't receive unexpected ``None`` keyword arguments.
    """
    input_items = body.get("input", [])
    if not isinstance(input_items, list):
        input_items = []
    messages = _responses_input_to_messages(input_items)
    if not messages:
        messages = [{"role": "user", "content": ""}]

    chat: dict[str, Any] = {
        "model": body.get("model", ""),
        "messages": messages,
        "stream": body.get("stream", False),
    }

    # Only forward optional parameters when explicitly provided.
    temperature = body.get("temperature")
    if temperature is not None:
        chat["temperature"] = temperature

    max_tokens = body.get("max_output_tokens") or body.get("max_tokens")
    if max_tokens is not None:
        chat["max_tokens"] = max_tokens

    return chat


def _chat_completions_to_responses(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """Transform Chat Completions SSE chunk to Responses API format."""
    choices = chunk.get("choices", [])
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    if not content:
        return None  # Skip empty chunks

    return {
        "type": "response.output_item.added",
        "item": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
        },
    }


async def handle_responses_request(request: Request) -> Response:
    """Handle Responses API HTTP POST request via LiteLLM Router."""
    try:
        body = await request.body()
        data = json.loads(body) if body else {}

        # Translate Responses API → Chat Completions
        chat_request = _responses_to_chat_completions(data)
        model = chat_request["model"]
        stream = chat_request.get("stream", False)

        # Get LiteLLM Router
        router = get_litellm_router()

        if stream:
            return await handle_responses_stream(request, chat_request, router)

        # Non-streaming request — route through LiteLLM Router for
        # fallback, cost tracking, and caching support.
        extra = {k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}
        response = await router.acompletion(
            model=model,
            messages=chat_request["messages"],
            **extra,
        )

        # Translate response back to Responses API format
        content = response.choices[0].message.content if response.choices else ""
        responses_data = {
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": content}],
                }
            ]
        }

        return Response(
            content=json.dumps(responses_data),
            status_code=200,
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        _log.error("Error handling Responses API request: %s", e, exc_info=True)
        return _error_response(e)


async def handle_responses_stream(request: Request, chat_request: dict[str, Any], router) -> StreamingResponse:
    """Handle Responses API streaming request via LiteLLM Router."""

    async def stream():
        try:
            model = chat_request["model"]
            messages = chat_request["messages"]
            extra = {k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}

            async for chunk in router.acompletion(
                model=model,
                messages=messages,
                stream=True,
                **extra,
            ):
                # Translate Chat Completions → Responses API
                chunk_dict = chunk.model_dump() if hasattr(chunk, "model_dump") else chunk
                responses_event = _chat_completions_to_responses(chunk_dict)
                if responses_event:
                    yield f"data: {json.dumps(responses_event)}\n\n"

            # Send completion event
            yield 'data: {"type": "response.completed"}\n\n'

        except Exception as e:
            _log.error("Error in Responses API stream: %s", e, exc_info=True)
            # Use json.dumps to safely encode the error message (handles
            # quotes, newlines, and other characters that break raw f-strings).
            error_payload = json.dumps({"error": {"message": str(e), "type": type(e).__name__}})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        stream(),
        status_code=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


async def handle_responses_websocket(websocket: WebSocket) -> None:
    """Handle Responses API WebSocket request via LiteLLM Router."""
    import asyncio

    await websocket.accept()
    _send_error = False

    try:
        # Receive request — timeout guards against clients that never send.
        data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)

        # Translate to Chat Completions
        chat_request = _responses_to_chat_completions(data)
        model = chat_request["model"]
        messages = chat_request["messages"]
        extra = {k: v for k, v in chat_request.items() if k not in ("model", "messages", "stream")}

        # Get router
        router = get_litellm_router()

        # Stream response
        async for chunk in router.acompletion(
            model=model,
            messages=messages,
            stream=True,
            **extra,
        ):
            chunk_dict = chunk.model_dump() if hasattr(chunk, "model_dump") else chunk
            responses_event = _chat_completions_to_responses(chunk_dict)
            if responses_event:
                await websocket.send_json(responses_event)

        # Send completion event
        await websocket.send_json({"type": "response.completed"})

    except Exception as e:
        _log.error("Error in Responses API WebSocket: %s", e, exc_info=True)
        _send_error = True
        try:
            await websocket.send_json({"error": {"message": str(e), "type": type(e).__name__}})
        except Exception:
            pass  # Connection may already be broken; ignore send failure.
    finally:
        try:
            # Use code 1001 (Going Away) on error so clients can distinguish
            # from a clean close (1000 = Normal Closure).
            close_code = 1001 if _send_error else 1000
            await websocket.close(close_code)
        except Exception:
            pass  # Already closed.
