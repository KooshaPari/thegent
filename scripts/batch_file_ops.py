#!/usr/bin/env python3
"""
Batch File Operations Helper

Reduces verbosity by batching multiple file operations into single calls.
"""

import json
from pathlib import Path


def batch_read_files(
    paths: list[str | Path],
    offsets: dict[str, int] | None = None,
    limits: dict[str, int] | None = None,
    base_path: str | Path | None = None,
) -> dict[str, str]:
    """
    Read multiple files efficiently.

    Args:
        paths: List of file paths (relative or absolute)
        offsets: Optional dict mapping path -> offset line number
        limits: Optional dict mapping path -> limit line count
        base_path: Optional base path for relative paths

    Returns:
        Dict mapping normalized path -> file content

    Example:
        >>> files = batch_read_files(
        ...     ["docs/file1.md", "docs/file2.md"],
        ...     offsets={"docs/file1.md": 10},
        ...     limits={"docs/file1.md": 50}
        ... )
    """
    offsets = offsets or {}
    limits = limits or {}
    base_path = Path(base_path) if base_path else Path.cwd()

    results = {}

    for path in paths:
        # Normalize path
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = base_path / path_obj

        normalized = str(path_obj.resolve())

        # Read file
        try:
            # dx-improve-file-reading-efficiency: Use offset/limit for targeted reading
            # If offset/limit specified, read only needed lines instead of entire file
            offset = offsets.get(normalized) or offsets.get(path, 0)
            limit = limits.get(normalized) or limits.get(path)

            if offset > 0 or limit:
                # Read only the needed lines (more efficient for large files)
                content_lines = []
                with path_obj.open(encoding="utf-8") as f:
                    # Skip lines before offset
                    for _ in range(max(0, offset - 1)):
                        try:
                            next(f)
                        except StopIteration:
                            break

                    # Read up to limit lines (or all remaining if no limit)
                    lines_read = 0
                    for line in f:
                        if limit and lines_read >= limit:
                            break
                        content_lines.append(line.rstrip("\n\r"))
                        lines_read += 1

                content = "\n".join(content_lines)
            else:
                # No offset/limit - read entire file
                content = path_obj.read_text(encoding="utf-8")

            results[normalized] = content
        except Exception as e:
            results[normalized] = f"ERROR: {e}"

    return results


def batch_grep_files(
    pattern: str, paths: list[str | Path], output_mode: str = "content", **grep_kwargs
) -> dict[str, list[str] | int]:
    """
    Batch grep across multiple files.

    Args:
        pattern: Regex pattern to search
        paths: List of file paths
        output_mode: "content", "files_with_matches", or "count"
        **grep_kwargs: Additional grep arguments

    Returns:
        Dict mapping path -> matches (or count)
    """
    # This would integrate with the grep tool
    # For now, return structure
    results = {}

    for path in paths:
        # Normalize path
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj

        normalized = str(path_obj.resolve())
        results[normalized] = []  # Would be populated by actual grep

    return results


def normalize_path(path: str | Path, base: str | Path | None = None) -> str:
    """
    Normalize path to absolute.

    Args:
        path: Path to normalize
        base: Base path for relative paths

    Returns:
        Absolute path as string
    """
    path_obj = Path(path)
    base_path = Path(base) if base else Path.cwd()

    if not path_obj.is_absolute():
        path_obj = base_path / path_obj

    return str(path_obj.resolve())


def batch_write_files(files: dict[str, str], base_path: str | Path | None = None) -> dict[str, bool]:
    """
    Write multiple files efficiently.

    Args:
        files: Dict mapping path -> content
        base_path: Optional base path for relative paths

    Returns:
        Dict mapping path -> success (True/False)
    """
    base_path = Path(base_path) if base_path else Path.cwd()
    results = {}

    for path, content in files.items():
        try:
            path_obj = Path(path)
            if not path_obj.is_absolute():
                path_obj = base_path / path_obj

            # Create parent directories
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            path_obj.write_text(content, encoding="utf-8")
            results[str(path_obj.resolve())] = True
        except Exception as e:
            results[str(path_obj.resolve())] = False

    return results


if __name__ == "__main__":
    # Example usage
    files = batch_read_files(
        ["docs/research/CROSS_PROJECT_WORK_STREAM_ANALYSIS.md"],
        offsets={"docs/research/CROSS_PROJECT_WORK_STREAM_ANALYSIS.md": 1},
        limits={"docs/research/CROSS_PROJECT_WORK_STREAM_ANALYSIS.md": 50},
    )
    print(json.dumps(list(files.keys()), indent=2))
