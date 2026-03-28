"""Async and Sync clients for the Phenotype SDK.

Following ADR-001:
- Clean separation between sync and async clients
- Both clients share the same interface
- Uses httpx for HTTP requests
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

import httpx

from phenotype_sdk.config import Config
from phenotype_sdk.errors import (
    SDKError,
    APIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    TimeoutError,
    NetworkError,
)
from phenotype_sdk.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseClient:
    """Base client with shared functionality."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._client: httpx.Client | httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get common headers."""
        headers = {
            "User-Agent": f"phenotype-sdk/0.1.0",
            "Accept": "application/json",
        }

        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and convert to SDK errors."""
        if response.status_code == 401:
            raise AuthenticationError(
                message="Authentication failed",
                context={"status_code": 401},
            )

        if response.status_code == 403:
            raise AuthenticationError(
                message="Access forbidden",
                context={"status_code": 403},
            )

        if response.status_code == 404:
            raise NotFoundError(
                resource_type="resource",
                resource_id="unknown",
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message="Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"message": response.text}

            raise APIError(
                status_code=response.status_code,
                message=error_data.get("message", "API error"),
                response_data=error_data,
            )

        return response.json()


class SyncClient(BaseClient):
    """Synchronous client for the Phenotype API."""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._client = httpx.Client(
            base_url=config.api_base_url,
            timeout=httpx.Timeout(config.timeout_seconds),
            headers=self._get_headers(),
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            self._client.close()

    def __enter__(self) -> SyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def query(
        self,
        prompt: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a query to the API.

        Args:
            prompt: The prompt to send
            variables: Optional variables for the prompt
            **kwargs: Additional parameters

        Returns:
            API response as dictionary
        """
        logger.info("query", prompt=prompt[:100], variables=variables)

        payload = {
            "prompt": prompt,
            **(variables or {}),
            **kwargs,
        }

        try:
            response = self._client.post("/query", json=payload)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timed out: {e}",
                timeout_seconds=self.config.timeout_seconds,
            )
        except httpx.ConnectError as e:
            raise NetworkError(
                message=f"Connection error: {e}",
            )

    def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a task.

        Args:
            task: The task to execute
            context: Optional context
            **kwargs: Additional parameters

        Returns:
            Execution result as dictionary
        """
        logger.info("execute", task=task)

        payload = {
            "task": task,
            "context": context or {},
            **kwargs,
        }

        try:
            response = self._client.post("/execute", json=payload)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timed out: {e}",
                timeout_seconds=self.config.timeout_seconds,
            )


class AsyncClient(BaseClient):
    """Asynchronous client for the Phenotype API."""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._client = httpx.AsyncClient(
            base_url=config.api_base_url,
            timeout=httpx.Timeout(config.timeout_seconds),
            headers=self._get_headers(),
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def query(
        self,
        prompt: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a query to the API (async).

        Args:
            prompt: The prompt to send
            variables: Optional variables for the prompt
            **kwargs: Additional parameters

        Returns:
            API response as dictionary
        """
        logger.info("query", prompt=prompt[:100], variables=variables)

        payload = {
            "prompt": prompt,
            **(variables or {}),
            **kwargs,
        }

        try:
            response = await self._client.post("/query", json=payload)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timed out: {e}",
                timeout_seconds=self.config.timeout_seconds,
            )
        except httpx.ConnectError as e:
            raise NetworkError(
                message=f"Connection error: {e}",
            )

    async def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a task (async).

        Args:
            task: The task to execute
            context: Optional context
            **kwargs: Additional parameters

        Returns:
            Execution result as dictionary
        """
        logger.info("execute", task=task)

        payload = {
            "task": task,
            "context": context or {},
            **kwargs,
        }

        try:
            response = await self._client.post("/execute", json=payload)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(
                message=f"Request timed out: {e}",
                timeout_seconds=self.config.timeout_seconds,
            )
