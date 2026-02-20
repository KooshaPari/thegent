"""Tests for the LiteLLM Router Responses API handler.

Coverage:
- @trace FR-ROUTE-001  Request conversion: Responses API input -> Chat Completions messages
- @trace FR-ROUTE-002  Non-streaming response transformation
- @trace FR-ROUTE-003  Streaming SSE response transformation
- @trace FR-ROUTE-004  Error handling with structured error responses and correct HTTP codes
- @trace FR-ROUTE-005  WebSocket handler
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Async-iterator helpers (used instead of async generators to avoid
# unreachable-yield issues in error-raising variants).
# ---------------------------------------------------------------------------


class _AsyncGenFromChunks:
    """Async iterator that yields MagicMock objects wrapping chunk dicts."""

    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        self._chunks = chunks
        self._idx = 0

    def __aiter__(self) -> _AsyncGenFromChunks:
        return self

    async def __anext__(self) -> MagicMock:
        if self._idx >= len(self._chunks):
            raise StopAsyncIteration
        chunk = self._chunks[self._idx]
        self._idx += 1
        return MagicMock(**{"model_dump.return_value": chunk})


class _AsyncGenRaise:
    """Async iterator that immediately raises the given exception on first iteration."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def __aiter__(self) -> _AsyncGenRaise:
        return self

    async def __anext__(self) -> MagicMock:
        raise self._exc


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_message_item(role: str = "user", content: Any = "Hello") -> dict[str, Any]:
    """Build a Responses API input item of type 'message'."""
    return {"type": "message", "role": role, "content": content}


