"""In-memory adapter for testing and local development."""

from typing import Any, AsyncIterator

from phenotype_sdk.domain.entities import ConfigEntry, FeatureFlag
from phenotype_sdk.domain.ports import ConfigRepository, FeatureRepository
from phenotype_sdk.domain.value_objects import ConfigValue


class InMemoryConfigRepository(ConfigRepository):
    """
    In-memory implementation of ConfigRepository.

    Useful for testing and local development (Hexagonal: Driven Adapter).
    """

    def __init__(self) -> None:
        self._entries: dict[str, ConfigEntry] = {}

    async def get(self, key: str) -> ConfigEntry | None:
        """Get a configuration entry by key."""
        return self._entries.get(key)

    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """Save a configuration entry."""
        self._entries[entry.key] = entry
        return entry

    async def delete(self, key: str) -> bool:
        """Delete a configuration entry."""
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    async def list(self, prefix: str | None = None) -> AsyncIterator[ConfigEntry]:
        """List all configuration entries."""
        for entry in self._entries.values():
            if prefix is None or entry.key.startswith(prefix):
                yield entry

    def clear(self) -> None:
        """Clear all entries (useful for testing)."""
        self._entries.clear()


class InMemoryFeatureRepository(FeatureRepository):
    """
    In-memory implementation of FeatureRepository.

    Useful for testing and local development.
    """

    def __init__(self) -> None:
        self._flags: dict[str, FeatureFlag] = {}

    async def get(self, key: str) -> FeatureFlag | None:
        """Get a feature flag by key."""
        return self._flags.get(key)

    async def save(self, flag: FeatureFlag) -> FeatureFlag:
        """Save a feature flag."""
        self._flags[flag.key] = flag
        return flag

    async def list(self) -> AsyncIterator[FeatureFlag]:
        """List all feature flags."""
        for flag in self._flags.values():
            yield flag

    def clear(self) -> None:
        """Clear all flags (useful for testing)."""
        self._flags.clear()
