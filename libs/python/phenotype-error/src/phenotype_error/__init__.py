"""Phenotype Error Handling Library.

A comprehensive error handling library following:
- Hexagonal Architecture (Ports & Adapters)
- Clean Architecture principles
- SOLID principles
- xDD methodologies (TDD, BDD, DDD)

Usage:
    from phenotype_error import AppError, ErrorCode, Result
    
    def divide(a: int, b: int) -> Result[int, AppError]:
        if b == 0:
            return Err(AppError(
                code=ErrorCode.DIVISION_BY_ZERO,
                message="Cannot divide by zero",
                context={"a": a, "b": b}
            ))
        return Ok(a // b)
"""

from phenotype_error.core import (
    AppError,
    ErrorCode,
    ErrorSeverity,
    Result,
    Ok,
    Err,
)
from phenotype_error.domain import (
    DomainError,
    EntityNotFoundError,
    BusinessRuleViolationError,
    ValidationError,
)
from phenotype_error.infrastructure import (
    InfrastructureError,
    DatabaseError,
    CacheError,
    ExternalServiceError,
)
from phenotype_error.api import (
    HttpError,
    HttpStatusCode,
    ValidationError as ApiValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Core
    "AppError",
    "ErrorCode",
    "ErrorSeverity",
    "Result",
    "Ok",
    "Err",
    # Domain
    "DomainError",
    "EntityNotFoundError",
    "BusinessRuleViolationError",
    "ValidationError",
    # Infrastructure
    "InfrastructureError",
    "DatabaseError",
    "CacheError",
    "ExternalServiceError",
    # API
    "HttpError",
    "HttpStatusCode",
    "ApiValidationError",
]
