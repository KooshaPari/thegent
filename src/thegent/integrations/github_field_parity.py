"""GitHub field update parity checker.

# @trace WL-162
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldParityReport:
    """Report on field parity between GitHub and local state."""

    field_name: str
    github_value: str | None
    local_value: str | None
    in_parity: bool


class GitHubFieldParityChecker:
    """Checks and reports on GitHub field update parity."""

    def check(self, field_name: str, github_value: str | None, local_value: str | None) -> FieldParityReport:
        """Check parity for a single field.

        Args:
            field_name: The name of the field to check.
            github_value: The current value in GitHub (or None).
            local_value: The current value in local state (or None).

        Returns:
            A FieldParityReport indicating parity status.
        """
        in_parity = github_value == local_value
        return FieldParityReport(
            field_name=field_name,
            github_value=github_value,
            local_value=local_value,
            in_parity=in_parity,
        )

    def check_all(self, fields: dict[str, tuple[str | None, str | None]]) -> list[FieldParityReport]:
        """Check parity for multiple fields.

        Args:
            fields: Dictionary mapping field_name to (github_value, local_value) tuples.

        Returns:
            List of FieldParityReport for all fields.
        """
        reports: list[FieldParityReport] = []
        for field_name, (github_val, local_val) in fields.items():
            report = self.check(field_name, github_val, local_val)
            reports.append(report)
        return reports

    def out_of_parity(self, reports: list[FieldParityReport]) -> list[FieldParityReport]:
        """Filter reports to only those out of parity.

        Args:
            reports: List of FieldParityReport to filter.

        Returns:
            Sublist of reports where in_parity is False.
        """
        return [r for r in reports if not r.in_parity]
