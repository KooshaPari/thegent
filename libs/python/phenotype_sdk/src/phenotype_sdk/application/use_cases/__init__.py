"""Application use cases - Orchestrate domain objects and ports."""

from typing import Any, AsyncIterator

from phenotype_sdk.domain.entities import ConfigEntry, FeatureFlag
from phenotype_sdk.domain.ports import ConfigRepository, FeatureRepository, ConfigEventPublisher
from phenotype_sdk.domain.value_objects import ConfigValue, ValueType
from phenotype_sdk.application.dto import ConfigEntryDTO, CreateConfigDTO, UpdateConfigDTO


class ConfigUseCases:
    """
    Application service for configuration management.

    Orchestrates domain entities and ports (Application Service pattern).
    Handles cross-cutting concerns like validation and event publishing.
    """

    def __init__(
        self,
        repository: ConfigRepository,
        event_publisher: ConfigEventPublisher | None = None,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    async def create_config(self, dto: CreateConfigDTO) -> ConfigEntry:
        """
        Create a new configuration entry.

        TDD: Write test first, then implementation.
        """
        # Check for existing entry
        existing = await self._repository.get(dto.key)
        if existing is not None:
            raise ValueError(f"Config entry already exists: {dto.key}")

        # Create domain entity
        config_value = ConfigValue.from_primitive(dto.value, dto.value_type)
        entry = ConfigEntry(key=dto.key, value=config_value, metadata=dto.metadata or {})

        # Persist
        saved = await self._repository.save(entry)

        # Publish event (CQRS: separate read/write models)
        if self._event_publisher is not None:
            await self._event_publisher.publish_config_created(saved)

        return saved

    async def update_config(self, dto: UpdateConfigDTO) -> ConfigEntry:
        """Update an existing configuration entry."""
        existing = await self._repository.get(dto.key)
        if existing is None:
            raise ValueError(f"Config entry not found: {dto.key}")

        # Create new value
        config_value = ConfigValue.from_primitive(dto.value, existing.value.value_type)
        updated = existing.with_updated_value(config_value)

        # Persist
        saved = await self._repository.save(updated)

        # Publish event
        if self._event_publisher is not None:
            await self._event_publisher.publish_config_updated(saved, existing)

        return saved

    async def get_config(self, key: str) -> ConfigEntry:
        """Retrieve a configuration entry."""
        entry = await self._repository.get(key)
        if entry is None:
            raise KeyError(f"Config entry not found: {key}")
        return entry

    async def delete_config(self, key: str) -> bool:
        """Delete a configuration entry."""
        deleted = await self._repository.delete(key)

        if deleted and self._event_publisher is not None:
            await self._event_publisher.publish_config_deleted(key)

        return deleted

    async def list_configs(self, prefix: str | None = None) -> AsyncIterator[ConfigEntry]:
        """List all configuration entries."""
        async for entry in self._repository.list(prefix):
            yield entry


class FeatureUseCases:
    """Application service for feature flag management."""

    def __init__(self, repository: FeatureRepository) -> None:
        self._repository = repository

    async def create_flag(self, key: str, enabled: bool, rollout_percentage: float = 100.0) -> FeatureFlag:
        """Create a new feature flag."""
        flag = FeatureFlag(key=key, enabled=enabled, rollout_percentage=rollout_percentage)
        return await self._repository.save(flag)

    async def get_flag(self, key: str) -> FeatureFlag:
        """Retrieve a feature flag."""
        flag = await self._repository.get(key)
        if flag is None:
            raise KeyError(f"Feature flag not found: {key}")
        return flag

    async def evaluate_flag(
        self, key: str, user_id: str, attributes: dict[str, Any] | None = None
    ) -> bool:
        """Evaluate if a feature is enabled for a user."""
        flag = await self.get_flag(key)
        return flag.is_enabled_for_user(user_id, attributes or {})

    async def list_flags(self) -> AsyncIterator[FeatureFlag]:
        """List all feature flags."""
        async for flag in self._repository.list():
            yield flag
