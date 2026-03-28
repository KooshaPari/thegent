"""
Skill Queries

Query definitions for skill-related operations.
Following CQRS pattern: Queries represent intent to read state.
"""

from dataclasses import dataclass
from typing import Optional

from hexagonal.ports.inbound import Query


@dataclass
class GetSkillQuery(Query):
    """Query to get a single skill by ID."""
    skill_id: str


@dataclass
class ListSkillsQuery(Query):
    """Query to list skills with optional filters."""
    category: Optional[str] = None
    tag: Optional[str] = None
    is_active: Optional[bool] = None
    limit: int = 100
    offset: int = 0


@dataclass
class SearchSkillsQuery(Query):
    """Query to search skills by name or description."""
    search_term: str
    limit: int = 50


@dataclass
class GetSkillToolsQuery(Query):
    """Query to get tools for a skill."""
    skill_id: str


@dataclass
class GetSkillHistoryQuery(Query):
    """Query to get the change history of a skill."""
    skill_id: str
    limit: int = 50
