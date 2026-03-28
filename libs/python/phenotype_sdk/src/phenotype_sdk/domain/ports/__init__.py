"""Domain ports - Interfaces defining boundaries of the domain."""

from abc import ABC, abstractmethod
from typing import AsyncIterator
from uuid import UUID

from phenotype_sdk.domain.entities import ConfigEntry, FeatureFlag


class ConfigRepository(ABC):
    """
    Port interface for configuration persistence.

    Implemented by adapters (Hexagonal Architecture: Driven/Secondary Port).
    This interface is defined by the domain, not the infrastructure.
    """

    @abstractmethod
    async def get(self, key: str) -> ConfigEntry | None:
        """Retrieve a configuration entry by key."""
        ...

    @abstractmethod
    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """Persist a configuration entry."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a configuration entry."""
        ...

    @abstractmethod
    async def list(self, prefix: str | None = None) -> AsyncIterator[ConfigEntry]:
        """List all configuration entries, optionally filtered by prefix."""
        ...


class ConfigEventPublisher(ABC):
    """
    Port interface for publishing configuration change events.

    Supports Event-Driven Architecture patterns.
    """

    @abstractmethod
    async def publish_config_created(self, entry: ConfigEntry) -> None:
        """Publish event when a config entry is created."""
        ...

    @abstractmethod
    async def publish_config_updated(self, entry: ConfigEntry, previous: ConfigEntry) -> None:
        """Publish event when a config entry is updated."""
        ...

    @abstractmethod
    async def publish_config_deleted(self, key: str) -> None:
        """Publish event when a config entry is deleted."""
        ...


class FeatureRepository(ABC):
    """
    Port interface for feature flag persistence.

    Separates domain from storage implementation details.
    """

    @abstractmethod
    async def get(self, key: str) -> FeatureFlag | None:
        """Retrieve a feature flag by key."""
        ...

    @abstractmethod
    async def save(self, flag: FeatureFlag) -> FeatureFlag:
        """Persist a feature flag."""
        ...

    @abstractmethod
    async def list(self) -> AsyncIterator[FeatureFlag]:
        """List all feature flags."""
        ...


class FeatureEvaluator(ABC):
    """
    Port interface for feature evaluation.

    Allows swapping evaluation strategies (e.g., local, remote, hybrid).
    """

    @abstractmethod
    async def is_enabled(
        self, flag_key: str, user_id: str, attributes: dict[str, Any] | None = None
    ) -> bool:
        """Check if a feature is enabled for a user."""
        ...

    @abstractmethod
    async def get_variant(
        self, flag_key: str, user_id: str, attributes: dict[str, Any] | None = None
    ) -> str | None:
        """Get the variant value for a multivariate feature."""
        ...
