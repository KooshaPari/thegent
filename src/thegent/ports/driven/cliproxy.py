"""Port interface (Protocol) for cliproxy provider lifecycle.

Defines the contract for cliproxy management without tying to specific implementations.
"""

from typing import Any, Protocol, runtime_checkable
from pathlib import Path


@runtime_checkable
class CliproxyProvider(Protocol):
    """Interface for cliproxy provider lifecycle management."""

    def ensure_running(self) -> str:
        """Ensure cliproxy is running and return base_url.

        Raises FileNotFoundError if binary not available.
        Raises RuntimeError if startup fails.
        """
        ...

    def start_managed(self) -> tuple[Any | None, str]:
        """Start proxy and return (proc, base_url) for lifecycle management.

        proc is None if proxy already running. Caller must terminate proc.
        """
        ...

    def kill(self) -> bool:
        """Kill proxy process. Returns True if a process was killed."""
        ...

    def fetch_metrics(self) -> dict[str, dict] | None:
        """Fetch per-provider metrics from /v1/metrics/providers.

        Returns metrics dict or None if unavailable.
        """
        ...

    def get_last_metrics_status(self) -> dict[str, Any]:
        """Return status metadata from latest metrics fetch."""
        ...


class CliproxyCredentialsManager(Protocol):
    """Interface for cliproxy credentials and configuration."""

    def setup_provider(self, provider: str, api_key: str | None = None) -> int:
        """Setup provider with API key or OAuth.

        Returns 0 on success, 1 on skip, 2 on error.
        """
        ...

    def get_provider_config(self, provider: str) -> dict[str, Any] | None:
        """Get provider login configuration."""
        ...

    def has_credentials(self, provider: str) -> bool:
        """Check if provider already has credentials configured."""
        ...


class CliproxyHTTPAdapter(Protocol):
    """HTTP adapter interface for cliproxy requests."""

    def proxy_request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes, dict[str, str]]:
        """Proxy HTTP request to cliproxy backend.

        Returns (status_code, response_body, response_headers).
        """
        ...

    def proxy_stream(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Proxy streaming HTTP request (SSE).

        Returns async generator yielding response chunks.
        """
        ...