def _make_responses_body(
    model: str = "gpt-4o",
    input_items: list[dict] | None = None,
    stream: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build a minimal Responses API request body."""
    body: dict[str, Any] = {
        "model": model,
        "input": input_items if input_items is not None else [_make_message_item()],
        "stream": stream,
    }
    body.update(kwargs)
    return body


def _make_chat_chunk(content: str | None, finish_reason: str | None = None) -> dict[str, Any]:
    """Build a Chat Completions streaming chunk dict."""
    delta: dict[str, Any] = {}
    if content is not None:
        delta["content"] = content
    choice: dict[str, Any] = {"delta": delta}
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return {"choices": [choice]}


# ---------------------------------------------------------------------------
# _responses_input_to_messages
# ---------------------------------------------------------------------------


class TestResponsesInputToMessages:
    """@trace FR-ROUTE-001"""

    def test_simple_user_string_message(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        items = [_make_message_item("user", "Hello there")]
        msgs = _responses_input_to_messages(items)
        assert msgs == [{"role": "user", "content": "Hello there"}]

    def test_assistant_message(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        items = [_make_message_item("assistant", "I am an assistant")]
        msgs = _responses_input_to_messages(items)
        assert msgs == [{"role": "assistant", "content": "I am an assistant"}]

    def test_multi_part_content_list(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        content_parts = [
            {"type": "text", "text": "Part one"},
            {"type": "text", "text": "Part two"},
        ]
        items = [_make_message_item("user", content_parts)]
        msgs = _responses_input_to_messages(items)
        assert msgs == [{"role": "user", "content": "Part one\nPart two"}]

    def test_content_list_skips_non_text_parts(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        content_parts = [
            {"type": "image_url", "url": "http://example.com/img.png"},
            {"type": "text", "text": "Caption"},
        ]
        items = [_make_message_item("user", content_parts)]
        msgs = _responses_input_to_messages(items)
        assert msgs == [{"role": "user", "content": "Caption"}]

    def test_non_message_type_items_are_ignored(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        items = [
            {"type": "tool_result", "content": "tool output"},
            _make_message_item("user", "Real message"),
        ]
        msgs = _responses_input_to_messages(items)
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Real message"

    def test_non_dict_items_are_ignored(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        bad_items: list[Any] = ["not a dict", 42]
        msgs = _responses_input_to_messages(bad_items)
        assert msgs == []

    def test_multiple_messages_preserved_in_order(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        items = [
            _make_message_item("user", "First"),
            _make_message_item("assistant", "Second"),
            _make_message_item("user", "Third"),
        ]
        msgs = _responses_input_to_messages(items)
        assert [m["role"] for m in msgs] == ["user", "assistant", "user"]
        assert [m["content"] for m in msgs] == ["First", "Second", "Third"]

    def test_none_content_coerced_to_empty_string(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_input_to_messages

        items = [{"type": "message", "role": "user", "content": None}]
        msgs = _responses_input_to_messages(items)
        assert msgs == [{"role": "user", "content": ""}]


# ---------------------------------------------------------------------------
# _responses_to_chat_completions
# ---------------------------------------------------------------------------


class TestResponsesToChatCompletions:
    """@trace FR-ROUTE-001"""

    def test_basic_conversion(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(model="gpt-4o")
        result = _responses_to_chat_completions(body)
        assert result["model"] == "gpt-4o"
        assert result["stream"] is False
        assert result["messages"][0]["role"] == "user"

    def test_empty_input_produces_fallback_message(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(input_items=[])
        result = _responses_to_chat_completions(body)
        assert result["messages"] == [{"role": "user", "content": ""}]

    def test_non_list_input_produces_fallback_message(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = {"model": "gpt-4o", "input": "bad input type", "stream": False}
        result = _responses_to_chat_completions(body)
        assert result["messages"] == [{"role": "user", "content": ""}]

    def test_temperature_included_when_set(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(temperature=0.7)
        result = _responses_to_chat_completions(body)
        assert result["temperature"] == 0.7

    def test_temperature_absent_when_not_set(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body()
        result = _responses_to_chat_completions(body)
        assert "temperature" not in result

    def test_max_output_tokens_mapped_to_max_tokens(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(max_output_tokens=512)
        result = _responses_to_chat_completions(body)
        assert result["max_tokens"] == 512

    def test_max_tokens_fallback(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(max_tokens=256)
        result = _responses_to_chat_completions(body)
        assert result["max_tokens"] == 256

    def test_max_tokens_absent_when_not_set(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body()
        result = _responses_to_chat_completions(body)
        assert "max_tokens" not in result

    def test_stream_flag_forwarded(self) -> None:
        from thegent.routing.litellm_responses_handler import _responses_to_chat_completions

        body = _make_responses_body(stream=True)
        result = _responses_to_chat_completions(body)
        assert result["stream"] is True


# ---------------------------------------------------------------------------
# _chat_completions_to_responses
# ---------------------------------------------------------------------------


class TestChatCompletionsToResponses:
    """@trace FR-ROUTE-003"""

    def test_content_chunk_transformed(self) -> None:
        from thegent.routing.litellm_responses_handler import _chat_completions_to_responses

        chunk = _make_chat_chunk("Hello")
        event = _chat_completions_to_responses(chunk)
        assert event is not None
        assert event["type"] == "response.output_item.added"
        assert event["item"]["content"][0]["text"] == "Hello"
        assert event["item"]["role"] == "assistant"

    def test_empty_content_returns_none(self) -> None:
        from thegent.routing.litellm_responses_handler import _chat_completions_to_responses

        chunk = _make_chat_chunk("")
        assert _chat_completions_to_responses(chunk) is None

    def test_none_content_returns_none(self) -> None:
        from thegent.routing.litellm_responses_handler import _chat_completions_to_responses

        chunk = _make_chat_chunk(None)
        assert _chat_completions_to_responses(chunk) is None

    def test_no_choices_returns_none(self) -> None:
        from thegent.routing.litellm_responses_handler import _chat_completions_to_responses

        assert _chat_completions_to_responses({"choices": []}) is None

    def test_missing_choices_key_returns_none(self) -> None:
        from thegent.routing.litellm_responses_handler import _chat_completions_to_responses

        assert _chat_completions_to_responses({}) is None


# ---------------------------------------------------------------------------
# _error_status_code / _error_response
# ---------------------------------------------------------------------------


class TestErrorHelpers:
    """@trace FR-ROUTE-004"""

    def test_rate_limit_maps_to_429(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("rate limit exceeded")) == 429

    def test_too_many_requests_maps_to_429(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("too many requests")) == 429

    def test_invalid_model_maps_to_400(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("invalid model gpt-99")) == 400

    def test_authentication_maps_to_401(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("authentication failed")) == 401

    def test_context_length_exceeded_maps_to_400(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("context_length_exceeded")) == 400

    def test_unknown_error_maps_to_500(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_status_code

        assert _error_status_code(Exception("some unexpected failure")) == 500

    def test_error_response_body_structure(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_response

        resp = _error_response(ValueError("bad thing happened"))
        assert resp.status_code == 500
        body = json.loads(resp.body)
        assert "error" in body
        assert body["error"]["message"] == "bad thing happened"
        assert body["error"]["type"] == "ValueError"

    def test_error_response_rate_limit_status(self) -> None:
        from thegent.routing.litellm_responses_handler import _error_response

        resp = _error_response(Exception("rate limit exceeded"))
        assert resp.status_code == 429


# ---------------------------------------------------------------------------
# handle_responses_request -- non-streaming (HTTP)
# ---------------------------------------------------------------------------


class TestHandleResponsesRequest:
    """@trace FR-ROUTE-002"""

    @pytest.mark.asyncio
    async def test_non_streaming_success(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_choice = MagicMock()
        mock_choice.message.content = "Hi from model"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(return_value=mock_response)

        body = json.dumps(_make_responses_body(model="gpt-4o")).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200
        data = resp.json()
        assert "output" in data
        assert data["output"][0]["content"][0]["text"] == "Hi from model"

    @pytest.mark.asyncio
    async def test_non_streaming_empty_body(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_choice = MagicMock()
        mock_choice.message.content = "Empty body response"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(return_value=mock_response)

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=b"", headers={"Content-Type": "application/json"})

        # Empty body defaults to empty dict; should not crash.
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_non_streaming_rate_limit_error_returns_429(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(side_effect=Exception("rate limit exceeded"))

        body = json.dumps(_make_responses_body(model="gpt-4o")).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 429
        data = resp.json()
        assert "error" in data
        assert "rate limit" in data["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_non_streaming_unknown_error_returns_500(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(side_effect=RuntimeError("unexpected server crash"))

        body = json.dumps(_make_responses_body(model="gpt-4o")).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 500
        data = resp.json()
        assert data["error"]["type"] == "RuntimeError"

    @pytest.mark.asyncio
    async def test_router_called_with_correct_model_and_messages(self) -> None:
        """Verify that router.acompletion receives the right model and messages."""
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(return_value=mock_response)

        body = json.dumps(
            _make_responses_body(
                model="claude-sonnet-4.5",
                input_items=[_make_message_item("user", "What is 2+2?")],
            )
        ).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        mock_router.acompletion.assert_awaited_once()
        call_kwargs = mock_router.acompletion.call_args
        assert call_kwargs.kwargs["model"] == "claude-sonnet-4.5"
        messages = call_kwargs.kwargs["messages"]
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "What is 2+2?"

    @pytest.mark.asyncio
    async def test_temperature_forwarded_to_router(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(return_value=mock_response)

        body = json.dumps(_make_responses_body(model="gpt-4o", temperature=0.3)).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        call_kwargs = mock_router.acompletion.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.3

    @pytest.mark.asyncio
    async def test_no_temperature_not_forwarded_to_router(self) -> None:
        """None temperature must not appear in acompletion kwargs."""
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_router = MagicMock()
        mock_router.acompletion = AsyncMock(return_value=mock_response)

        body = json.dumps(_make_responses_body(model="gpt-4o")).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        call_kwargs = mock_router.acompletion.call_args
        assert "temperature" not in call_kwargs.kwargs


# ---------------------------------------------------------------------------
# handle_responses_stream -- SSE streaming
# ---------------------------------------------------------------------------


class TestHandleResponsesStream:
    """@trace FR-ROUTE-003"""

    @pytest.mark.asyncio
    async def test_streaming_yields_sse_events(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        chunks = [
            _make_chat_chunk("Hello"),
            _make_chat_chunk(", world"),
            _make_chat_chunk(None, finish_reason="stop"),
        ]

        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenFromChunks(chunks)

        body = json.dumps(_make_responses_body(model="gpt-4o", stream=True)).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        lines = [line for line in resp.text.split("\n\n") if line.strip()]
        # At minimum: two content events + one completion event.
        assert len(lines) >= 3

        event1 = json.loads(lines[0].removeprefix("data: "))
        assert event1["type"] == "response.output_item.added"
        assert event1["item"]["content"][0]["text"] == "Hello"

        event2 = json.loads(lines[1].removeprefix("data: "))
        assert event2["item"]["content"][0]["text"] == ", world"

        last = json.loads(lines[-1].removeprefix("data: "))
        assert last == {"type": "response.completed"}

    @pytest.mark.asyncio
    async def test_streaming_error_yields_error_event(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenRaise(RuntimeError("upstream broke"))

        body = json.dumps(_make_responses_body(model="gpt-4o", stream=True)).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200  # SSE always starts 200
        assert "text/event-stream" in resp.headers["content-type"]

        lines = [line for line in resp.text.split("\n\n") if line.strip()]
        assert len(lines) >= 1
        error_event = json.loads(lines[0].removeprefix("data: "))
        assert "error" in error_event
        assert "upstream broke" in error_event["error"]["message"]

    @pytest.mark.asyncio
    async def test_streaming_error_message_with_quotes_is_valid_json(self) -> None:
        """Error messages containing quotes must be properly JSON-encoded."""
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        bad_exc = ValueError('She said "hello" and it failed')
        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenRaise(bad_exc)

        body = json.dumps(_make_responses_body(model="gpt-4o", stream=True)).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        lines = [line for line in resp.text.split("\n\n") if line.strip()]
        payload = lines[0].removeprefix("data: ")
        parsed = json.loads(payload)  # Must not raise
        assert "error" in parsed

    @pytest.mark.asyncio
    async def test_streaming_response_headers(self) -> None:
        from starlette.testclient import TestClient

        from thegent.routing.litellm_responses_handler import handle_responses_request

        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenFromChunks([])

        body = json.dumps(_make_responses_body(model="gpt-4o", stream=True)).encode()

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import Route

            app = Starlette(routes=[Route("/v1/responses", handle_responses_request, methods=["POST"])])
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post("/v1/responses", content=body, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200
        assert resp.headers.get("cache-control") == "no-cache"


# ---------------------------------------------------------------------------
# handle_responses_websocket
# ---------------------------------------------------------------------------


class TestHandleResponsesWebsocket:
    """@trace FR-ROUTE-005"""

    @pytest.mark.asyncio
    async def test_websocket_streams_events_and_closes_cleanly(self) -> None:
        from starlette.testclient import TestClient
        from starlette.websockets import WebSocket as StarletteWS

        from thegent.routing.litellm_responses_handler import handle_responses_websocket

        chunks = [
            _make_chat_chunk("Hello"),
            _make_chat_chunk(" world"),
        ]

        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenFromChunks(chunks)

        async def ws_endpoint(websocket: StarletteWS) -> None:
            await handle_responses_websocket(websocket)

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import WebSocketRoute

            app = Starlette(routes=[WebSocketRoute("/ws", ws_endpoint)])
            client = TestClient(app)

            with client.websocket_connect("/ws") as ws:
                ws.send_json(_make_responses_body(model="gpt-4o", stream=True))
                events = []
                for _ in range(10):
                    msg = ws.receive_json()
                    events.append(msg)
                    if msg.get("type") == "response.completed":
                        break

        content_events = [e for e in events if e.get("type") == "response.output_item.added"]
        completion_events = [e for e in events if e.get("type") == "response.completed"]
        assert len(content_events) == 2
        assert len(completion_events) == 1
        assert content_events[0]["item"]["content"][0]["text"] == "Hello"

    @pytest.mark.asyncio
    async def test_websocket_error_sends_error_message(self) -> None:
        from starlette.testclient import TestClient
        from starlette.websockets import WebSocket as StarletteWS

        from thegent.routing.litellm_responses_handler import handle_responses_websocket

        bad_exc = ValueError("invalid model xyz")
        mock_router = MagicMock()
        mock_router.acompletion = lambda **kwargs: _AsyncGenRaise(bad_exc)

        async def ws_endpoint(websocket: StarletteWS) -> None:
            await handle_responses_websocket(websocket)

        with patch(
            "thegent.routing.litellm_responses_handler.get_litellm_router",
            return_value=mock_router,
        ):
            from starlette.applications import Starlette
            from starlette.routing import WebSocketRoute

            app = Starlette(routes=[WebSocketRoute("/ws", ws_endpoint)])
            client = TestClient(app)

            with client.websocket_connect("/ws") as ws:
                ws.send_json(_make_responses_body(model="bad-model"))
                msg = ws.receive_json()

        assert "error" in msg
        assert "invalid model xyz" in msg["error"]["message"]
        assert msg["error"]["type"] == "ValueError"
