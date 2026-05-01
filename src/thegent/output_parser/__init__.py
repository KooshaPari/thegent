"""STUB MODULE - thegent.output_parser

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

OUTPUT_PARSER_SCHEMA_VERSION = "1.0.0"
PARSE_EMPTY = ""
PARSE_OK = "ok"
PARSE_TRUNCATED = "truncated"


@dataclass
class ParseResult:
    """Result of parsing output."""
    success: bool
    data: dict[str, Any] | None = None
    error: str = ""


# Stub implementation - functionality not available
__all__ = ["OUTPUT_PARSER_SCHEMA_VERSION", "PARSE_EMPTY", "PARSE_OK", "PARSE_TRUNCATED", "ParseResult"]
