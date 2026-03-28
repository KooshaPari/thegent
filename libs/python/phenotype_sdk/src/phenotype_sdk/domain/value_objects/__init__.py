"""Domain value objects - Immutable types representing specific values."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Union


class ValueType(Enum):
    """Enumeration of supported configuration value types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


@dataclass(frozen=True)
class ConfigValue:
    """
    Value object representing a typed configuration value.

    Immutable and validated at construction time.
    Enforces type safety throughout the domain (DDD Value Object pattern).
    """

    raw: Any
    value_type: ValueType

    def __post_init__(self) -> None:
        """Validate value matches declared type."""
        self._validate()

    def _validate(self) -> None:
        """Type validation based on ValueType."""
        match self.value_type:
            case ValueType.STRING:
                if not isinstance(self.raw, str):
                    raise TypeError(f"Expected string, got {type(self.raw).__name__}")
            case ValueType.INTEGER:
                if not isinstance(self.raw, int) or isinstance(self.raw, bool):
                    raise TypeError(f"Expected integer, got {type(self.raw).__name__}")
            case ValueType.FLOAT:
                if not isinstance(self.raw, (int, float)) or isinstance(self.raw, bool):
                    raise TypeError(f"Expected float, got {type(self.raw).__name__}")
            case ValueType.BOOLEAN:
                if not isinstance(self.raw, bool):
                    raise TypeError(f"Expected boolean, got {type(self.raw).__name__}")
            case ValueType.JSON:
                if not isinstance(self.raw, (dict, list)):
                    raise TypeError(f"Expected JSON object/array, got {type(self.raw).__name__}")
            case ValueType.SECRET:
                # Secrets are strings but should be handled specially
                if not isinstance(self.raw, str):
                    raise TypeError(f"Expected string for secret, got {type(self.raw).__name__}")

    @property
    def as_typed(self) -> Union[str, int, float, bool, dict, list]:
        """Return the value as its native Python type."""
        return self.raw

    @classmethod
    def from_primitive(cls, value: Any, value_type: ValueType) -> "ConfigValue":
        """Factory method to create ConfigValue from a primitive."""
        return cls(raw=value, value_type=value_type)


@dataclass(frozen=True)
class SecretValue(ConfigValue):
    """Specialized value object for secrets with masking support."""

    def __str__(self) -> str:
        """Return masked representation for logging."""
        return "***REDACTED***"

    def reveal(self) -> str:
        """Return the actual secret value (use carefully)."""
        if not isinstance(self.raw, str):
            raise TypeError("Secret can only contain string values")
        return self.raw
