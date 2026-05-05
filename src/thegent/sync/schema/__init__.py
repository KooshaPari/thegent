"""Stub module."""


def detect_schema_drift(old_schema: dict, new_schema: dict) -> bool:
    """Detect if there is schema drift between old and new schemas."""
    return old_schema != new_schema


__all__ = ["detect_schema_drift"]
