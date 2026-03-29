"""HTTP client adapter for cliproxy backend requests.

Handles:
- HTTP request/response proxying
- SSE streaming
- Request transformation (Responses -> Chat Completions)
- Response transformation
- Error handling and retries
- OpenRouter-specific logic
- LLM response caching (FR-CACHE-002)
"""

import asyncio
import httpx
import logging
from typing import Any

import orjson as json

_log = logging.getLogger(__name__)

# Completion paths that are eligible for response caching.
_CACHEABLE_PATHS: frozenset[str] = frozenset({
    "/v1/chat/completions",
    "/v1/completions",
    "/v1/responses",
})


def _is_cacheable_request(method: str, path: str, body: bytes) -> bool:
    """Return True when the request is a non-streaming completion POST."""
    if method.upper() != "POST":
        return False
    base_path = path.split("?", maxsplit=1)[0].rstrip("/")
    if base_path not in _CACHEABLE_PATHS:
        return False
    # Streaming responses cannot be replayed from cache.
    try:
        payload = json.loads(body) if body else {}
        return not payload.get("stream", False)
    except (json.JSONDecodeError, ValueError):
        return False


class CliproxyHTTPClient:
    """HTTP client for cliproxy backend communication.

    Args:
        backend_url:    URL of the cliproxy backend.
        timeout:        Request timeout in seconds.
        response_cache: Optional :class:`~thegent.cache.ResponseCache`
                        instance.  Pass ``None`` (default) to use the
                        module-level default cache, or pass a cache
                        constructed with ``enabled=False`` to disable
                        caching entirely (equivalent to ``--no-cache``).
    """

    def __init__(
        self,
        backend_url: str,
        timeout: float = 120.0,
        response_cache: "Any | None" = None,
    ) -> None:
        self.backend_url = backend_url.rstrip("/")
        self.timeout = timeout
        self._response_cache = response_cache  # None = lazy-load default

    def _cache(self) -> "Any":
        """Return the active ResponseCache (lazy-initialised on first use)."""
        if self._response_cache is None:
            from thegent.cache.response_cache import get_default_cache
            self._response_cache = get_default_cache()
        return self._response_cache

    async def proxy_request(
        self,
        request_method: str,
        request_path: str,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
        query_string: str = "",
    ) -> tuple[int, bytes, dict[str, str]]:
        """Proxy non-streaming HTTP request.

        For eligible completion endpoints the response is served from
        the :class:`~thegent.cache.ResponseCache` when available,
        avoiding a round-trip to the LLM backend.  Cache is keyed on
        the full canonical request body so only byte-identical requests
        are matched.

        Returns (status_code, response_body, response_headers).
        """
        headers = headers or {}
        url = self._build_url(request_path, query_string)
        cache = self._cache()

        # ------------------------------------------------------------------
        # Cache read (only for eligible non-streaming completions)
        # ------------------------------------------------------------------
        cache_key: str | None = None
        if _is_cacheable_request(request_method, request_path, body):
            try:
                payload: dict[str, Any] = json.loads(body) if body else {}
                cache_key = cache.make_key(
                    model=str(payload.get("model", "")),
                    messages=list(payload.get("messages", [])),
                    temperature=float(payload.get("temperature", 1.0)),
                    extra={
                        k: payload[k]
                        for k in ("max_tokens", "system", "top_p")
                        if k in payload
                    },
                )
                cached = cache.get(cache_key)
                if cached is not None:
                    cached_body = json.dumps(cached)
                    return 200, cached_body, {"Content-Type": "application/json", "X-Cache": "HIT"}
            except Exception as exc:  # pragma: no cover — defensive
                _log.debug("Response cache lookup failed (ignored): %s", exc)

        # ------------------------------------------------------------------
        # Upstream request
        # ------------------------------------------------------------------
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.request(
                    request_method,
                    url,
                    content=body,
                    headers=headers,
                )

            filtered_headers = dict(resp.headers)

            # ----------------------------------------------------------------
            # Cache write (only on successful 200 responses)
            # ----------------------------------------------------------------
            if cache_key is not None and resp.status_code == 200:
                try:
                    response_dict = json.loads(resp.content)
                    cache.set(cache_key, response_dict)
                    filtered_headers["X-Cache"] = "MISS"
                except Exception as exc:  # pragma: no cover — defensive
                    _log.debug("Response cache store failed (ignored): %s", exc)

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
