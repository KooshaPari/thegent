"""Common path utilities for thegent.

Provides consistent path handling across the codebase.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_parent_dir(path: Path) -> Path:
    """Ensure parent directory of a file exists."""
    if path.parent != path:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def expand_path(path: str | Path) -> Path:
    """Expand user home and environment variables in path."""
    return Path(os.path.expanduser(os.path.expandvars(path)))


def resolve_path(path: str | Path, base: Path | None = None) -> Path:
    """Resolve a path relative to base, or cwd if not provided."""
    path = expand_path(path)
    if path.is_absolute():
        return path.resolve()
    if base is None:
        base = Path.cwd()
    return (base / path).resolve()


def is_subpath(path: Path, parent: Path) -> bool:
    """Check if path is a subpath of parent."""
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def find_files(
    directory: Path,
    pattern: str = "*",
    recursive: bool = True,
) -> list[Path]:
    """Find files matching pattern in directory."""
    if recursive:
        return list(directory.rglob(pattern))
    return list(directory.glob(pattern))


def find_dirs(
    directory: Path,
    pattern: str = "*",
    recursive: bool = True,
) -> list[Path]:
    """Find directories matching pattern in directory."""
    if recursive:
        return [p for p in directory.rglob(pattern) if p.is_dir()]
    return [p for p in directory.glob(pattern) if p.is_dir()]


def get_project_root() -> Path:
    """Find project root by looking for common markers."""
    markers = ["pyproject.toml", "setup.py", "setup.cfg", "package.json"]
    current = Path.cwd()
    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent
    return Path.cwd()


def get_size(path: Path) -> int:
    """Get size of file or directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
    return total


def format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"


def normalize_path(path: str | Path | None = None) -> Path:
    """Normalize a path to an absolute Path, defaulting to cwd."""
    if path is None:
        return Path.cwd()
    return resolve_path(path)


def path_to_str(path: str | Path | None) -> str:
    """Convert a path to a string."""
    if path is None:
        return ""
    return str(Path(path))


def get_common_ancestor(paths: list[Path]) -> Path:
    """Get the common ancestor of a list of paths."""
    if not paths:
        return Path.cwd()
    resolved = [p.resolve() for p in paths]
    common = resolved[0]
    for p in resolved[1:]:
        parts_a = common.parts
        parts_b = p.parts
        common_parts = []
        for a, b in zip(parts_a, parts_b):
            if a == b:
                common_parts.append(a)
            else:
                break
        common = Path(*common_parts) if common_parts else Path("/")
    return common


def is_same_path(a: Path, b: Path) -> bool:
    """Check if two paths refer to the same file/directory."""
    return a.resolve() == b.resolve()


def is_within(path: Path, parent: Path) -> bool:
    """Alias for is_subpath."""
    return is_subpath(path, parent)


def rel_to_cwd(path: Path) -> Path:
    """Make path relative to current working directory."""
    try:
        return path.resolve().relative_to(Path.cwd())
    except ValueError:
        return path.resolve()


def safe_exists(path: str | Path | None) -> bool:
    """Check if path exists, returning False for None or invalid paths."""
    if path is None:
        return False
    try:
        return Path(path).exists()
    except (OSError, ValueError):
        return False


def safe_join(base: Path, *parts: str | Path) -> Path:
    """Join path parts safely."""
    result = base
    for part in parts:
        result = result / part
    return result


def sanitize_path(path: str | Path) -> Path:
    """Sanitize a path by resolving it and removing dangerous components."""
    return Path(path).resolve()
