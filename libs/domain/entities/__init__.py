"""
Domain Entities

Entities are objects with a distinct identity that runs through time and
different representations of the same conceptual thing.

Following SOLID principles:
- Single Responsibility: Each entity has one reason to change
- Open/Closed: Entities are open for extension, closed for modification
"""

from .skill import Skill, SkillCategory, SkillId, Entity, DomainEvent, Identifier

__all__ = ["Skill", "SkillCategory", "SkillId", "Entity", "DomainEvent", "Identifier"]
