"""API error types - HTTP and API-specific errors.

These errors are used when building REST APIs
and communicating with external APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from phenotype_error.core import AppError, ErrorCode


class HttpStatusCode(Enum):
    """Standard HTTP status codes."""
    
    # 1xx Informational
    CONTINUE = (100, "Continue")
    SWITCHING_PROTOCOLS = (101, "Switching Protocols")
    
    # 2xx Success
    OK = (200, "OK")
    CREATED = (201, "Created")
    ACCEPTED = (202, "Accepted")
    NO_CONTENT = (204, "No Content")
    
    # 3xx Redirection
    MOVED_PERMANENTLY = (301, "Moved Permanently")
    FOUND = (302, "Found")
    SEE_OTHER = (303, "See Other")
    NOT_MODIFIED = (304, "Not Modified")
    
    # 4xx Client Errors
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    METHOD_NOT_ALLOWED = (405, "Method Not Allowed")
    CONFLICT = (409, "Conflict")
    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity")
    TOO_MANY_REQUESTS = (429, "Too Many Requests")
    
    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    NOT_IMPLEMENTED = (501, "Not Implemented")
    BAD_GATEWAY = (502, "Bad Gateway")
    SERVICE_UNAVAILABLE = (503, "Service Unavailable")
    GATEWAY_TIMEOUT = (504, "Gateway Timeout")
    
    def __init__(self, code: int, phrase: str) -> None:
        self._code = code
        self._phrase = phrase
    
    @property
    def code(self) -> int:
        return self._code
    
    @property
    def phrase(self) -> str:
        return self._phrase


@dataclass
class HttpError(AppError):
    """Base class for HTTP errors."""
    
    status_code: HttpStatusCode = HttpStatusCode.INTERNAL_SERVER_ERROR
    
    def __init__(
        self,
        message: str,
        status_code: HttpStatusCode = HttpStatusCode.INTERNAL_SERVER_ERROR,
        headers: dict[str, str] | None = None,
        code: ErrorCode = ErrorCode.UNKNOWN,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            context=context or {},
        )
        self.status_code = status_code
        self.headers = headers or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        result = super().to_dict()
        result["status_code"] = self.status_code.code
        result["status_phrase"] = self.status_code.phrase
        return result


@dataclass
class BadRequestError(HttpError):
    """400 Bad Request error."""
    
    def __init__(
        self,
        message: str = "Bad request",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=HttpStatusCode.BAD_REQUEST,
            code=ErrorCode.INVALID_INPUT,
            context=context,
        )


@dataclass
class UnauthorizedError(HttpError):
    """401 Unauthorized error."""
    
    def __init__(
        self,
        message: str = "Unauthorized",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=HttpStatusCode.UNAUTHORIZED,
            code=ErrorCode.AUTHENTICATION_ERROR,
            context=context,
        )


@dataclass
class ForbiddenError(HttpError):
    """403 Forbidden error."""
    
    def __init__(
        self,
        message: str = "Forbidden",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=HttpStatusCode.FORBIDDEN,
            code=ErrorCode.AUTHORIZATION_ERROR,
            context=context,
        )


@dataclass
class NotFoundError(HttpError):
    """404 Not Found error."""
    
    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=HttpStatusCode.NOT_FOUND,
            code=ErrorCode.ENTITY_NOT_FOUND,
            context={"resource": resource, "identifier": identifier, **(context or {})},
        )


@dataclass
class ConflictError(HttpError):
    """409 Conflict error."""
    
    def __init__(
        self,
        message: str = "Conflict",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=HttpStatusCode.CONFLICT,
            code=ErrorCode.DUPLICATE_ENTITY,
            context=context,
        )


@dataclass
class ValidationError(HttpError):
    """422 Unprocessable Entity error for validation failures."""
    
    def __init__(
        self,
        errors: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message="Validation failed",
            status_code=HttpStatusCode.UNPROCESSABLE_ENTITY,
            code=ErrorCode.VALIDATION_ERROR,
            context={"validation_errors": errors, **(context or {})},
        )


__all__ = [
    "HttpStatusCode",
    "HttpError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
]
