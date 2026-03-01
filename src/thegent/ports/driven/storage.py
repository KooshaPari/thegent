"""StoragePort: Interface for file/database persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class StoragePort(Protocol):
    """Port interface for persisting and retrieving provider/model data."""

    def load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON data from file.

        Args:
            path: Path to JSON file.

        Returns:
            Parsed JSON data as dict. Returns empty dict if file doesn't exist.
        """
        ...

    def save_json(self, path: Path, data: dict[str, Any]) -> None:
        """Save data as JSON.

        Args:
            path: Path to JSON file.
            data: Data to save.
        """
        ...

    def load_yaml(self, path: Path) -> dict[str, Any]:
        """Load YAML configuration file.

        Args:
            path: Path to YAML file.

        Returns:
            Parsed YAML data as dict. Returns empty dict if file doesn't exist.
        """
        ...

    def save_yaml(self, path: Path, data: dict[str, Any]) -> None:
        """Save data as YAML.

        Args:
            path: Path to YAML file.
            data: Data to save.
        """
        ...

    def file_exists(self, path: Path) -> bool:
        """Check if a file exists.

        Args:
            path: Path to check.

        Returns:
            True if file exists, False otherwise.
        """
        ...

    def create_directory(self, path: Path) -> None:
        """Create a directory and all parents.

        Args:
            path: Directory path to create.
        """
        ...


__all__ = [
    "StoragePort",
]
