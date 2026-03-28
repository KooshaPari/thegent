"""Domain error types - Pure domain errors with no external dependencies.

Following ADR-001 dependency rule:
- domain/ contains ZERO external dependencies
- Only standard library imports allowed
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from phenotype_error.core import AppError, ErrorCode


@dataclass
class DomainError(AppError):
    """Base class for domain errors.
    
    Domain errors represent business rule violations
    and should be meaningful to domain experts.
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
class EntityNotFoundError(DomainError):
    """Raised when an entity cannot be found.
    
    Example:
        raise EntityNotFoundError(
            entity_type="Order",
            entity_id="order-123",
        )
    """
    
    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            context={"entity_type": entity_type, "entity_id": entity_id},
        )


@dataclass
class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated.
    
    Example:
        raise BusinessRuleViolationError(
            rule="minimum_order_value",
            details="Order value must be at least $10.00",
        )
    """
    
    def __init__(self, rule: str, details: str) -> None:
        super().__init__(
            message=f"Business rule violated: {rule}",
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            context={"rule": rule, "details": details},
        )


@dataclass
class ValidationError(DomainError):
    """Raised when domain validation fails.
    
    Example:
        raise ValidationError(
            field="email",
            value="invalid-email",
            constraint="Must be a valid email address",
        )
    """
    
    def __init__(self, field: str, value: Any, constraint: str) -> None:
        super().__init__(
            message=f"Validation failed for field '{field}'",
            code=ErrorCode.VALIDATION_ERROR,
            context={"field": field, "value": value, "constraint": constraint},
        )


@dataclass
class DuplicateEntityError(DomainError):
    """Raised when attempting to create a duplicate entity."""
    
    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(
            message=f"{entity_type} with identifier '{identifier}' already exists",
            code=ErrorCode.DUPLICATE_ENTITY,
            context={"entity_type": entity_type, "identifier": identifier},
        )


@dataclass
class InvalidStateTransitionError(DomainError):
    """Raised when an invalid state transition is attempted."""
    
    def __init__(
        self,
        entity_type: str,
        current_state: str,
        attempted_state: str,
    ) -> None:
        super().__init__(
            message=(
                f"Invalid state transition for {entity_type}: "
                f"{current_state} -> {attempted_state}"
            ),
            code=ErrorCode.INVALID_STATE_TRANSITION,
            context={
                "entity_type": entity_type,
                "current_state": current_state,
                "attempted_state": attempted_state,
            },
        )


__all__ = [
    "DomainError",
    "EntityNotFoundError",
    "BusinessRuleViolationError",
    "ValidationError",
    "DuplicateEntityError",
    "InvalidStateTransitionError",
]
