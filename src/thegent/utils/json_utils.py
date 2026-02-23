"""Common JSON utilities for thegent.

Provides JSON parsing, loading, and saving with consistent error handling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import orjson


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON from a file."""
    return json.loads(path.read_text())


def save_json(path: Path, data: dict[str, Any], indent: int = 2) -> None:
    """Save JSON to a file."""
    path.write_text(json.dumps(data, indent=indent))


def load_json_fast(path: Path) -> dict[str, Any]:
    """Load JSON from a file using orjson (faster)."""
    return orjson.loads(path.read_bytes())


def save_json_fast(path: Path, data: dict[str, Any]) -> None:
    """Save JSON to a file using orjson (faster)."""
    path.write_bytes(orjson.dumps(data))


def parse_json(text: str) -> dict[str, Any] | None:
    """Parse JSON text, returning None on error."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def parse_json_fast(text: str) -> dict[str, Any] | None:
    """Parse JSON text using orjson, returning None on error."""
    try:
        return orjson.loads(text)
    except orjson.JSONDecodeError:
        return None


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    """Parse multiple JSON objects from text (JSONL format)."""
    results: list[dict[str, Any]] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line:
            obj = parse_json(line)
            if obj is not None:
                results.append(obj)
    return results


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key not found
    
    Example:
        safe_get(config, "database", "host", default="localhost")
    """
    current: Any = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current if current is not None else default

# Aliases for backward compatibility
json_loads = json.loads
json_dumps = json.dumps

