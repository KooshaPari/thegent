"""
Domain Services

Domain services are used to define operations that don't naturally belong
to a single entity or value object.

Following DDD principles:
- Single Responsibility: Each service has one purpose
- No state: Services are stateless
- Pure logic: No side effects, only business logic
"""

from typing import Callable, TypeVar, Generic, Any
from abc import ABC, abstractmethod

T = TypeVar('T')


class Specification(ABC, Generic[T]):
    """
    Specification pattern for business rule composition.

    Allows combining business rules using AND, OR, NOT operations.

    Following SOLID principles:
    - Open/Closed: Extendable with new operations
    - Single Responsibility: Only defines business rules
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies this specification."""
        pass

    def and_(self, other: "Specification[T]") -> "Specification[T]":
        """Combine with AND operation."""
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "Specification[T]":
        """Combine with OR operation."""
        return OrSpecification(self, other)

    def not_(self) -> "Specification[T]":
        """Negate this specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Combines two specifications with AND."""
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """Combines two specifications with OR."""
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """Negates a specification."""
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)


class SkillSpecification(Specification):
    """Domain service for skill-related business rules."""

    @staticmethod
    def is_active() -> "Specification":
        """Specification for active skills."""
        from hexagonal.domain.entities.skill import Skill
        return ActiveSkillSpecification()

    @staticmethod
    def by_category(category) -> "Specification":
        """Specification for skills by category."""
        from hexagonal.domain.entities.skill import Skill
        return CategorySpecification(category)

    @staticmethod
    def has_tag(tag: str) -> "Specification":
        """Specification for skills with a specific tag."""
        from hexagonal.domain.entities.skill import Skill
        return TagSpecification(tag)


class ActiveSkillSpecification(Specification):
    def is_satisfied_by(self, candidate) -> bool:
        from hexagonal.domain.entities.skill import Skill
        if not isinstance(candidate, Skill):
            return False
        return candidate.is_active


class CategorySpecification(Specification):
    def __init__(self, category):
        self._category = category

    def is_satisfied_by(self, candidate) -> bool:
        from hexagonal.domain.entities.skill import Skill
        if not isinstance(candidate, Skill):
            return False
        return candidate.category == self._category


class TagSpecification(Specification):
    def __init__(self, tag: str):
        self._tag = tag

    def is_satisfied_by(self, candidate) -> bool:
        from hexagonal.domain.entities.skill import Skill
        if not isinstance(candidate, Skill):
            return False
        return self._tag in candidate.tags


class Validator(ABC):
    """
    Base class for domain validators.

    Following KISS: Simple validation before operations
    """
    errors: list[str] = []

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate the value and populate errors."""
        pass

    def is_valid(self, value: Any) -> bool:
        """Check if value is valid."""
        self.errors = []
        return self.validate(value)

    def get_errors(self) -> list[str]:
        """Get validation errors."""
        return list(self.errors)


class SkillValidator(Validator):
    """Validator for skill entities."""

    def validate(self, value: Any) -> bool:
        from hexagonal.domain.entities.skill import Skill
        if not isinstance(value, Skill):
            self.errors.append("Value must be a Skill entity")
            return False

        if not value.name.strip():
            self.errors.append("Skill name cannot be empty")

        if not value.description.strip():
            self.errors.append("Skill description cannot be empty")

        if not value.instructions.strip():
            self.errors.append("Skill instructions cannot be empty")

        return len(self.errors) == 0
