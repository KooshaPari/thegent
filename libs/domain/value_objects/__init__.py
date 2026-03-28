"""
Domain Value Objects

Value objects are immutable objects defined by their attributes rather than
a unique identity. They are compared by their attribute values.

Following DDD principles:
- Immutable: Once created, cannot be modified
- Value-based equality: Two value objects with same values are equal
- Side-effect free: No behavior that modifies state
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Hashable
import re


@dataclass(frozen=True)
class Identifier(ABC):
    """
    Base class for all identifiers.

    Identifiers are value objects that uniquely identify an entity.
    They are immutable and compared by value.

    Following SOLID:
    - Interface Segregation: Simple interface with just the value
    - Single Responsibility: Only identity concerns
    """
    value: Hashable

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class StringId(Identifier):
    """String-based identifier."""
    value: str


@dataclass(frozen=True)
class UuidId(Identifier):
    """UUID-based identifier."""
    value: str

    @classmethod
    def generate(cls) -> "UuidId":
        import uuid
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, value: str) -> "UuidId":
        """Create from a string representation."""
        return cls(value=value)


@dataclass(frozen=True)
class EmailAddress:
    """
    Email address value object.

    Validates format and normalizes to lowercase.
    """
    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email address: {self.value}")
        # Normalize to lowercase
        object.__setattr__(self, 'value', self.value.lower())

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Url:
    """URL value object with validation."""
    value: str

    def __post_init__(self):
        if not self._is_valid_url(self.value):
            raise ValueError(f"Invalid URL: {self.value}")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Version:
    """Semantic version value object."""
    major: int
    minor: int
    patch: int
    prerelease: str = ""

    def __post_init__(self):
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Version numbers cannot be negative")

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    def bump_major(self) -> "Version":
        return Version(major=self.major + 1, minor=0, patch=0)

    def bump_minor(self) -> "Version":
        return Version(major=self.major, minor=self.minor + 1, patch=0)

    def bump_patch(self) -> "Version":
        return Version(major=self.major, minor=self.minor, patch=self.patch + 1)


@dataclass(frozen=True)
class Timestamp:
    """Timestamp value object for tracking temporal data."""
    value: str  # ISO 8601 format

    @classmethod
    def now(cls) -> "Timestamp":
        from datetime import datetime
        return cls(value=datetime.utcnow().isoformat() + "Z")

    @classmethod
    def from_datetime(cls, dt: Any) -> "Timestamp":
        return cls(value=dt.isoformat() + "Z")

    def to_datetime(self) -> Any:
        from datetime import datetime
        return datetime.fromisoformat(self.value.rstrip('Z'))
