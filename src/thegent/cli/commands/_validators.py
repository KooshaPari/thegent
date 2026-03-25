"""Validation utilities for thegent CLI.

Common validation functions to reduce duplication.
"""

from __future__ import annotations

import re
from pathlib import Path


def validate_model_name(name: str) -> bool:
    """Validate a model name format."""
    if not name:
        return False
    # Allow alphanumeric, dash, underscore, colon, slash
    return bool(re.match(r"^[\w\-/:]+$", name))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")


def validate_path(path: str) -> Path | None:
    """Validate and return a path, or None if invalid."""
    try:
        return Path(path).expanduser().resolve()
    except Exception:
        return None


def validate_port(port: int) -> bool:
    """Validate a port number."""
    return 1 <= port <= 65535


def validate_timeout(timeout: int) -> bool:
    """Validate a timeout value in seconds."""
    return timeout > 0 and timeout <= 3600


def sanitize_filename(name: str) -> str:
    """Sanitize a filename by removing unsafe characters."""
    # Remove path separators and unsafe characters
    return re.sub(r"[/\\:*?\"<>|]", "_", name)


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate a string to max length."""
    if len(s) <= max_length:
        return s
    return s[: max_length - 3] + "..."
