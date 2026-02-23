"""Versioned mapping registry for managing evolving mappings.

Maintains historical versions of mappings with automatic versioning and
lookup capabilities across versions.

FR traceability: WL-311 (Versioned Mapping Registry)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class MappingVersion:
    """A versioned snapshot of mappings.

    Attributes:
        version: The version number (auto-incremented from 1).
        mappings: Dictionary of key-to-value mappings.
        created_at: Timestamp when this version was created.
        label: Optional descriptive label for this version.
    """

    version: int
    mappings: dict[str, str]
    created_at: datetime
    label: str = ""


class VersionedMappingRegistry:
    """Registry for managing versioned mappings.

    Maintains multiple versions of mappings and provides lookup across versions.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._versions: dict[int, MappingVersion] = {}
        self._next_version: int = 1

    def register(self, mappings: dict[str, str], label: str = "") -> MappingVersion:
        """Register a new version of mappings.

        Creates a new version with auto-incremented version number and current timestamp.

        Args:
            mappings: Dictionary of key-to-value mappings to register.
            label: Optional descriptive label for this version.

        Returns:
            The created MappingVersion.
        """
        version = self._next_version
        mapping_version = MappingVersion(
            version=version,
            mappings=mappings.copy(),
            created_at=datetime.now(timezone.utc),
            label=label,
        )
        self._versions[version] = mapping_version
        self._next_version += 1
        return mapping_version

    def get_version(self, version: int) -> MappingVersion:
        """Get a specific version of mappings.

        Args:
            version: The version number to retrieve.

        Returns:
            The MappingVersion.

        Raises:
            KeyError: If the version does not exist.
        """
        if version not in self._versions:
            raise KeyError(f"Version {version} not found")
        return self._versions[version]

    def latest(self) -> MappingVersion:
        """Get the latest version of mappings.

        Returns:
            The most recently registered MappingVersion.

        Raises:
            ValueError: If no versions have been registered.
        """
        if not self._versions:
            raise ValueError("No versions registered")
        return self._versions[self._next_version - 1]

    def list_versions(self) -> list[int]:
        """List all registered version numbers.

        Returns:
            Sorted list of version numbers in ascending order.
        """
        return sorted(self._versions.keys())

    def resolve(self, key: str, version: int | None = None) -> str:
        """Look up a key in a specific version or the latest version.

        Args:
            key: The mapping key to look up.
            version: The version number to use, or None to use latest.

        Returns:
            The mapped value.

        Raises:
            KeyError: If the version or key is not found.
            ValueError: If version is None and no versions are registered.
        """
        if version is None:
            mapping_version = self.latest()
        else:
            mapping_version = self.get_version(version)

        if key not in mapping_version.mappings:
            raise KeyError(f"Key '{key}' not found in version {mapping_version.version}")

        return mapping_version.mappings[key]
