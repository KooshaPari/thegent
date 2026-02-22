"""Base Pydantic schema for doc frontmatter.

# @trace FR-DOCS-001
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DocType(StrEnum):
    CONVERSATION_DUMP = "conversation-dump"
    SESSION_MEMORY = "session-memory"
    SCRATCH = "scratch"
    AGENT_WORKLOG = "agent-worklog"
    IDEA = "idea"
    RESEARCH = "research"
    DEBUG_LOG = "debug-log"
    CHANGE_PROPOSAL = "change-proposal"
    WORKLOG = "worklog"
    PRD = "prd"
    FR = "fr"
    ADR = "adr"
    USER_JOURNEY = "user-journey"
    IMPL_PLAN = "impl-plan"
    CONTEXT_DOC = "context-doc"
    ARCH_DOC = "arch-doc"
    DESIGN_DOC = "design-doc"
    SPRINT_PLAN = "sprint-plan"
    CHANGE_DESIGN = "change-design"
    CHANGE_TASKS = "change-tasks"
    TEST_LOG = "test-log"
    CHANGELOG = "changelog"
    COMPLETION_REPORT = "completion-report"
    SPRINT_RETRO = "sprint-retro"
    EPIC_RETRO = "epic-retro"
    INCIDENT_RETRO = "incident-retro"
    KB_EXTRACT = "kb-extract"


class DocStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    STAGING = "staging"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class DocFrontmatter(BaseModel):
    type: DocType
    status: DocStatus
    date: str
    title: str
    layer: int = Field(ge=0, le=4)
    relates_to: list[str] = Field(default_factory=list)
    traces_to: list[str] = Field(default_factory=list)
    author: str = "agent"
    session_id: str = ""
    git_commit: str = ""
    tags: list[str] = Field(default_factory=list)
