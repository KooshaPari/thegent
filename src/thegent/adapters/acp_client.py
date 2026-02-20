"""ACP (Agent Communication Protocol) HTTP client adapter.

Allows thegent to send tasks to remote ACP-compatible agents over HTTP.

Complements the stdio-based ACPClientAdapter in thegent.acp.client.

Config (all optional — can also be passed to constructor directly):
    THGENT_ACP_BASE_URL  - ACP server base URL (default: http://localhost:8080)
    THGENT_ACP_AGENT_ID  - Sender agent ID (default: "thegent")

# @trace FR-ACP-001
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:8080"
_DEFAULT_AGENT_ID = "thegent"

_MAX_RETRY_ATTEMPTS = 4
_RETRY_MIN_WAIT = 1.0
_RETRY_MAX_WAIT = 30.0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ACPClientError(Exception):
    """Raised when the ACP server returns a non-retryable error."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"ACP server error {status_code}: {message}")
        self.status_code = status_code


class ACPServerUnreachableError(Exception):
    """Raised when the ACP server is unreachable after all retries."""


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class ACPResult:
    """Result returned by ACPClient.send_task().

    Attributes:
        success:    True if the task completed without error.
        result:     Text result returned by the remote agent.
        agent_id:   Identifier of the remote agent that processed the task.
        elapsed_ms: Wall-clock time spent on the request (milliseconds).
    """

    success: bool
    result: str
    agent_id: str
    elapsed_ms: float


# ---------------------------------------------------------------------------
# Retry predicate
# ---------------------------------------------------------------------------


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient errors that warrant a retry (429, 503, network).

    Args:
        exc: The exception to inspect.

    Returns:
        True when the error is considered transient.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 503)
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError)):
        return True
    return False


# ---------------------------------------------------------------------------
# ACPClient
# ---------------------------------------------------------------------------


class ACPClient:
    """HTTP client for ACP-compatible agent servers.

    Sends tasks to a remote ACP server and returns structured results.
    Uses httpx.AsyncClient for all I/O and tenacity with
    wait_random_exponential for retry on 429/503 and transient network errors.

    Example::

        client = ACPClient(base_url="http://agent.example.com:8080")
        result = await client.send_task("Summarise the latest PR diffs")
        if result.success:
            print(result.result)

    Args:
        base_url:  Base URL of the ACP server (no trailing slash).
        agent_id:  Identifier sent as the ``X-Agent-ID`` header and in the
                   request body.  Defaults to ``"thegent"``.
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        agent_id: str = _DEFAULT_AGENT_ID,
    ) -> None:
        """Initialise the client.

        Args:
            base_url:  ACP server base URL, e.g. ``"http://localhost:8080"``.
            agent_id:  Logical sender ID embedded in outgoing requests.
        """
        self._base_url = base_url.rstrip("/")
        self._agent_id = agent_id

        logger.debug(
            "ACPClient initialised (base_url=%s, agent_id=%s)",
            self._base_url,
            self._agent_id,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_client(self, timeout: float) -> httpx.AsyncClient:
        """Create a configured AsyncClient instance.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            A fresh httpx.AsyncClient ready for use as an async context manager.
        """
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Agent-ID": self._agent_id,
            },
            timeout=httpx.Timeout(timeout),
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise an appropriate exception for non-2xx responses.

        Retryable statuses (429, 503) raise httpx.HTTPStatusError so tenacity
        can detect and retry them.  All other non-2xx statuses raise
        ACPClientError immediately.

        Args:
            response: The httpx response to inspect.

        Raises:
            httpx.HTTPStatusError: For 429/503 (retryable).
            ACPClientError:        For all other non-2xx statuses.
        """
        if response.is_success:
            return
        if response.status_code in (429, 503):
            response.raise_for_status()  # lets tenacity catch it
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        raise ACPClientError(response.status_code, detail)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def send_task(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> ACPResult:
        """Send a task to the remote ACP agent and return the result.

        The request is posted to ``POST /tasks`` with a JSON body::

            {
                "task": "<task text>",
                "agent_id": "<sender agent id>",
                "context": { ... }   # omitted when None
            }

        The server is expected to respond with::

            {
                "result": "<agent output>",
                "agent_id": "<remote agent id>"
            }

        Retries are performed automatically on 429, 503, and transient
        network errors using exponential back-off with jitter.

        Args:
            task:    Task description / prompt to send.
            context: Optional key-value context attached to the request body.
            timeout: Per-attempt HTTP timeout in seconds (default 30.0).

        Returns:
            ACPResult with success, result text, remote agent_id, and elapsed_ms.

        Raises:
            ACPServerUnreachableError: When all retry attempts fail due to
                                       network-level errors (ConnectError,
                                       TimeoutException, etc.).
            ACPClientError:            On non-retryable server errors (4xx
                                       excluding 429, 5xx excluding 503).
        """
        payload: dict[str, Any] = {
            "task": task,
            "agent_id": self._agent_id,
        }
        if context:
            payload["context"] = context

        start = time.monotonic()

        @retry(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=_RETRY_MIN_WAIT, max=_RETRY_MAX_WAIT),
            stop=stop_after_attempt(_MAX_RETRY_ATTEMPTS),
            reraise=True,
        )
        async def _do_send() -> dict[str, Any]:
            async with self._make_client(timeout) as client:
                response = await client.post("/tasks", json=payload)
                self._raise_for_status(response)
                data: dict[str, Any] = response.json()
                return data

        try:
            data = await _do_send()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as exc:
            raise ACPServerUnreachableError(
                f"ACP server at {self._base_url} is unreachable after {_MAX_RETRY_ATTEMPTS} "
                f"attempts: {exc}"
            ) from exc

        elapsed_ms = (time.monotonic() - start) * 1000
        remote_agent_id: str = data.get("agent_id", "unknown")
        result_text: str = data.get("result", "")

        logger.debug(
            "ACP task completed (agent_id=%s, elapsed_ms=%.1f)",
            remote_agent_id,
            elapsed_ms,
        )

        return ACPResult(
            success=True,
            result=result_text,
            agent_id=remote_agent_id,
            elapsed_ms=elapsed_ms,
        )

    async def health_check(self) -> bool:
        """Check whether the ACP server is reachable and healthy.

        Issues a ``GET /health`` request.  Returns True if the server
        responds with any 2xx status, False for all other outcomes
        (unreachable, 4xx, 5xx).

        Returns:
            True if the server is healthy, False otherwise.
        """
        try:
            async with self._make_client(timeout=5.0) as client:
                response = await client.get("/health")
                healthy = response.is_success
                logger.debug(
                    "ACP health check %s (status=%d, base_url=%s)",
                    "OK" if healthy else "FAILED",
                    response.status_code,
                    self._base_url,
                )
                return healthy
        except Exception as exc:
            logger.debug("ACP health check failed (base_url=%s): %s", self._base_url, exc)
            return False
