"""HTTP client adapter for cliproxy backend requests.

Handles:
- HTTP request/response proxying
- SSE streaming
- Request transformation (Responses -> Chat Completions)
- Response transformation
- Error handling and retries
- OpenRouter-specific logic
"""

import asyncio
import httpx
import logging
from typing import Any

import orjson as json

_log = logging.getLogger(__name__)


class CliproxyHTTPClient:
    """HTTP client for cliproxy backend communication."""

    def __init__(self, backend_url: str, timeout: float = 120.0):
        self.backend_url = backend_url.rstrip("/")
        self.timeout = timeout

    async def proxy_request(
        self,
        request_method: str,
        request_path: str,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
        query_string: str = "",
    ) -> tuple[int, bytes, dict[str, str]]:
        """Proxy non-streaming HTTP request.

        Returns (status_code, response_body, response_headers).
        """
        headers = headers or {}
        url = self._build_url(request_path, query_string)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.request(
                    request_method,
                    url,
                    content=body,
                    headers=headers,
                )

            filtered_headers = dict(resp.headers)
            return resp.status_code, resp.content, filtered_headers

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            _log.error("Backend proxy unreachable: %s", e)
            error_body = json.dumps({
                "error": {
                    "message": f"Backend proxy ({self.backend_url}) unreachable."
                }
            }).encode()
            return 503, error_body, {"Content-Type": "application/json"}

    async def proxy_stream(
        self,
        request_method: str,
        request_path: str,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Proxy streaming HTTP request (SSE/Server-Sent Events).

        Returns async generator yielding response chunks.
        """
        headers = headers or {}
        url = self._build_url(request_path, "")

        async def stream_generator():
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        request_method,
                        url,
                        content=body,
                        headers=headers,
                    ) as resp:
                        if resp.status_code != 200:
                            err_body = await resp.aread()
                            _log.warning("Backend stream error %s", resp.status_code)
                            error = self._make_error_response(resp.status_code, err_body)
                            yield json.dumps(error).encode()
                            return

                        async for chunk in resp.aiter_bytes():
                            yield chunk
            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                _log.error("Backend stream connection failed: %s", e)
                error = {
                    "error": {
                        "message": f"Backend proxy ({self.backend_url}) unreachable."
                    }
                }
                yield json.dumps(error).encode()

        return stream_generator()

    def _build_url(self, path: str, query_string: str) -> str:
        """Build full backend URL."""
        if path.startswith("/"):
            url = f"{self.backend_url}{path}"
        else:
            url = f"{self.backend_url}/{path}"

        if query_string:
            url = f"{url}?{query_string}"
        return url

    @staticmethod
    def _make_error_response(status_code: int, body: bytes) -> dict[str, Any]:
        """Make error response dict from backend error."""
        try:
            error = json.loads(body)
            if isinstance(error, dict) and "error" in error:
                return error
        except json.JSONDecodeError:
            pass

        return {
            "error": {
                "code": status_code,
                "message": f"Backend error: {status_code}",
            }
        }


class CliproxyResponseTransformer:
    """Transforms responses between protocols."""

    @staticmethod
    def transform_models_response(
        response_body: bytes,
        inject_openrouter: bool = False,
    ) -> tuple[bytes, str] | None:
        """Transform /v1/models response to canonical format.

        Returns (transformed_body, etag) or None if not transformable.
        """
        try:
            from thegent.cliproxy_models_transform import (
                transform_models_response,
            )

            result = transform_models_response(
                response_body,
                inject_openrouter=inject_openrouter,
            )
            return result
        except Exception as e:
            _log.debug("Models response transform failed: %s", e)
            return None

    @staticmethod
    def transform_request_body(
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Transform /v1/responses request to /v1/chat/completions."""
        try:
            from thegent.cliproxy_request_transform import (
                _responses_to_chat_completions,
            )

            return _responses_to_chat_completions(body)
        except Exception as e:
            _log.warning("Request transform failed: %s", e)
            return body


class CliproxyHeaderManager:
    """Manages request/response headers for cliproxy."""

    @staticmethod
    def sanitize_outbound_headers(headers: dict[str, str]) -> dict[str, str]:
        """Sanitize headers for backend request."""
        try:
            from thegent.cliproxy_header_utils import (
                sanitize_outbound_request_headers,
            )

            return sanitize_outbound_request_headers(headers)
        except Exception:
            return headers

    @staticmethod
    def filter_inbound_headers(headers: dict[str, str]) -> dict[str, str]:
        """Filter headers from backend response."""
        try:
            from thegent.cliproxy_header_utils import (
                filter_inbound_response_headers,
            )

            return filter_inbound_response_headers(headers)
        except Exception:
            return headers

    @staticmethod
    def inject_openrouter_headers(
        headers: dict[str, str],
        backend_url: str,
    ) -> None:
        """Inject OpenRouter attribution headers if needed."""
        if "openrouter.ai" in backend_url:
            headers.setdefault("HTTP-Referer", "https://thegent.dev")
            headers.setdefault("X-Title", "thegent")
