"""BKM-10: JSONL operations using native Rust (thegent-jsonl).

Streams JSON objects from JSONL (newline-delimited JSON) files without loading
entire files into memory. Uses the thegent-jsonl PyO3 extension.

Requires thegent-jsonl to be installed.

FR-JSONL-001  @trace FR-JSONL-001
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

_log = logging.getLogger(__name__)

# Native Rust extension (required)
try:
    import thegent_jsonl  # type: ignore[reportMissingImports]
except ImportError:
    raise ImportError("thegent-jsonl not available - install with: pip install thegent-jsonl")


class JsonlParser:
    """Native JSONL parser using Rust."""

    @staticmethod
    def stream(path: Path) -> Iterator[dict[str, Any]]:
        """Stream records from a JSONL file.
        
        Args:
            path: Path to JSONL file
            
        Yields:
            Parsed JSON objects
        """
        result = thegent_jsonl.parse_file(str(path))
        if result.is_err():
            raise OSError(f"Failed to parse {path}: {result.err()}")

        iter = result.unwrap()
        while True:
            item = iter.__next__()
            if item.is_err():
                _log.debug("parse error: %s", item.err())
                continue
            yield item.unwrap()

    @staticmethod
    def count(path: Path) -> int:
        """Count non-blank lines in a JSONL file.
        
        Args:
            path: Path to JSONL file
            
        Returns:
            Number of records
        """
        result = thegent_jsonl.count_file(str(path))
        if result.is_err():
            raise OSError(f"Failed to count {path}: {result.err()}")
        return result.unwrap()

    @staticmethod
    def filter(path: Path, key: str, value: str) -> Iterator[dict[str, Any]]:
        """Filter records by key=value.
        
        Args:
            path: Path to JSONL file
            key: JSON field to filter on
            value: Value to match
            
        Yields:
            Matching JSON objects
        """
        result = thegent_jsonl.filter_file(str(path), key, value)
        if result.is_err():
            raise OSError(f"Failed to filter {path}: {result.err()}")

        iter = result.unwrap()
        while True:
            item = iter.__next__()
            if item.is_err():
                continue
            yield item.unwrap()

    @staticmethod
    def sample(path: Path, n: int) -> list[dict[str, Any]]:
        """Get first N records from a JSONL file.
        
        Args:
            path: Path to JSONL file
            n: Number of records to get
            
        Returns:
            List of JSON objects
        """
        result = thegent_jsonl.sample_file(str(path), n)
        if result.is_err():
            raise OSError(f"Failed to sample {path}: {result.err()}")

        items = result.unwrap()
        return [i for i in items if i.is_ok()]
