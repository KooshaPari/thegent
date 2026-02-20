"""Task validation implementation."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from thegent.infra.fast_json_schema import FastJSONSchemaValidator, get_schema_validator
from thegent.task.parser import TaskParseError, parse_task_file

_log = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Single validation error."""

    field: str
    message: str
    code: str
    path: list[str]


@dataclass
class ValidationResult:
    """Task validation result."""

    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]

    def format_errors(self) -> str:
        """Format errors for display."""
        lines = []
        for error in self.errors:
            path_str = ".".join(error.path) if error.path else error.field
            lines.append(f"{path_str}: {error.message} ({error.code})")
        return "\n".join(lines)


class TaskValidator:
    """Task validator using JSON Schema."""

    def __init__(self, schema_path: Path | None = None) -> None:
        """Initialize validator with schema.

        Args:
            schema_path: Path to JSON Schema file (defaults to schemas/task-input.schema.json)
        """
        if schema_path is None:
            # Default to schemas directory relative to package root
            package_root = Path(__file__).parent.parent.parent.parent
            schema_path = package_root / "schemas" / "task-input.schema.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        self.schema_path = schema_path
        self.schema = json.loads(schema_path.read_text())
        self.validator = FastJSONSchemaValidator(self.schema)

    def validate(self, task: dict[str, Any]) -> ValidationResult:
        """Validate a task dictionary.

        Args:
            task: Task dictionary to validate

        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []

        # Schema validation using fast validator
        try:
            self.validator.validate(task)
        except Exception as e:
            # Convert validation error to our format
            error_msg = str(e)
            # Try to extract field path from error message
            field = "root"
            path_parts = []
            if ":" in error_msg:
                parts = error_msg.split(":", 1)
                field = parts[0].strip()
                error_msg = parts[1].strip()
                if "." in field:
                    path_parts = field.split(".")
            errors.append(
                ValidationError(
                    field=field,
                    message=error_msg,
                    code="validation_error",
                    path=path_parts,
                )
            )

        # Custom validation
        custom_errors = self._validate_custom(task)
        errors.extend(custom_errors)

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a task file.

        Args:
            file_path: Path to task file

        Returns:
            ValidationResult with validation status and errors
        """
        try:
            task = parse_task_file(file_path)
            return self.validate(task)
        except TaskParseError as e:
            return ValidationResult(
                valid=False,
                errors=[
                    ValidationError(
                        field="file",
                        message=f"Failed to parse file: {e}",
                        code="parse_error",
                        path=[],
                    )
                ],
                warnings=[],
            )
        except Exception as e:
            _log.exception(f"Unexpected error validating {file_path}")
            return ValidationResult(
                valid=False,
                errors=[
                    ValidationError(
                        field="file",
                        message=f"Unexpected error: {e}",
                        code="unexpected_error",
                        path=[],
                    )
                ],
                warnings=[],
            )

    def _validate_custom(self, task: dict[str, Any]) -> list[ValidationError]:
        """Custom validation rules.

        Args:
            task: Task dictionary

        Returns:
            List of custom validation errors
        """
        errors = []
        import re

        # Validate task ID format
        task_id = task.get("id", "")
        if task_id and not re.match(r"^[a-z0-9-]+$", task_id):
            errors.append(
                ValidationError(
                    field="id",
                    message=f"Task ID must be lowercase alphanumeric with hyphens, got '{task_id}'",
                    code="invalid_format",
                    path=["id"],
                )
            )

        # Validate dependencies format
        depends = task.get("depends", [])
        for dep_id in depends:
            if not isinstance(dep_id, str) or not re.match(r"^[a-z0-9-]+$", dep_id):
                errors.append(
                    ValidationError(
                        field="depends",
                        message=f"Invalid dependency ID format: {dep_id}",
                        code="invalid_format",
                        path=["depends"],
                    )
                )

        return errors


def validate_task(task: dict[str, Any], schema_path: Path | None = None) -> ValidationResult:
    """Validate a task dictionary.

    Convenience function that creates a validator and validates.

    Args:
        task: Task dictionary to validate
        schema_path: Optional path to schema file

    Returns:
        ValidationResult
    """
    validator = TaskValidator(schema_path=schema_path)
    return validator.validate(task)


def validate_task_file(file_path: Path, schema_path: Path | None = None) -> ValidationResult:
    """Validate a task file.

    Convenience function that creates a validator and validates.

    Args:
        file_path: Path to task file
        schema_path: Optional path to schema file

    Returns:
        ValidationResult
    """
    validator = TaskValidator(schema_path=schema_path)
    return validator.validate_file(file_path)
