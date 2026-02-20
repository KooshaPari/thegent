"""CLIProxy adapter: exposes /v1/responses (HTTP + WebSocket) for Codex compatibility.

cliproxyapi++ (kooshapari fork) may not implement /v1/responses. This adapter:
- Proxies all /v1/* to the backend
- For POST /v1/responses: tries backend first; on 404, translates to /v1/chat/completions
- For WebSocket /v1/responses: bridges WS to HTTP streaming (SSE)
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
from typing import TYPE_CHECKING, Any

from starlette.applications import Starlette
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route, WebSocketRoute

if TYPE_CHECKING:
    from starlette.requests import Request

_log = logging.getLogger(__name__)


def _map_model_for_backend(model: str) -> str:
    """Map Codex/provider model IDs to backend (CLIProxyAPIPlus) model IDs."""
    from thegent.routing.harness_model_mapping import resolve_model_for_backend

    return resolve_model_for_backend(model)


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
    """Transform Responses API request to Chat Completions format."""
    input_items = body.get("input", [])
    if not isinstance(input_items, list):
        input_items = []
    messages = _responses_input_to_messages(input_items)
    if not messages:
        messages = [{"role": "user", "content": ""}]
    raw_model = body.get("model", "")
    mapped_model = _map_model_for_backend(raw_model)
    return {
        "model": mapped_model,
        "messages": messages,
        "stream": body.get("stream", False),
        "temperature": body.get("temperature"),
        "max_tokens": body.get("max_output_tokens") or body.get("max_tokens"),
    }


def _chat_completions_to_responses(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """Transform Chat Completions SSE chunk to Responses API format.
    Returns None for empty deltas — do not emit; Codex expects Responses format only, not mixed Chat Completions."""
    choices = chunk.get("choices", [])
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    content = delta.get("content", "")
    if not content:
        return None  # Skip empty chunks; emitting Chat Completions format confuses Codex
    return {
        "type": "response.output_item.added",
        "item": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
        },
    }


async def _proxy_request(
    request: Request,
    backend_url: str,
    path: str,
    *,
    transform_responses: bool = False,
) -> Response:
    """Forward request to backend. Optionally transform Responses <-> Chat Completions."""
    import httpx

    body = b""
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
    url = f"{backend_url.rstrip('/')}{path}" if path.startswith("/") else f"{backend_url.rstrip('/')}/{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    if transform_responses and body and path == "/v1/responses":
        try:
            data = json.loads(body)
            transformed = _responses_to_chat_completions(data)
            body = json.dumps(transformed).encode()
            url = f"{backend_url.rstrip('/')}/v1/chat/completions"
        except (json.JSONDecodeError, KeyError) as e:
            _log.warning("responses->chat transform failed: %s", e)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.request(
                request.method,
                url,
                content=body,
                headers=headers,
            )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={k: v for k, v in resp.headers.items() if k.lower() not in ("transfer-encoding", "connection")},
        )
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        _log.error("Backend proxy (%s) unreachable: %s", backend_url, e)
        return Response(
            content=json.dumps(
                {"error": {"message": f"Backend proxy ({backend_url}) unreachable. Restart with: thegent mcp restart"}}
            ).encode(),
            status_code=503,
            headers={"Content-Type": "application/json"},
        )


def _process_sse_line(line: bytes, transform: bool) -> bytes | None:
    """Process one SSE line. Returns transformed bytes or None to pass through."""
    line = line.strip()
    if not line.startswith(b"data:"):
        return line + b"\n" if line else None
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


async def _proxy_stream(
    body: bytes,
    headers: dict[str, str],
    backend_url: str,
    path: str,
    *,
    transform_responses: bool = False,
) -> Response:
    """Stream proxy with optional response transformation. Buffers SSE by line to handle chunk boundaries."""
    import httpx

    if transform_responses:
        try:
            data = json.loads(body)
            transformed = _responses_to_chat_completions(data)
            body = json.dumps(transformed).encode()
        except (json.JSONDecodeError, KeyError):
            pass
        url = f"{backend_url.rstrip('/')}/chat/completions"
    else:
        url = f"{backend_url.rstrip('/')}{path}" if path.startswith("/") else f"{backend_url.rstrip('/')}/{path}"

    async def stream():
        buffer = b""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, content=body, headers=headers) as resp:
                    if resp.status_code != 200:
                        err_body = await resp.aread()
                        _log.warning("backend stream error %s: %s", resp.status_code, err_body[:200])
                        yield f'data: {{"error":{{"message":"Backend {resp.status_code}"}}}}\n\n'.encode()
                        return
                    async for chunk in resp.aiter_bytes():
                        buffer += chunk
                        while b"\n" in buffer or (buffer and buffer.endswith(b"\n")):
                            idx = buffer.find(b"\n")
                            if idx < 0:
                                break
                            line = buffer[:idx]
                            buffer = buffer[idx + 1 :]
                            out = _process_sse_line(line, transform_responses)
                            if out:
                                yield out
                    if buffer.strip():
                        out = _process_sse_line(buffer, transform_responses)
                        if out:
                            yield out
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            _log.error("Backend stream connection failed: %s", e)
            yield f'data: {{"error":{{"message":"Backend proxy ({url}) unreachable."}}}}\n\n'.encode()

    return StreamingResponse(
        stream(),
        status_code=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


def _transform_models_response(content: bytes) -> bytes | None:
    """Transform CLIProxy models response to Codex format (models) and enrich with metadata.

    - Converts data -> models for Codex compatibility
    - Adds context_window, max_completion_tokens from model_metadata to fix
      "Model metadata for X not found" warning
    - Returns None when response already has 'models' (no transform needed)
    """
    try:
        data = json.loads(content.decode(errors="replace"))
        if "data" not in data and "models" in data:
            return None  # Already in Codex format, pass through
        models = data.pop("data", data.get("models", []))
        if not isinstance(models, list):
            return None
        data["models"] = models

        # Enrich each model with metadata for Codex (avoids fallback metadata warning)
        try:
            from thegent.routing.model_metadata import get_model_metadata
        except ImportError:

            def get_model_metadata(_):
                return None

        for m in models:
            if not isinstance(m, dict):
                continue
            mid = m.get("id") or m.get("name") or ""
            if not mid:
                continue
            meta = get_model_metadata(mid)
            if not meta and "/" in mid:
                meta = get_model_metadata(mid.split("/", 1)[1])
            if meta:
                ctx = meta.get("context_window")
                if "slug" not in m:
                    m["slug"] = mid
                if ctx is not None and "context_window" not in m:
                    m["context_window"] = ctx
                if ctx is not None and "context_length" not in m:
                    m["context_length"] = ctx
                if ctx is not None and "max_completion_tokens" not in m:
                    m["max_completion_tokens"] = min(ctx, 8192)
            elif "slug" not in m:
                m["slug"] = mid

        return json.dumps(data).encode()
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _backend_path(backend_url: str, request_path: str) -> str:
    """Path to append to backend base. Backend base is .../v1, so /v1/responses -> /responses."""
    base = backend_url.rstrip("/")
    if base.endswith("/v1") and request_path.startswith("/v1/"):
        return request_path[4:]  # /v1/responses -> /responses
    return request_path


async def proxy_handler(request: Request) -> Response:
    """Proxy /v1/* to backend. Transform /v1/responses to /v1/chat/completions."""
    backend = getattr(request.app.state, "backend_url", "http://127.0.0.1:8318/v1")
    path = request.url.path or "/v1/models"

    # Check if LiteLLM Router should be used
    use_litellm = os.environ.get("THGENT_USE_LITELLM_ROUTER", "0") == "1"

    if _log.isEnabledFor(logging.DEBUG) or __debug__:
        _log.debug("adapter request: %s %s (litellm=%s)", request.method, path, use_litellm)

    if not path.startswith("/v1/"):
        return Response("Not Found", status_code=404)

    # Route Responses API to LiteLLM Router if enabled
    if use_litellm and path == "/v1/responses" and request.method == "POST":
        try:
            from thegent.routing.litellm_responses_handler import handle_responses_request

            return await handle_responses_request(request)
        except Exception as e:
            _log.error("LiteLLM Router handler failed: %s", e, exc_info=True)
            # Fallback to CLIProxyAPIPlus

    backend_path = _backend_path(backend, path)

    if request.method == "GET" and path in ("/v1/models", "/v1/models/"):
        resp = await _proxy_request(request, backend, backend_path)
        # Codex expects {"models": [...]}; CLIProxy returns {"data": [...], "object": "list"}
        if resp.status_code == 200 and resp.body:
            transformed = _transform_models_response(resp.body)
            if transformed is not None:
                return Response(
                    content=transformed,
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                )
        return resp
    if request.method == "POST":
        try:
            body = await request.body()
            data = json.loads(body) if body else {}
            stream_mode = data.get("stream", False)
        except json.JSONDecodeError:
            stream_mode = False

        if path == "/v1/responses":
            # Backend often lacks /v1/responses; translate to /v1/chat/completions
            if data:
                _log.debug("responses transform: model=%s stream=%s", data.get("model"), data.get("stream"))
            req_headers = dict(request.headers)
            req_headers.pop("host", None)
            req_headers.pop("content-length", None)
            return await _proxy_stream(body, req_headers, backend, "/chat/completions", transform_responses=True)

        if stream_mode and path == "/v1/chat/completions":
            req_headers = dict(request.headers)
            req_headers.pop("host", None)
            req_headers.pop("content-length", None)
            return await _proxy_stream(body, req_headers, backend, backend_path)
        return await _proxy_request(request, backend, backend_path)
    return await _proxy_request(request, backend, backend_path)


async def websocket_responses_handler(websocket: Any) -> None:
    """Bridge WebSocket /v1/responses to HTTP streaming. Buffers SSE by line."""
    import asyncio

    # Check if LiteLLM Router should be used
    use_litellm = os.environ.get("THGENT_USE_LITELLM_ROUTER", "0") == "1"

    if use_litellm:
        try:
            from thegent.routing.litellm_responses_handler import handle_responses_websocket

            await handle_responses_websocket(websocket)
            return
        except Exception as e:
            _log.error("LiteLLM Router WebSocket handler failed: %s", e, exc_info=True)
            # Fallback to CLIProxyAPIPlus

    import httpx

    await websocket.accept()
    backend = getattr(websocket.app.state, "backend_url", "http://127.0.0.1:8318/v1")
    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
    except TimeoutError:
        _log.warning("ws responses: receive_json timeout")
        await websocket.close(1008)
        return
    except Exception as e:
        _log.warning("ws responses: receive_json failed: %s", e)
        await websocket.close(1008)
        return

    body = json.dumps(data).encode()
    transform = True
    base = backend.rstrip("/")
    url = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
    if "input" in data:
        transformed = _responses_to_chat_completions(data)
        body = json.dumps(transformed).encode()
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, content=body, headers=headers) as resp:
                if resp.status_code != 200:
                    err_body = await resp.aread()
                    _log.warning("ws backend error %s: %s", resp.status_code, err_body[:200])
                    await websocket.send_json({"error": {"message": f"Backend {resp.status_code}"}})
                    await websocket.close(1011)
                    return
                buffer = b""
                async for chunk in resp.aiter_bytes():
                    buffer += chunk
                    while b"\n" in buffer:
                        idx = buffer.find(b"\n")
                        line = buffer[:idx]
                        buffer = buffer[idx + 1 :]
                        line = line.strip()
                        if line.startswith(b"data:"):
                            data_part = line[5:].strip()
                            if data_part and data_part != b"[DONE]":
                                try:
                                    obj = json.loads(data_part.decode(errors="replace"))
                                    out = _chat_completions_to_responses(obj) if transform else obj
                                    if out is not None:
                                        await websocket.send_json(out)
                                except (json.JSONDecodeError, UnicodeDecodeError):
                                    pass
                # Codex expects response.completed before WS close; else "websocket closed by server before response.completed"
                await websocket.send_json({"type": "response.completed"})
    except Exception as e:
        _log.warning("ws responses: stream error: %s", e)
    finally:
        with contextlib.suppress(Exception):
            await websocket.close(1000)


def create_adapter_app(backend_url: str) -> Starlette:
    """Create the adapter Starlette app."""
    from thegent.config import ThegentSettings

    if ThegentSettings().debug:
        _log.setLevel(logging.DEBUG)
    app = Starlette(
        routes=[
            Route("/{path:path}", proxy_handler, methods=["GET", "POST", "OPTIONS"]),
            WebSocketRoute("/v1/responses", websocket_responses_handler),
        ],
    )
    app.state.backend_url = backend_url.rstrip("/")
    return app
