"""Stub module."""

__all__ = ["validate_csm", "ValidationResult", "InvariantViolation", "SemanticValidationError", "ensure_valid_csm"]


def ensure_valid_csm(data: dict[str, object]) -> None:
    """Ensure CSM data is valid, raising an exception if not."""
    result = validate_csm(data)
    if not result.valid:
        raise SemanticValidationError(", ".join(result.errors))


class SemanticValidationError(Exception):
    """Exception raised when semantic validation fails."""


class InvariantViolation(Exception):
    """Exception raised when an invariant is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self, valid: bool, errors: list[str] | None = None) -> None:
        self.valid = valid
        self.errors = errors or []

    def to_dict(self) -> dict[str, object]:
        return {"valid": self.valid, "errors": self.errors}


def validate_csm(data: dict[str, object]) -> ValidationResult:
    """Validate a CSM document."""
    return ValidationResult(valid=True)
