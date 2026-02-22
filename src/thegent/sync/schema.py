"""Schema drift detection primitives.

# @trace WL-210
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaDriftReport:
    missing_fields: list[str]
    unexpected_fields: list[str]

    @property
    def has_drift(self) -> bool:
        return bool(self.missing_fields or self.unexpected_fields)


def detect_schema_drift(*, mapped_fields: set[str], remote_fields: set[str]) -> SchemaDriftReport:
    missing = sorted(mapped_fields - remote_fields)
    unexpected = sorted(remote_fields - mapped_fields)
    return SchemaDriftReport(missing_fields=missing, unexpected_fields=unexpected)

