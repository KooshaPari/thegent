"""Workstream Schema Linter for validating workstream record structure.

WL-224: Workstream Schema Linter
Validates workstream records against required schema (id, title, status).

# @trace WL-224
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SchemaViolation:
    """Represents a schema violation in a workstream record."""

    field: str
    message: str
    severity: str = "error"


class WorkstreamSchemaLinter:
    """Lints workstream records for schema compliance."""

    def __init__(self) -> None:
        """Initialize the linter with required field definitions."""
        self._required_fields = {"id", "title", "status"}

    def lint(self, record: dict[str, Any]) -> list[SchemaViolation]:
        """Lint a single workstream record.

        Args:
            record: The record to lint.

        Returns:
            List of SchemaViolation instances for any schema issues.
        """
        violations: list[SchemaViolation] = []

        for field in self._required_fields:
            if field not in record:
                violations.append(
                    SchemaViolation(
                        field=field,
                        message=f"Missing required field: {field}",
                        severity="error",
                    )
                )
            elif not record[field]:
                violations.append(
                    SchemaViolation(
                        field=field,
                        message=f"Required field '{field}' is empty",
                        severity="error",
                    )
                )

        return violations

    def is_valid(self, record: dict[str, Any]) -> bool:
        """Check if a record is valid.

        Args:
            record: The record to validate.

        Returns:
            True if the record passes all schema checks, False otherwise.
        """
        return len(self.lint(record)) == 0

    def lint_many(self, records: list[dict[str, Any]]) -> dict[int, list[SchemaViolation]]:
        """Lint multiple records.

        Args:
            records: List of records to lint.

        Returns:
            Dictionary mapping record index to list of violations.
                Only includes indices with violations.
        """
        result: dict[int, list[SchemaViolation]] = {}

        for idx, record in enumerate(records):
            violations = self.lint(record)
            if violations:
                result[idx] = violations

        return result
