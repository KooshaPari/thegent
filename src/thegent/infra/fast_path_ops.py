"""Fast path operations with optimizations.

This module provides optimized path operations:
- Direct os.path operations for hot paths
- Optimized path joining and normalization
- Fast path existence checks

Performance improvements:
- Direct os.path: Faster than pathlib for simple operations
- Optimized for common path operations
"""

import os
from pathlib import Path


class FastPathOps:
    """High-performance path operations with optimizations."""

    @staticmethod
    def join(*parts: str) -> str:
        """Join path parts efficiently.

        Args:
            *parts: Path components

        Returns:
            Joined path string

        Performance:
            - os.path.join: Faster than Path() for simple joins
            - Optimized for common cases
        """
        return os.path.join(*parts)

    @staticmethod
    def exists(path: str | Path) -> bool:
        """Check if path exists efficiently.

        Args:
            path: Path to check

        Returns:
            True if path exists

        Performance:
            - os.path.exists: Fast existence check
            - Avoids Path overhead for simple checks
        """
        return os.path.exists(str(path))

    @staticmethod
    def is_file(path: str | Path) -> bool:
        """Check if path is a file efficiently.

        Args:
            path: Path to check

        Returns:
            True if path is a file
        """
        return os.path.isfile(str(path))

    @staticmethod
    def is_dir(path: str | Path) -> bool:
        """Check if path is a directory efficiently.

        Args:
            path: Path to check

        Returns:
            True if path is a directory
        """
        return os.path.isdir(str(path))

    @staticmethod
    def normalize(path: str) -> str:
        """Normalize path efficiently.

        Args:
            path: Path to normalize

        Returns:
            Normalized path

        Performance:
            - os.path.normpath: Fast normalization
            - Handles .. and . correctly
        """
        return os.path.normpath(path)

    @staticmethod
    def abspath(path: str) -> str:
        """Get absolute path efficiently.

        Args:
            path: Path to resolve

        Returns:
            Absolute path
        """
        return os.path.abspath(path)

    @staticmethod
    def basename(path: str | Path) -> str:
        """Get basename efficiently.

        Args:
            path: Path

        Returns:
            Basename (filename)
        """
        return os.path.basename(str(path))

    @staticmethod
    def dirname(path: str | Path) -> str:
        """Get directory name efficiently.

        Args:
            path: Path

        Returns:
            Directory name
        """
        return os.path.dirname(str(path))

    @staticmethod
    def split(path: str | Path) -> tuple[str, str]:
        """Split path into directory and filename efficiently.

        Args:
            path: Path to split

        Returns:
            Tuple of (directory, filename)
        """
        return os.path.split(str(path))

    @staticmethod
    def splitext(path: str | Path) -> tuple[str, str]:
        """Split path into base and extension efficiently.

        Args:
            path: Path to split

        Returns:
            Tuple of (base, extension)
        """
        return os.path.splitext(str(path))


# Convenience functions
def path_join(*parts: str) -> str:
    """Join path parts efficiently."""
    return FastPathOps.join(*parts)


def path_exists(path: str | Path) -> bool:
    """Check if path exists efficiently."""
    return FastPathOps.exists(path)


def path_is_file(path: str | Path) -> bool:
    """Check if path is a file efficiently."""
    return FastPathOps.is_file(path)


def path_is_dir(path: str | Path) -> bool:
    """Check if path is a directory efficiently."""
    return FastPathOps.is_dir(path)


def path_normalize(path: str) -> str:
    """Normalize path efficiently."""
    return FastPathOps.normalize(path)
