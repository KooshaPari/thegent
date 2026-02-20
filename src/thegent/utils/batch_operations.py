"""Batch file operations to reduce tool calls."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def batch_file_operations(
    files: list[Path],
    operation: Callable[[Path], Any],
    batch_size: int = 10,
) -> list[Any]:
    """Perform batch file operations.

    Args:
        files: List of file paths
        operation: Operation function to apply to each file
        batch_size: Number of files to process per batch

    Returns:
        List of operation results
    """
    results = []

    for i in range(0, len(files), batch_size):
        batch = files[i : i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} files)")

        def _process_file(file_path: Path) -> Any:
            """Process a single file, returning result or None on error."""
            try:
                return operation(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                return None

        for file_path in batch:
            result = _process_file(file_path)
            results.append(result)

    return results


def batch_read_files(files: list[Path], batch_size: int = 10) -> dict[Path, str]:
    """Batch read multiple files.

    Args:
        files: List of file paths
        batch_size: Number of files to read per batch

    Returns:
        Dictionary mapping paths to file contents
    """

    def read_file(file_path: Path) -> tuple[Path, str]:
        return file_path, file_path.read_text()

    results = batch_file_operations(files, read_file, batch_size)
    return {path: content for path, content in results if path is not None}


def batch_write_files(file_contents: dict[Path, str], batch_size: int = 10) -> None:
    """Batch write multiple files.

    Args:
        file_contents: Dictionary mapping paths to file contents
        batch_size: Number of files to write per batch
    """

    def write_file(item: tuple[Path, str]) -> None:
        path, content = item
        path.write_text(content)

    items = list(file_contents.items())
    batch_file_operations(
        [item[0] for item in items],
        lambda p: write_file(next((i for i in items if i[0] == p), None)),
        batch_size,
    )
