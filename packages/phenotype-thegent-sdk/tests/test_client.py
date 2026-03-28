from __future__ import annotations

import orjson as json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

SDK_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SDK_SRC))

from phenotype_thegent_sdk import (  # noqa: E402
    AsyncThegentClient,
    ThegentAuthenticationError,
    ThegentClient,
    ThegentClientError,
    ThegentHTTPError,
    ThegentNotFoundError,
    ThegentRateLimitError,
    ThegentRequestError,
    ThegentServerError,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _client_with_handler(handler: httpx.MockTransport) -> ThegentClient:
    return ThegentClient("https://example.test", api_key="test-key", http_client=httpx.Client(transport=handler))


def _async_client_with_handler(
    handler: httpx.MockTransport,
    *,
    protocol: str = "rest",
) -> AsyncThegentClient:
    return AsyncThegentClient(
        "https://example.test",
        api_key="test-key",
        protocol=protocol,
        http_client=httpx.AsyncClient(transport=handler),
    )


def test_run_success_maps_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/run"
        return httpx.Response(
            200,
            json={
                "exit_code": 0,
                "stdout": "ok",
                "stderr": "",
                "timed_out": False,
                "context_tokens_used": 25,
                "context_usage_ratio": 0.42,
            },
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    result = client.run("hello")
    assert result.exit_code == 0
    assert result.stdout == "ok"
    assert result.context_tokens_used == 25
    assert result.context_usage_ratio == pytest.approx(0.42)


def test_run_sends_model_provider_and_options() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, json={"exit_code": 0, "stdout": "", "stderr": ""})

    client = _client_with_handler(httpx.MockTransport(handler))
    client.run("hello", model="gpt-5", provider="openai", mode="fast")
    assert captured["payload"] == {"prompt": "hello", "model": "gpt-5", "provider": "openai", "mode": "fast"}


def test_run_includes_bearer_authorization_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == "Bearer test-key"
        return httpx.Response(200, json={"exit_code": 0, "stdout": "", "stderr": ""})

    client = _client_with_handler(httpx.MockTransport(handler))
    client.run("hello")


def test_run_raises_http_error_for_non_2xx() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="bad gateway")

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentServerError, match="500"):
        client.run("hello")


def test_run_raises_client_error_for_non_json_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="plain-text")

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentClientError, match="valid JSON"):
        client.run("hello")


def test_run_raises_client_error_for_non_object_payload() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["bad"])

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentClientError, match="non-object"):
        client.run("hello")


def test_list_sessions_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/sessions"
        return httpx.Response(
            200,
            json=[{"session_id": "s-1", "status": "running", "started_at": "2026-02-21T12:00:00Z", "agent": "codex"}],
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    sessions = client.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].session_id == "s-1"
    assert sessions[0].status == "running"


def test_list_sessions_accepts_wrapped_payload() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "sessions": [
                    {
                        "id": "run-1",
                        "run_id": "run-1",
                        "correlation_id": "sess-1",
                        "status": "running",
                        "started_at_utc": "2026-02-21T12:00:00Z",
                        "agent": "codex",
                        "model": "gpt-5",
                        "owner": "dev",
                    }
                ],
                "count": 1,
            },
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    sessions = client.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].session_id == "run-1"
    assert sessions[0].run_id == "run-1"
    assert sessions[0].correlation_id == "sess-1"
    assert sessions[0].started_at == "2026-02-21T12:00:00Z"
    assert sessions[0].model == "gpt-5"
    assert sessions[0].owner == "dev"


def test_list_sessions_requires_list_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"not": "a-list"})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentClientError, match="non-list"):
        client.list_sessions()


def test_list_sessions_requires_object_rows() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["bad-row"])

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentClientError, match="must be objects"):
        client.list_sessions()


def test_context_manager_closes_owned_client() -> None:
    with ThegentClient("https://example.test") as client:
        assert client._client.is_closed is False  # noqa: SLF001
    assert client._client.is_closed is True  # noqa: SLF001


