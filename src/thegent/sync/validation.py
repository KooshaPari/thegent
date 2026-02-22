"""Required-field validation gate.

# @trace WL-211
"""

from __future__ import annotations


def validate_required_fields(*, required_fields: set[str], available_fields: set[str]) -> None:
    missing = sorted(required_fields - available_fields)
    if not missing:
        return
    raise ValueError(f"missing required fields: {', '.join(missing)}")
