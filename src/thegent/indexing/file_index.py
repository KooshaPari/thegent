"""File indexing (fd-style) for fast find patterns.

Provides a TTL-based in-memory file index built with os.scandir for
performance. Avoids repeated filesystem traversals for common find patterns.

Design reference: docs/research/CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md §3.1
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from cachetools import TTLCache

# Default TTL in seconds (override via THGENT_FILE_INDEX_TTL env var)
_DEFAULT_TTL: int = 30

_DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {".git", "__pycache__", ".venv", "node_modules", ".mypy_cache", "dist", "build"}
)


def _get_ttl() -> int:
    """Read TTL from settings."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.file_index_ttl


class FileIndex:
    """In-memory file index with TTL-based invalidation.

    Builds the index once using ``os.scandir`` (faster than ``os.walk``),
    then serves queries from memory until the TTL expires.

    Usage::

        idx = FileIndex()
        idx.build(Path("/my/project"))
        py_files = idx.find_by_ext(".py")
        configs  = idx.find_by_name("pyproject.toml")
        srcs     = idx.find("src/**/*.py")
    """

    def __init__(self, ttl: int | None = None) -> None:
        self._ttl: int = ttl if ttl is not None else _get_ttl()
        # TTLCache keyed by root path str -> list[Path]
        self._cache: TTLCache[str, list[Path]] = TTLCache(maxsize=32, ttl=self._ttl)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        root: Path,
        exclude_dirs: set[str] | frozenset[str] = _DEFAULT_EXCLUDE_DIRS,
        *,
        force: bool = False,
    ) -> list[Path]:
        """Scan *root* recursively and cache the result.

        Args:
            root: Directory to index.
            exclude_dirs: Directory names to skip during traversal.
            force: Rebuild even if a valid cached index exists.

        Returns:
            List of all non-excluded file paths found under *root*.
        """
        key = str(root.resolve())
        if not force and key in self._cache:
            return self._cache[key]

        paths: list[Path] = []
        self._scandir(root.resolve(), frozenset(exclude_dirs), paths)
        self._cache[key] = paths
        return paths

    def find(self, pattern: str, root: Path | None = None) -> list[Path]:
        """Return paths matching a glob *pattern* (e.g. ``src/**/*.py``).

        The index for *root* must already be built (or will be built on demand).
        """
        index = self._get_or_build(root)
        return [p for p in index if fnmatch.fnmatch(str(p), pattern)]

    def find_by_name(self, name: str, root: Path | None = None) -> list[Path]:
        """Return paths whose filename (last component) equals *name*."""
        index = self._get_or_build(root)
        return [p for p in index if p.name == name]

    def find_by_ext(self, ext: str, root: Path | None = None) -> list[Path]:
        """Return paths with the given extension (e.g. ``".py"``).

        The leading dot is optional: ``"py"`` and ``".py"`` both work.
        """
        normalised = ext if ext.startswith(".") else f".{ext}"
        index = self._get_or_build(root)
        return [p for p in index if p.suffix == normalised]

    def invalidate(self, root: Path | None = None) -> None:
        """Manually expire the cache for *root* (or all roots if None)."""
        if root is None:
            self._cache.clear()
        else:
            self._cache.pop(str(root.resolve()), None)

    def is_cached(self, root: Path) -> bool:
        """Return True if a valid (non-expired) index exists for *root*."""
        return str(root.resolve()) in self._cache

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_build(self, root: Path | None) -> list[Path]:
        """Return index for *root*, building it on demand if absent."""
        if root is None:
            root = Path.cwd()
        return self.build(root)

    def _scandir(
        self,
        directory: Path,
        exclude_dirs: frozenset[str],
        out: list[Path],
    ) -> None:
        """Recursive scandir traversal (faster than os.walk)."""
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name not in exclude_dirs:
                            self._scandir(Path(entry.path), exclude_dirs, out)
                    else:
                        out.append(Path(entry.path))
        except PermissionError:
            pass  # Skip directories we cannot read
