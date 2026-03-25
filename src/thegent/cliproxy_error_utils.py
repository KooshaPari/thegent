# MIGRATION NOTE: Migrate to cliproxyapi-plusplus Go SDK
from __future__ import annotations

import orjson as json
from typing import Any

__all__ = [
    "_ERROR_MESSAGES",
    "_RETRY_MAX_ATTEMPTS",
    "InsufficientCreditsError",
    "_RetryableStreamError",
    "_make_error_body",
]

_ERROR_MESSAGES: dict[int, str] = {
    402: "Payment required — provider credit exhausted",
    408: "Request timeout — provider took too long to respond",
    429: "Rate limit exceeded",
    502: "Bad gateway — provider is down or returned an invalid response",
    503: "Service unavailable — no providers matched the request",
}

# OR-13: retry attempts per status code — 408/502/503 = transient, retryable.
_RETRY_MAX_ATTEMPTS: dict[int, int] = {408: 1, 502: 3, 503: 3}


class InsufficientCreditsError(RuntimeError):
    """OR-13: Raised when OpenRouter returns HTTP 402 (insufficient credits).

    MUST NOT be retried — callers must surface this error to the user immediately.
    """


class _RetryableStreamError(Exception):
    """OR-13: Internal signal that the stream got a retryable HTTP error (408/502/503)."""

    def __init__(self, status_code: int, raw_body: bytes) -> None:
        self.status_code = status_code
        self.raw_body = raw_body
        super().__init__(f"Backend returned {status_code}")


def _make_error_body(status_code: int, raw_body: bytes) -> dict[str, Any]:
    """GW-06: Parse or construct a structured error body for a backend error response."""
    try:
        obj = json.loads(raw_body.decode(errors="replace"))
        # Inject code + human message if missing
        if isinstance(obj, dict):
            err = obj.setdefault("error", {})
            if isinstance(err, dict):
                err.setdefault("code", status_code)
                if status_code in _ERROR_MESSAGES and not err.get("message"):
                    err["message"] = _ERROR_MESSAGES[status_code]
        return obj
    except json.JSONDecodeError, UnicodeDecodeError:
        msg = _ERROR_MESSAGES.get(status_code, f"Backend returned {status_code}")
        return {"error": {"message": msg, "code": status_code}}
