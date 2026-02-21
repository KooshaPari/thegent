from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal

import httpx

from .types import RunResult, SessionInfo, StreamEvent, parse_run_result, parse_session_info, parse_stream_event


class ThegentClientError(RuntimeError):
    pass


class ThegentHTTPError(ThegentClientError):
    def __init__(self, status_code: int, detail: str, body: Any = None) -> None:
        super().__init__(f"thegent request failed ({status_code}): {detail}")
        self.status_code = status_code
        self.detail = detail
        self.body = body


class ThegentRequestError(ThegentHTTPError):
    """4xx class of HTTP errors from the thegent API."""


class ThegentAuthenticationError(ThegentRequestError):
    """401/403 authentication and authorization errors."""


class ThegentNotFoundError(ThegentRequestError):
    """404 not found errors."""


class ThegentRateLimitError(ThegentRequestError):
    """429 rate limit errors."""


class ThegentServerError(ThegentHTTPError):
    """5xx class of HTTP errors from the thegent API."""


def _extract_error_detail(response: httpx.Response) -> tuple[str, Any]:
    def _extract_message_from_list(values: list[Any]) -> str | None:
        for item in values:
            extracted = _extract_message(item)
            if extracted:
                return extracted
        return None

    def _extract_message(value: Any) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list):
            return _extract_message_from_list(value)
        if isinstance(value, dict):
            for nested_key in ("msg", "message", "detail", "reason", "title"):
                nested_message = value.get(nested_key)
                extracted = _extract_message(nested_message)
                if extracted:
                    return extracted
        return None

    body: Any = None
    detail = response.text.strip()
    with_context_body: Any = None
    try:
        with_context_body = response.json()
    except ValueError:
        with_context_body = None
    if with_context_body is not None:
        body = with_context_body
        if isinstance(body, dict):
            for key in ("detail", "error", "errors", "message"):
                value = body.get(key)
                extracted = _extract_message(value)
                if extracted:
                    detail = extracted
                    break
            else:
                detail = json.dumps(body, separators=(",", ":"))
        elif isinstance(body, list):
            extracted = _extract_message_from_list(body)
            if extracted:
                detail = extracted
            else:
                detail = json.dumps(body, separators=(",", ":"))
    if not detail:
        detail = f"HTTP {response.status_code}"
    return detail, body


