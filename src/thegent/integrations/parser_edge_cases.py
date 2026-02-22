"""Parser/Reflection Edge-Case Unit Tests (WL-177): Robust parser testing utilities.

@trace WL-177

Provides edge-case testing utilities for markdown/JSON parser validation,
including handling of malformed input, status reflection, and boundary conditions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class ParseResult:
    """Result of parsing an input string.

    Attributes:
        raw: The raw input string that was parsed.
        parsed: The parsed result (dict, None if parsing failed).
        error: Optional error message if parsing failed.
    """

    raw: str
    parsed: dict[str, Any] | None
    error: str | None = None


class EdgeCaseParser:
    """Parser for edge cases and malformed input.

    Provides methods to parse JSON strings with graceful error handling,
    useful for testing parser robustness against malformed markdown blocks
    and status reflection edge cases.

    Example:
        >>> parser = EdgeCaseParser()
        >>> result = parser.parse('{"key": "value"}')
        >>> if result.parsed:
        ...     print("Success:", result.parsed)
        ... else:
        ...     print("Error:", result.error)
    """

    def parse(self, raw: str) -> ParseResult:
        """Parse a raw string as JSON.

        Args:
            raw: The raw string to parse.

        Returns:
            ParseResult with parsed dict or None, and error if failed.
        """
        try:
            parsed = json.loads(raw)
            return ParseResult(raw=raw, parsed=parsed, error=None)
        except json.JSONDecodeError as e:
            return ParseResult(raw=raw, parsed=None, error=str(e))
        except Exception as e:
            return ParseResult(raw=raw, parsed=None, error=str(e))

    def parse_many(self, items: list[str]) -> list[ParseResult]:
        """Parse multiple strings.

        Args:
            items: List of raw strings to parse.

        Returns:
            List of ParseResult objects.
        """
        return [self.parse(item) for item in items]

    @staticmethod
    def failures(results: list[ParseResult]) -> list[ParseResult]:
        """Filter for failed parse results.

        Args:
            results: List of ParseResult objects.

        Returns:
            List of ParseResult objects where parsed is None.
        """
        return [r for r in results if r.parsed is None]
