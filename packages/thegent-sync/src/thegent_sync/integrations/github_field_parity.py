"""Parity helpers for comparing GitHub project fields to local state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

__all__ = ["FieldParityReport", "GitHubFieldParityChecker"]


@dataclass(frozen=True, slots=True)
class FieldParityReport:
    """Parity result for a single field."""

    field_name: str
    github_value: Any
    local_value: Any
    in_parity: bool


class GitHubFieldParityChecker:
    """Compute parity reports for GitHub-facing field values."""

    def check(self, field_name: str, github_value: Any, local_value: Any) -> FieldParityReport:
        return FieldParityReport(
            field_name=field_name,
            github_value=github_value,
            local_value=local_value,
            in_parity=github_value == local_value,
        )

    def check_all(self, field_values: dict[str, tuple[Any, Any]] | Iterable[tuple[str, tuple[Any, Any]]]) -> list[FieldParityReport]:
        items = field_values.items() if isinstance(field_values, dict) else field_values
        return [self.check(name, values[0], values[1]) for name, values in items]

    def out_of_parity(self, reports: Iterable[FieldParityReport]) -> list[FieldParityReport]:
        return [report for report in reports if not report.in_parity]