def _raise_for_non_2xx(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return
    detail, body = _extract_error_detail(response)
    status_code = response.status_code
    if status_code in {401, 403}:
        raise ThegentAuthenticationError(status_code, detail, body=body)
    if status_code == 404:
        raise ThegentNotFoundError(status_code, detail, body=body)
    if status_code == 429:
        raise ThegentRateLimitError(status_code, detail, body=body)
    if 400 <= status_code < 500:
        raise ThegentRequestError(status_code, detail, body=body)
    if 500 <= status_code < 600:
        raise ThegentServerError(status_code, detail, body=body)
    raise ThegentHTTPError(status_code, detail, body=body)


class ThegentClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        protocol: Literal["rest", "mcp"] = "rest",
        timeout: float = 30.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._protocol = protocol
        self._request_id = 0
        self._owned_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        if self._owned_client:
            self._client.close()

    def __enter__(self) -> ThegentClient:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        self.close()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.request(
                method=method,
                url=f"{self._base_url}{path}",
                headers=self._headers(),
                json=json_body,
            )
        except httpx.HTTPError as exc:
            raise ThegentClientError(f"request failed: {exc}") from exc

        _raise_for_non_2xx(response)

        try:
            return response.json()
        except ValueError as exc:
            raise ThegentClientError("response was not valid JSON") from exc

    def _mcp_call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }
        response = self._request("POST", "/mcp", json_body=payload)
        if not isinstance(response, dict):
            raise ThegentClientError("MCP endpoint returned non-object response")
        error = response.get("error")
        if isinstance(error, dict):
            message = str(error.get("message") or "MCP tool call failed")
            raise ThegentClientError(message)
        result = response.get("result")
        if not isinstance(result, dict):
            raise ThegentClientError("MCP tool result was not an object")

        structured = result.get("structured_content", result.get("structuredContent"))
        if structured is not None:
            return structured

        content = result.get("content")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
            raw_text = "\n".join(part for part in text_parts if part.strip())
            if raw_text:
                try:
                    return json.loads(raw_text)
                except ValueError:
                    return raw_text
        return result

    def run(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        **opts: Any,
    ) -> RunResult:
        payload: dict[str, Any] = {"prompt": prompt}
        if model is not None:
            payload["model"] = model
        if provider is not None:
            payload["provider"] = provider
        payload.update(opts)

        if self._protocol == "mcp":
            data = self._mcp_call_tool("thegent_run", payload)
        else:
            data = self._request("POST", "/v1/run", json_body=payload)
        if not isinstance(data, dict):
            raise ThegentClientError("run endpoint returned non-object response")
        return parse_run_result(data)

    def list_sessions(self) -> list[SessionInfo]:
        if self._protocol == "mcp":
            data = self._mcp_call_tool("thegent_session_list", {"all": False, "limit": 50})
        else:
            data = self._request("GET", "/v1/sessions")
        rows: Any = data
        if isinstance(data, dict):
            rows = data.get("sessions")
        if not isinstance(rows, list):
            raise ThegentClientError("list_sessions endpoint returned non-list response")
        if not all(isinstance(item, dict) for item in rows):
            raise ThegentClientError("list_sessions payload rows must be objects")
        return [parse_session_info(item) for item in rows]

    def resume(self, session_id: str, prompt: str | None = None) -> RunResult:
        cleaned = session_id.strip()
        if not cleaned:
            raise ThegentClientError("session_id must be non-empty")

        payload: dict[str, Any] = {}
        if prompt is not None:
            payload["prompt"] = prompt

        if self._protocol == "mcp":
            if payload:
                # thegent_resume MCP tool only accepts session_id.
                raise ThegentClientError("MCP resume does not accept prompt yet")
            data = self._mcp_call_tool("thegent_resume", {"session_id": cleaned})
        else:
            data = self._request("POST", f"/v1/sessions/{cleaned}/resume", json_body=payload)
        if not isinstance(data, dict):
            raise ThegentClientError("resume endpoint returned non-object response")
        raw_result = data.get("result") if isinstance(data.get("result"), dict) else data
        if not isinstance(raw_result, dict):
            raise ThegentClientError("resume endpoint returned non-object result payload")
        return parse_run_result(raw_result)

    def run_stream(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        **opts: Any,
    ) -> Iterator[StreamEvent]:
        payload: dict[str, Any] = {"prompt": prompt, "stream": True}
        if model is not None:
            payload["model"] = model
        if provider is not None:
            payload["provider"] = provider
        payload.update(opts)

        try:
            with self._client.stream(
                "POST",
                f"{self._base_url}/v1/run",
                headers=self._headers(),
                json=payload,
            ) as response:
                _raise_for_non_2xx(response)
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except ValueError as exc:
                        raise ThegentClientError("stream line was not valid JSON") from exc
                    if not isinstance(raw, dict):
                        raise ThegentClientError("stream line payload must be an object")
                    yield parse_stream_event(raw)
        except httpx.HTTPError as exc:
            raise ThegentClientError(f"request failed: {exc}") from exc


class AsyncThegentClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        protocol: Literal["rest", "mcp"] = "rest",
        timeout: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._protocol = protocol
        self._request_id = 0
        self._owned_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        if self._owned_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncThegentClient:
        return self

    async def __aexit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        await self.aclose()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        try:
            response = await self._client.request(
                method=method,
                url=f"{self._base_url}{path}",
                headers=self._headers(),
                json=json_body,
            )
        except httpx.HTTPError as exc:
            raise ThegentClientError(f"request failed: {exc}") from exc

        _raise_for_non_2xx(response)

        try:
            return response.json()
        except ValueError as exc:
            raise ThegentClientError("response was not valid JSON") from exc

    async def _mcp_call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }
        response = await self._request("POST", "/mcp", json_body=payload)
        if not isinstance(response, dict):
            raise ThegentClientError("MCP endpoint returned non-object response")
        error = response.get("error")
        if isinstance(error, dict):
            message = str(error.get("message") or "MCP tool call failed")
            raise ThegentClientError(message)
        result = response.get("result")
        if not isinstance(result, dict):
            raise ThegentClientError("MCP tool result was not an object")

        structured = result.get("structured_content", result.get("structuredContent"))
        if structured is not None:
            return structured

        content = result.get("content")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
            raw_text = "\n".join(part for part in text_parts if part.strip())
            if raw_text:
                try:
                    return json.loads(raw_text)
                except ValueError:
                    return raw_text
        return result

    async def run(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        **opts: Any,
    ) -> RunResult:
        payload: dict[str, Any] = {"prompt": prompt}
        if model is not None:
            payload["model"] = model
        if provider is not None:
            payload["provider"] = provider
        payload.update(opts)

        if self._protocol == "mcp":
            data = await self._mcp_call_tool("thegent_run", payload)
        else:
            data = await self._request("POST", "/v1/run", json_body=payload)
        if not isinstance(data, dict):
            raise ThegentClientError("run endpoint returned non-object response")
        return parse_run_result(data)

    async def list_sessions(self) -> list[SessionInfo]:
        if self._protocol == "mcp":
            data = await self._mcp_call_tool("thegent_session_list", {"all": False, "limit": 50})
        else:
            data = await self._request("GET", "/v1/sessions")
        rows: Any = data
        if isinstance(data, dict):
            rows = data.get("sessions")
        if not isinstance(rows, list):
            raise ThegentClientError("list_sessions endpoint returned non-list response")
        if not all(isinstance(item, dict) for item in rows):
            raise ThegentClientError("list_sessions payload rows must be objects")
        return [parse_session_info(item) for item in rows]

    async def resume(self, session_id: str, prompt: str | None = None) -> RunResult:
        cleaned = session_id.strip()
        if not cleaned:
            raise ThegentClientError("session_id must be non-empty")

        payload: dict[str, Any] = {}
        if prompt is not None:
            payload["prompt"] = prompt

        if self._protocol == "mcp":
            if payload:
                raise ThegentClientError("MCP resume does not accept prompt yet")
            data = await self._mcp_call_tool("thegent_resume", {"session_id": cleaned})
        else:
            data = await self._request("POST", f"/v1/sessions/{cleaned}/resume", json_body=payload)
        if not isinstance(data, dict):
            raise ThegentClientError("resume endpoint returned non-object response")
        raw_result = data.get("result") if isinstance(data.get("result"), dict) else data
        if not isinstance(raw_result, dict):
            raise ThegentClientError("resume endpoint returned non-object result payload")
        return parse_run_result(raw_result)

    async def run_stream(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        **opts: Any,
    ) -> AsyncIterator[StreamEvent]:
        payload: dict[str, Any] = {"prompt": prompt, "stream": True}
        if model is not None:
            payload["model"] = model
        if provider is not None:
            payload["provider"] = provider
        payload.update(opts)

        try:
            async with self._client.stream(
                "POST",
                f"{self._base_url}/v1/run",
                headers=self._headers(),
                json=payload,
            ) as response:
                _raise_for_non_2xx(response)
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except ValueError as exc:
                        raise ThegentClientError("stream line was not valid JSON") from exc
                    if not isinstance(raw, dict):
                        raise ThegentClientError("stream line payload must be an object")
                    yield parse_stream_event(raw)
        except httpx.HTTPError as exc:
            raise ThegentClientError(f"request failed: {exc}") from exc
