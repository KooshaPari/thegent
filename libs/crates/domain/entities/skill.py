"""
Skill Entity

Represents a skill in the system with full domain logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, ClassVar
from enum import Enum


class Identifier:
    """Base class for value objects used as identifiers."""
    value: str
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


class Entity:
    """Base class for domain entities."""
    def entity_id(self) -> Identifier:
        raise NotImplementedError


class DomainEvent:
    """Base class for domain events."""
    pass


class SkillCategory(Enum):
    """Categories for skills."""
    DEVELOPMENT = "development"
    QUALITY = "quality"
    OPERATIONS = "operations"
    SECURITY = "security"
    DATA = "data"
    INFRASTRUCTURE = "infrastructure"
    COMMUNICATION = "communication"
    OTHER = "other"


@dataclass
class SkillId(Identifier):
    """Unique identifier for a skill."""
    value: str

    def __str__(self) -> str:
        return self.value

    @classmethod
    def generate(cls) -> "SkillId":
        import uuid
        return cls(value=str(uuid.uuid4()))


@dataclass
class Skill(Entity):
    """
    Skill entity representing a reusable capability.

    An entity with:
    - Unique identity (id)
    - Mutable state
    - Domain logic encapsulated in methods

    Following DDD principles:
    - Identity is stable and unique
    - State changes are validated
    - Domain events are raised on changes
    """
    id: SkillId
    name: str
    description: str
    category: SkillCategory
    instructions: str
    tools: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    def entity_id(self) -> Identifier:
        """Return the entity's unique identifier."""
        return self.id

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        """
        Update skill attributes with validation.

        Following KISS: Simple validation before update
        """
        if name is not None:
            if not name.strip():
                raise ValueError("Skill name cannot be empty")
            self.name = name.strip()

        if description is not None:
            self.description = description.strip()

        if instructions is not None:
            if not instructions.strip():
                raise ValueError("Skill instructions cannot be empty")
            self.instructions = instructions.strip()

        if tools is not None:
            self.tools = list(tools)

        if tags is not None:
            self.tags = list(tags)

        self.updated_at = datetime.utcnow()
        self._events.append(SkillUpdated(skill_id=str(self.id)))

    def activate(self) -> None:
        """Activate the skill."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()
            self._events.append(SkillActivated(skill_id=str(self.id)))

    def deactivate(self) -> None:
        """Deactivate the skill."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()
            self._events.append(SkillDeactivated(skill_id=str(self.id)))

    def add_tool(self, tool: str) -> None:
        """Add a tool to the skill."""
        if tool not in self.tools:
            self.tools.append(tool)
            self.updated_at = datetime.utcnow()
            self._events.append(SkillToolAdded(skill_id=str(self.id), tool=tool))

    def remove_tool(self, tool: str) -> None:
        """Remove a tool from the skill."""
        if tool in self.tools:
            self.tools.remove(tool)
            self.updated_at = datetime.utcnow()
            self._events.append(SkillToolRemoved(skill_id=str(self.id), tool=tool))

    def pull_and_merge_events(self) -> list[DomainEvent]:
        """Pull and clear domain events (for event sourcing)."""
        events = list(self._events)
        self._events.clear()
        return events


# Domain Events
@dataclass
class SkillCreated(DomainEvent):
    """Event raised when a new skill is created."""
    skill_id: str
    name: str
    category: str

    def event_type(self) -> str:
        return "skill.created"


@dataclass
class SkillUpdated(DomainEvent):
    """Event raised when a skill is updated."""
    skill_id: str

    def event_type(self) -> str:
        return "skill.updated"


@dataclass
class SkillActivated(DomainEvent):
    """Event raised when a skill is activated."""
    skill_id: str

    def event_type(self) -> str:
        return "skill.activated"


@dataclass
class SkillDeactivated(DomainEvent):
    """Event raised when a skill is deactivated."""
    skill_id: str

    def event_type(self) -> str:
        return "skill.deactivated"


@dataclass
class SkillToolAdded(DomainEvent):
    """Event raised when a tool is added to a skill."""
    skill_id: str
    tool: str

    def event_type(self) -> str:
        return "skill.tool_added"


@dataclass
class SkillToolRemoved(DomainEvent):
    """Event raised when a tool is removed from a skill."""
    skill_id: str
    tool: str

    def event_type(self) -> str:
        return "skill.tool_removed"
