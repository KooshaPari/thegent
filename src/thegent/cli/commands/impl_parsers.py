"""Parsing and normalization utility functions for CLI commands."""

from pathlib import Path
from typing import Any
import logging

_log = logging.getLogger(__name__)


def _normalize_image_paths(image_paths: list[str] | None) -> list[str]:
    if image_paths is None:
        return []
    return [p for p in image_paths if Path(p).is_file()]


def _build_run_event_details(
    *,
    stage: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
    tool_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = {}
    if stage:
        result["stage"] = stage
    if messages:
        result["messages"] = messages
    if tool_calls:
        result["tool_calls"] = tool_calls
    if tool_results:
        result["tool_results"] = tool_results
    return result


def _escape_cell(text: str) -> str:
    """Escape pipe characters in text for table display."""
    return text.replace("|", "\\|") if text else ""


__all__ = [
    "_normalize_image_paths",
    "_build_run_event_details",
    "_escape_cell",
]
