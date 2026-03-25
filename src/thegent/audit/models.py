"""Audit models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id() -> str:
    """Generate a new UUID."""
    return str(uuid4())


def now_iso() -> str:
    """Get current ISO timestamp."""
    return datetime.now().isoformat()


class AuditEntry(BaseModel):
    """Audit log entry."""

    id: str = Field(default_factory=new_id)
    timestamp: str = Field(default_factory=now_iso)
    operation: str
    repo_path: str
    details: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"
    error: str | None = None
