"""Coercion helpers for execution metadata parsing."""

from typing import Any


def as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    try:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int | float | str)):
            return float(value)
    except TypeError, ValueError:
        pass
    return default


def as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    try:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int | float | str)):
            return int(value)
    except TypeError, ValueError:
        pass
    return default


def as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int | float)):
        return bool(value)
    return default
