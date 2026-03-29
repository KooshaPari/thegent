"""Batch file operations: read, write, delete.

Thin wrappers over pathlib for batched multi-file operations.
Delegates to pathlib.Path directly for maximum simplicity.

# @trace FR-DX-001
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def batch_read(paths: list[Path]) -> dict[Path, str]:
    """Read multiple files and return a mapping of path to content.

    Args:
        paths: List of file paths to read.

    Returns:
        Dict mapping each path to its text content.

    Raises:
        FileNotFoundError: If any path does not exist.
    """
    return {p: p.read_text() for p in paths}


def batch_write(pairs: list[tuple[Path, str]]) -> None:
    """Write multiple files from a list of (path, content) pairs.

    Creates parent directories as needed.

    Args:
        pairs: List of (path, content) tuples.
    """
    for path, content in pairs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def batch_delete(paths: list[Path]) -> None:
    """Delete multiple files.

    Args:
        paths: List of file paths to delete.

    Raises:
        FileNotFoundError: If any path does not exist.
    """
    for p in paths:
        p.unlink()
