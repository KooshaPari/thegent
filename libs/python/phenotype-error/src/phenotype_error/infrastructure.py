"""Infrastructure error types - Errors from external systems.

These errors wrap infrastructure-level failures like
database errors, cache errors, and external service failures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from phenotype_error.core import AppError, ErrorCode


@dataclass
class InfrastructureError(AppError):
    """Base class for infrastructure errors.
    
    These errors typically indicate problems with
    external systems like databases, caches, or networks.
    """
    
    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.UNKNOWN,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            context=context or {},
        )


@dataclass
class DatabaseError(InfrastructureError):
    """Raised when a database operation fails.
    
    Example:
        raise DatabaseError(
            operation="SELECT",
            table="orders",
            cause=original_exception,
        )
    """
    
    def __init__(
        self,
        operation: str,
        table: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Database error during {operation}",
            code=ErrorCode.DATABASE_ERROR,
            context={
                "operation": operation,
                "table": table,
            },
        )
        if cause:
            self.cause = cause


@dataclass
class CacheError(InfrastructureError):
    """Raised when a cache operation fails."""
    
    def __init__(
        self,
        operation: str,
        key: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Cache error during {operation}",
            code=ErrorCode.CACHE_ERROR,
            context={
                "operation": operation,
                "key": key,
            },
        )
        if cause:
            self.cause = cause


@dataclass
class ExternalServiceError(InfrastructureError):
    """Raised when an external service call fails."""
    
    def __init__(
        self,
        service_name: str,
        operation: str,
        status_code: int | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"External service '{service_name}' error during {operation}",
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            context={
                "service_name": service_name,
                "operation": operation,
                "status_code": status_code,
            },
        )
        if cause:
            self.cause = cause


@dataclass
class NetworkError(InfrastructureError):
    """Raised when a network operation fails."""
    
    def __init__(
        self,
        host: str,
        port: int | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Network error connecting to {host}",
            code=ErrorCode.NETWORK_ERROR,
            context={
                "host": host,
                "port": port,
            },
        )
        if cause:
            self.cause = cause


@dataclass
class ConnectionError(InfrastructureError):
    """Raised when a connection cannot be established."""
    
    def __init__(
        self,
        endpoint: str,
        timeout_seconds: float | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"Connection error to {endpoint}",
            code=ErrorCode.CONNECTION_ERROR,
            context={
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
            },
        )
        if cause:
            self.cause = cause


__all__ = [
    "InfrastructureError",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
    "NetworkError",
    "ConnectionError",
]
