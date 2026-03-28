"""Core domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from phenotype_sdk.domain.value_objects import ValueType, ConfigValue


@dataclass(frozen=True)
class ConfigEntry:
    """
    Core domain entity representing a configuration entry.

    This entity is immutable and contains only business logic.
    Validation is performed at construction time (Domain-Driven Design).
    """

    key: str
    value: ConfigValue
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Validate entity invariants."""
        if not self.key:
            raise ValueError("ConfigEntry key cannot be empty")
        if not isinstance(self.key, str):
            raise TypeError("ConfigEntry key must be a string")
        if self.version < 1:
            raise ValueError("ConfigEntry version must be >= 1")

    def with_updated_value(self, value: ConfigValue) -> "ConfigEntry":
        """Create a new ConfigEntry with updated value (immutable update)."""
        return ConfigEntry(
            key=self.key,
            value=value,
            version=self.version + 1,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            metadata=self.metadata.copy(),
            id=self.id,
        )

    def with_metadata(self, metadata: dict[str, Any]) -> "ConfigEntry":
        """Create a new ConfigEntry with merged metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(metadata)
        return ConfigEntry(
            key=self.key,
            value=self.value,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=new_metadata,
            id=self.id,
        )


@dataclass(frozen=True)
class FeatureFlag:
    """
    Core domain entity representing a feature flag.

    Supports targeting rules and percentage rollouts (DDD Value Objects).
    """

    key: str
    enabled: bool
    rollout_percentage: float = 100.0
    targeting_rules: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Validate entity invariants."""
        if not self.key:
            raise ValueError("FeatureFlag key cannot be empty")
        if not 0 <= self.rollout_percentage <= 100:
            raise ValueError("rollout_percentage must be between 0 and 100")

    def is_enabled_for_user(self, user_id: str, attributes: dict[str, Any]) -> bool:
        """
        Determine if feature is enabled for a specific user.

        Implements targeting rules evaluation (Domain Service pattern).
        """
        if not self.enabled:
            return False

        # Check targeting rules first
        for rule in self.targeting_rules:
            if self._evaluate_rule(rule, user_id, attributes):
                return True

        # Fall back to percentage rollout
        return self._check_percentage_rollout(user_id)

    def _evaluate_rule(self, rule: dict[str, Any], user_id: str, attributes: dict[str, Any]) -> bool:
        """Evaluate a single targeting rule."""
        attribute_name = rule.get("attribute")
        operator = rule.get("operator")
        value = rule.get("value")

        if attribute_name not in attributes:
            return False

        attr_value = attributes[attribute_name]

        match operator:
            case "eq":
                return attr_value == value
            case "ne":
                return attr_value != value
            case "in":
                return attr_value in value
            case "gt":
                return attr_value > value
            case "gte":
                return attr_value >= value
            case "lt":
                return attr_value < value
            case "lte":
                return attr_value <= value
            case _:
                return False

    def _check_percentage_rollout(self, user_id: str) -> bool:
        """Check percentage-based rollout using consistent hashing."""
        # Use consistent hashing for stable percentage assignment
        hash_value = hash(f"{self.key}:{user_id}")
        bucket = abs(hash_value) % 100
        return bucket < self.rollout_percentage