def test_resume_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/sessions/s-1/resume"
        payload = json.loads(request.content)
        assert payload["prompt"] == "continue"
        return httpx.Response(200, json={"exit_code": 0, "stdout": "ok", "stderr": ""})

    client = _client_with_handler(httpx.MockTransport(handler))
    result = client.resume("s-1", prompt="continue")
    assert result.exit_code == 0
    assert result.stdout == "ok"


def test_resume_accepts_nested_result_payload() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": {"exit_code": 0, "stdout": "resumed", "stderr": ""}})

    client = _client_with_handler(httpx.MockTransport(handler))
    result = client.resume("s-2")
    assert result.stdout == "resumed"


def test_resume_rejects_empty_session_id() -> None:
    client = _client_with_handler(httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    with pytest.raises(ThegentClientError, match="session_id must be non-empty"):
        client.resume("  ")


def test_run_stream_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/run"
        payload = json.loads(request.content)
        assert payload["stream"] is True
        return httpx.Response(
            200,
            content=b'{"type":"delta","text":"a"}\n{"type":"completed","done":true}\n',
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    events = list(client.run_stream("hello"))
    assert [event.type for event in events] == ["delta", "completed"]
    assert events[0].payload["text"] == "a"
    assert events[1].payload["done"] is True


def test_run_stream_fixture_contract() -> None:
    fixture = FIXTURES_DIR / "run_stream_success.jsonl"
    payload = fixture.read_bytes()

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=payload)

    client = _client_with_handler(httpx.MockTransport(handler))
    events = list(client.run_stream("fixture"))
    assert [event.type for event in events] == ["delta", "delta", "completed"]
    assert events[0].payload["text"] == "hel"
    assert events[1].payload["text"] == "lo"
    assert events[2].payload["done"] is True


def test_run_stream_rejects_non_json_line() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b'{"type":"delta"}\nnot-json\n')

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentClientError, match="valid JSON"):
        list(client.run_stream("hello"))


def test_run_stream_raises_http_error_for_non_2xx() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited")

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRateLimitError, match="429"):
        list(client.run_stream("hello"))


def test_mcp_run_success_maps_structured_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/mcp"
        body = json.loads(request.content)
        assert body["method"] == "tools/call"
        assert body["params"]["name"] == "phenotype_thegent_run"
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {
                    "structuredContent": {"exit_code": 0, "stdout": "ok", "stderr": ""},
                },
            },
        )

    client = ThegentClient(
        "https://example.test", protocol="mcp", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    result = client.run("hello")
    assert result.exit_code == 0
    assert result.stdout == "ok"


def test_mcp_list_sessions_parses_text_json_content() -> None:
    payload = [{"run_id": "r-1", "status": "running", "agent": "codex"}]

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["params"]["name"] == "phenotype_thegent_session_list"
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {
                    "content": [{"type": "text", "text": json.dumps(payload).decode()}],
                },
            },
        )

    client = ThegentClient(
        "https://example.test", protocol="mcp", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    sessions = client.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].run_id == "r-1"
    assert sessions[0].status == "running"


def test_mcp_resume_maps_structured_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["params"]["name"] == "phenotype_thegent_resume"
        assert body["params"]["arguments"]["session_id"] == "s-1"
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {"structured_content": {"exit_code": 0, "stdout": "", "stderr": ""}},
            },
        )

    client = ThegentClient(
        "https://example.test", protocol="mcp", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    result = client.resume("s-1")
    assert result.exit_code == 0


def test_mcp_resume_rejects_prompt_argument() -> None:
    client = ThegentClient(
        "https://example.test",
        protocol="mcp",
        http_client=httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={}))),
    )
    with pytest.raises(ThegentClientError, match="does not accept prompt"):
        client.resume("s-1", prompt="continue")


