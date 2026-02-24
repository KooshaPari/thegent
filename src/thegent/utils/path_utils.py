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


<<<<<<< HEAD
=======
    Args:
        path: Path to check (``~`` expansion is applied).

    Returns:
        ``True`` if the path exists and is accessible; ``False`` otherwise.

    Examples:
        >>> safe_exists("/tmp")
        True

        >>> safe_exists("/nonexistent/path")
        False

        >>> safe_exists("/root/secret")   # PermissionError → False
        False
    """
    try:
        return Path(path).expanduser().exists()
    except (PermissionError, OSError, TypeError, ValueError):
        return False


def rel_to_cwd(path: str | Path) -> Path:
    """Return *path* relative to the current working directory when possible.

    If *path* is not under the CWD the resolved absolute path is returned
    unchanged.  Intended for human-readable display and logging — not for
    filesystem operations.

    Args:
        path: Path to make relative (``~`` expansion applied).

    Returns:
        Relative :class:`~pathlib.Path` when *path* is inside the CWD,
        otherwise the absolute :class:`~pathlib.Path`.

    Examples:
        >>> rel_to_cwd("/home/user/project/src/main.py")   # CWD=/home/user/project
        PosixPath('src/main.py')

        >>> rel_to_cwd("/etc/hosts")
        PosixPath('/etc/hosts')
    """
    resolved = _resolve(Path(path).expanduser())
    try:
        return resolved.relative_to(Path.cwd())
    except ValueError:
        return resolved


def ensure_dir(path: str | Path) -> Path:
    """Create *path* as a directory (including parents) if it does not exist.

    Equivalent to ``mkdir -p``.  Does nothing if the directory already exists.

    Args:
        path: Directory path to create (``~`` expansion applied).

    Returns:
        Resolved absolute :class:`~pathlib.Path` of the created/existing directory.

    Raises:
        NotADirectoryError: If *path* exists but is a file.
        PermissionError: If the directory cannot be created.

    Examples:
        >>> ensure_dir("/tmp/myapp/logs")
        PosixPath('/tmp/myapp/logs')
    """
    p = _resolve(Path(path).expanduser())
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Retained helpers from prior implementation
# ---------------------------------------------------------------------------


<<<<<<< HEAD
def path_to_str(path: str | Path | None) -> str:
    """Convert a path to a string, handling ``None`` gracefully.

    Args:
        path: Path object, string, or ``None``.

    Returns:
        String representation of *path*, or ``''`` for ``None``.
    """
    if path is None:
        return ""
    return str(path)


def get_common_ancestor(*paths: str | Path) -> Path:
    """Find the common ancestor directory of multiple paths.

    Args:
        *paths: Paths to find the common ancestor for.

    Returns:
        Common ancestor as a :class:`~pathlib.Path`, or the filesystem root
        if no common ancestor exists above the root.

    Examples:
        >>> get_common_ancestor("/home/user/a", "/home/user/b")
        PosixPath('/home/user')
    """
    if not paths:
        return Path.cwd()

    normalized = [normalize_path(p) for p in paths]
    all_parts = [p.parts for p in normalized]
    common: list[str] = []

    for i, part in enumerate(all_parts[0]):
        if all(i < len(pp) and pp[i] == part for pp in all_parts):
            common.append(part)
        else:
            break

    if not common:
        return Path(normalized[0].anchor or "/")

    return Path(*common)


def is_same_path(path1: str | Path, path2: str | Path) -> bool:
    """Return ``True`` if two paths refer to the same filesystem object.

    Uses :meth:`~pathlib.Path.samefile` when both paths exist (handles
    symlinks correctly) and falls back to resolved-path comparison otherwise.

    Args:
        path1: First path.
        path2: Second path.

    Returns:
        ``True`` if paths refer to the same object.
    """
    try:
        return normalize_path(path1).samefile(normalize_path(path2))
    except (OSError, ValueError):
        return normalize_path(path1) == normalize_path(path2)


def is_absolute_or_relative(path: str | Path) -> bool:
    """Return ``True`` if *path* is absolute, ``False`` if relative.

    Note: ``~`` paths are treated as relative until expanded.

    Args:
        path: Path to inspect.

    Returns:
        ``True`` if the path is absolute.

    Examples:
        >>> is_absolute_or_relative("/home/user")
        True

        >>> is_absolute_or_relative("~/projects")
        False

        >>> is_absolute_or_relative("./src")
        False
    """
    p = Path(path) if isinstance(path, str) else path
    return p.is_absolute()


def sanitize_path(name: str) -> str:
    """Replace characters illegal in file system paths with underscores.

    Replaces the characters ``:<>"/\\|?*`` with ``_``.

    Args:
        name: Filename or path component to sanitize.

    Returns:
        Sanitized string safe for use as a path component.

    Examples:
        >>> sanitize_path('file:with*illegal?chars.txt')
        'file_with_illegal_chars.txt'
    """
    return re.sub(r'[:<>"/\\|?*]', "_", name)


def strip_common_prefix(paths: list[str | Path]) -> list[str]:
    """Strip the common directory prefix from a list of paths for display.

    Args:
        paths: Paths to strip common prefix from.

    Returns:
        List of paths with common prefix removed, as strings.

    Examples:
        >>> strip_common_prefix(["/a/b/file1.txt", "/a/b/file2.txt"])
        ['file1.txt', 'file2.txt']
    """
    if not paths:
        return []

    normalized = [normalize_path(p) for p in paths]
    common = get_common_ancestor(*normalized)
    result = []
    for p in normalized:
        if is_within(p, common):
            result.append(str(p.relative_to(common)))
        else:
            result.append(str(p))
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve(path: Path) -> Path:
    """Resolve a path, falling back gracefully when it does not exist.

    On Python 3.6+, ``Path.resolve()`` resolves symlinks and ``..``
    components but does NOT require the path to exist (``strict=False``
    is the default since 3.6).  We make that explicit here.
    """
    return path.resolve()


# ---------------------------------------------------------------------------
# CLI self-test / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    cwd = Path.cwd()
    sandbox_base = Path(tempfile.gettempdir()) / "sandbox"

    with contextlib.suppress(ValueError):
        safe_join(sandbox_base, "../../etc/passwd")

    safe = safe_join(sandbox_base, "sub/file.txt")

    with tempfile.TemporaryDirectory() as td:
        created = ensure_dir(Path(td) / "a" / "b" / "c")

    sys.exit(0)
=======
>>>>>>> origin/fix/cli-test-failures
def format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"


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
<<<<<<< HEAD


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
=======
>>>>>>> origin/main
>>>>>>> origin/fix/cli-test-failures
