"""
Skill Commands

Command definitions for skill-related operations.
Following CQRS pattern: Commands represent intent to change state.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from ...ports.inbound import Command


@dataclass
class CreateSkillCommand(Command):
    """
    Command to create a new skill.

    Attributes:
        name: Skill name
        description: Skill description
        category: Skill category
        instructions: Skill instructions
        tools: List of tool names
        tags: List of tags
    """
    name: str
    description: str
    category: str
    instructions: str
    tools: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class UpdateSkillCommand(Command):
    """
    Command to update an existing skill.

    Attributes:
        skill_id: ID of the skill to update
        name: New name (optional)
        description: New description (optional)
        instructions: New instructions (optional)
        tools: New tools list (optional)
        tags: New tags list (optional)
    """
    skill_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[list[str]] = None
    tags: Optional[list[str]] = None


@dataclass
class DeleteSkillCommand(Command):
    """Command to delete a skill."""
    skill_id: str


@dataclass
class ActivateSkillCommand(Command):
    """Command to activate a skill."""
    skill_id: str


@dataclass
class DeactivateSkillCommand(Command):
    """Command to deactivate a skill."""
    skill_id: str


@dataclass
class AddToolToSkillCommand(Command):
    """Command to add a tool to a skill."""
    skill_id: str
    tool: str


@dataclass
class RemoveToolFromSkillCommand(Command):
    """Command to remove a tool from a skill."""
    skill_id: str
    tool: str


@dataclass
class CloneSkillCommand(Command):
    """Command to clone a skill from another source."""
    source_url: str
    target_name: Optional[str] = None
    target_category: Optional[str] = None