def test_mcp_error_payload_raises_client_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "error": {"code": -32601, "message": "Method not found"},
            },
        )

    client = ThegentClient(
        "https://example.test", protocol="mcp", http_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    with pytest.raises(ThegentClientError, match="Method not found"):
        client.run("hello")


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [
        (400, ThegentRequestError),
        (401, ThegentAuthenticationError),
        (403, ThegentAuthenticationError),
        (404, ThegentNotFoundError),
        (429, ThegentRateLimitError),
        (500, ThegentServerError),
    ],
)
def test_http_error_type_mapping(status_code: int, error_type: type[ThegentHTTPError]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "mapped"})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(error_type) as exc_info:
        client.run("hello")
    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == "mapped"
    assert exc_info.value.body == {"detail": "mapped"}


def test_http_error_uses_json_message_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "backend exploded"})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentServerError, match="backend exploded"):
        client.run("hello")


def test_http_error_uses_nested_error_message_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "too many requests"}})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRateLimitError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "too many requests"
    assert exc_info.value.body == {"error": {"message": "too many requests"}}


def test_http_error_uses_nested_error_detail_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"detail": "bad request payload"}})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "bad request payload"
    assert exc_info.value.body == {"error": {"detail": "bad request payload"}}


def test_http_error_uses_nested_error_detail_list_message_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"detail": [{"msg": "field is required"}]}})

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "field is required"
    assert exc_info.value.body == {"error": {"detail": [{"msg": "field is required"}]}}


def test_http_error_uses_list_detail_message_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"detail": [{"loc": ["body", "prompt"], "msg": "prompt is required", "type": "value_error.missing"}]},
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "prompt is required"
    assert exc_info.value.body == {
        "detail": [{"loc": ["body", "prompt"], "msg": "prompt is required", "type": "value_error.missing"}]
    }


def test_http_error_uses_top_level_list_message_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json=[{"loc": ["body", "model"], "message": "model is invalid"}],
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "model is invalid"
    assert exc_info.value.body == [{"loc": ["body", "model"], "message": "model is invalid"}]


def test_http_error_uses_top_level_errors_list_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"errors": [{"loc": ["body", "prompt"], "msg": "prompt cannot be blank"}]},
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "prompt cannot be blank"
    assert exc_info.value.body == {"errors": [{"loc": ["body", "prompt"], "msg": "prompt cannot be blank"}]}


def test_http_error_uses_top_level_errors_title_fallback() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"errors": [{"title": "Request payload rejected"}]},
        )

    client = _client_with_handler(httpx.MockTransport(handler))
    with pytest.raises(ThegentRequestError) as exc_info:
        client.run("hello")
    assert exc_info.value.detail == "Request payload rejected"
    assert exc_info.value.body == {"errors": [{"title": "Request payload rejected"}]}


@pytest.mark.asyncio
async def test_async_run_stream_fixture_contract() -> None:
    fixture = FIXTURES_DIR / "run_stream_success.jsonl"
    payload = fixture.read_bytes()

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=payload)

    client = _async_client_with_handler(httpx.MockTransport(handler))
    events = [event async for event in client.run_stream("fixture")]
    await client.aclose()
    assert [event.type for event in events] == ["delta", "delta", "completed"]
    assert events[0].payload["text"] == "hel"
    assert events[1].payload["text"] == "lo"
    assert events[2].payload["done"] is True


@pytest.mark.asyncio
async def test_async_mcp_run_uses_tools_call() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["method"] == "tools/call"
        assert body["params"]["name"] == "phenotype_thegent_run"
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": body["id"],
                "result": {"structuredContent": {"exit_code": 0, "stdout": "ok", "stderr": ""}},
            },
        )

    client = _async_client_with_handler(httpx.MockTransport(handler), protocol="mcp")
    result = await client.run("hello")
    await client.aclose()
    assert result.stdout == "ok"
