"""Error types for the Phenotype SDK.

Following ADR-001:
- Errors are structured and descriptive
- Errors include context for debugging
- Errors are typed for easy handling
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class SDKError(Exception):
    """Base class for all SDK errors."""

    def __init__(
        self,
        message: str,
        code: str = "SDK_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }


class ConfigurationError(SDKError):
    """Raised when SDK configuration is invalid."""

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            context=context,
        )


class AuthenticationError(SDKError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            context=context,
        )


class AuthorizationError(SDKError):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Authorization failed",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            context=context,
        )


class RateLimitError(SDKError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        context = context or {}
        if retry_after:
            context["retry_after"] = retry_after
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            context=context,
        )
        self.retry_after = retry_after


class APIError(SDKError):
    """Raised when API returns an error."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_data: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        context = context or {}
        context["status_code"] = status_code
        if response_data:
            context["response_data"] = response_data
        super().__init__(
            message=message,
            code=f"API_ERROR_{status_code}",
            context=context,
        )
        self.status_code = status_code
        self.response_data = response_data


class ValidationError(SDKError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_errors: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        context = context or {}
        if field_errors:
            context["field_errors"] = field_errors
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            context=context,
        )
        self.field_errors = field_errors or []


class TimeoutError(SDKError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_seconds: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        context = context or {}
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            context=context,
        )


class NetworkError(SDKError):
    """Raised when a network error occurs."""

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="NETWORK_ERROR",
            context=context,
        )


class NotFoundError(SDKError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        context = context or {}
        context["resource_type"] = resource_type
        context["resource_id"] = resource_id
        super().__init__(
            message=f"{resource_type} '{resource_id}' not found",
            code="NOT_FOUND_ERROR",
            context=context,
        )
