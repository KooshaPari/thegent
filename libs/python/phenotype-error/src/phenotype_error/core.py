"""Core error types following hexagonal architecture.

This module contains the core error types that are framework-agnostic
and can be used throughout the application.

Following ADR-001:
- domain/ contains ZERO external dependencies
- Only standard library imports allowed
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Any


T = TypeVar("T")
E = TypeVar("E", bound="AppError")


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting."""
    
    DEBUG = auto()      # Debug information
    INFO = auto()       # Informational
    WARNING = auto()    # Warning condition
    ERROR = auto()      # Error condition
    CRITICAL = auto()   # Critical error


class ErrorCode(Enum):
    """Standardized error codes for the Phenotype ecosystem.
    
    Error codes follow the format: CATEGORY_SPECIFIC_ERROR
    - Use uppercase with underscores
    - Be specific about the error type
    - Include category prefix for organization
    """
    
    # General errors (1000-1999)
    UNKNOWN = "UNKNOWN"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    INVALID_STATE = "INVALID_STATE"
    TIMEOUT = "TIMEOUT"
    
    # Validation errors (2000-2999)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Domain errors (3000-3999)
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    DUPLICATE_ENTITY = "DUPLICATE_ENTITY"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    AGGREGATE_ERROR = "AGGREGATE_ERROR"
    
    # Infrastructure errors (4000-4999)
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    
    # Auth errors (5000-5999)
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Math errors (6000-6999)
    DIVISION_BY_ZERO = "DIVISION_BY_ZERO"
    OVERFLOW = "OVERFLOW"
    UNDERFLOW = "UNDERFLOW"
    PRECISION_LOSS = "PRECISION_LOSS"


@dataclass
class AppError(Exception):
    """Base class for all application errors.
    
    Following best practices:
    - Immutable dataclass
    - Structured error information
    - Chainable exceptions
    - Context preservation
    
    Attributes:
        code: Standardized error code
        message: Human-readable error message
        context: Additional context for debugging
        severity: Error severity level
        cause: Original exception if wrapping
        stack_trace: Stack trace if capturing
    """
    
    code: ErrorCode = ErrorCode.UNKNOWN
    message: str = "An unknown error occurred"
    context: dict[str, Any] = field(default_factory=dict)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    cause: Exception | None = None
    stack_trace: str | None = None
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.cause is not None and self.stack_trace is None:
            self.stack_trace = traceback.format_exception(
                type(self.cause),
                self.cause,
                self.cause.__traceback__
            )
    
    def with_context(self, **kwargs: Any) -> AppError:
        """Add context to the error.
        
        Args:
            **kwargs: Key-value pairs to add to context
            
        Returns:
            New AppError with additional context
        """
        new_context = {**self.context, **kwargs}
        return AppError(
            code=self.code,
            message=self.message,
            context=new_context,
            severity=self.severity,
            cause=self.cause,
            stack_trace=self.stack_trace,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "code": self.code.value,
            "message": self.message,
            "context": self.context,
            "severity": self.severity.name,
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.code.value}] {self.message}"


# Result type following functional programming patterns
# Similar to Rust's Result<T, E> or Haskell's Either


@dataclass
class Ok(Generic[T]):
    """Success variant of Result."""
    
    value: T
    
    def is_ok(self) -> bool:
        """Check if result is Ok."""
        return True
    
    def is_err(self) -> bool:
        """Check if result is Err."""
        return False
    
    def unwrap(self) -> T:
        """Unwrap the value."""
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Unwrap or return default."""
        return self.value
    
    def map(self, fn: callable[[T], Any]) -> Ok:
        """Map the value."""
        return Ok(fn(self.value))


@dataclass
class Err(Generic[E]):
    """Error variant of Result."""
    
    error: E
    
    def is_ok(self) -> bool:
        """Check if result is Ok."""
        return False
    
    def is_err(self) -> bool:
        """Check if result is Err."""
        return True
    
    def unwrap(self) -> Exception:
        """Unwrap the error."""
        if isinstance(self.error, Exception):
            raise self.error
        raise AppError(message=str(self.error))
    
    def unwrap_or(self, default: T) -> T:
        """Unwrap or return default."""
        return default
    
    def map(self, fn: callable) -> Err:
        """Map is no-op for Err."""
        return self


# Type alias for Result
Result = Ok[T] | Err[E]


__all__ = [
    "AppError",
    "ErrorCode",
    "ErrorSeverity",
    "Result",
    "Ok",
    "Err",
]
