"""Data Transfer Objects - Immutable representations for API boundaries."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from phenotype_sdk.domain.value_objects import ValueType


@dataclass(frozen=True)
class ConfigEntryDTO:
    """DTO for transferring configuration entry data."""

    id: str
    key: str
    value: Any
    value_type: ValueType
    version: int
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_entity(cls, entity: "phenotype_sdk.domain.entities.ConfigEntry") -> "ConfigEntryDTO":
        """Convert domain entity to DTO."""
        from phenotype_sdk import domain as domain_module
        return cls(
            id=str(entity.id),
            key=entity.key,
            value=entity.value.raw,
            value_type=entity.value.value_type,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            metadata=entity.metadata,
        )


@dataclass(frozen=True)
class CreateConfigDTO:
    """DTO for creating a new configuration entry."""

    key: str
    value: Any
    value_type: ValueType
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateConfigDTO:
    """DTO for updating a configuration entry."""

    key: str
    value: Any


@dataclass(frozen=True)
class FeatureFlagDTO:
    """DTO for transferring feature flag data."""

    id: str
    key: str
    enabled: bool
    rollout_percentage: float
    targeting_rules: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: "phenotype_sdk.domain.entities.FeatureFlag") -> "FeatureFlagDTO":
        """Convert domain entity to DTO."""
        return cls(
            id=str(entity.id),
            key=entity.key,
            enabled=entity.enabled,
            rollout_percentage=entity.rollout_percentage,
            targeting_rules=entity.targeting_rules,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
