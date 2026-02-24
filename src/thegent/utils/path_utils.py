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
