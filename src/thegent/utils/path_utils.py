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
<<<<<<< HEAD
=======


def normalize_path(path: Path | str | None) -> Path | None:
    """Normalize a path - expand user, resolve, and make absolute."""
    if path is None:
        return None
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve()


def path_to_str(path: Path | None) -> str | None:
    """Convert Path to string representation."""
    if path is None:
        return None
    return str(path)


def get_common_ancestor(paths: list[Path]) -> Path | None:
    """Get the common ancestor of multiple paths."""
    if not paths:
        return None
    if len(paths) == 1:
        return paths[0].parent
    # Find common ancestor by checking each path's parents
    first = paths[0]
    for parent in [first] + list(first.parents):
        if all(p.is_relative_to(parent) or parent in p.parents for p in paths):
            return parent
    return Path("/")


def is_same_path(path1: Path, path2: Path) -> bool:
    """Check if two paths resolve to the same location."""
    try:
        return path1.resolve() == path2.resolve()
    except Exception:
        return path1 == path2


def is_within(path: Path, parent: Path) -> bool:
    """Check if path is within parent directory."""
    try:
        return path.is_relative_to(parent)
    except Exception:
        return parent in path.parents


def rel_to_cwd(path: Path) -> Path:
    """Get path relative to current working directory."""
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path


def safe_exists(path: Path) -> bool:
    """Check if path exists, handling race conditions."""
    try:
        return path.exists()
    except Exception:
        return False


def safe_is_file(path: Path) -> bool:
    """Check if path is a file, handling race conditions."""
    try:
        return path.is_file()
    except Exception:
        return False


def safe_is_dir(path: Path) -> bool:
    """Check if path is a directory, handling race conditions."""
    try:
        return path.is_dir()
    except Exception:
        return False


def safe_join(base: Path, *parts: str) -> Path | None:
    """Safely join path parts, ensuring result is within base."""
    try:
        result = base.joinpath(*parts).resolve()
        base_resolved = base.resolve()
        # Security: ensure result is within base
        if not str(result).startswith(str(base_resolved)):
            return None
        return result
    except Exception:
        return None


def sanitize_path(path: str) -> str:
    """Remove dangerous characters from path component."""
    # Remove null bytes and path traversal attempts
    import re
    return re.sub(r'[\x00..\x1f]', '', path)
>>>>>>> fix/additional-improvements
