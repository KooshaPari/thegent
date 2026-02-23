"""Audit package for thegent."""

from pydantic import BaseModel

class AuditEntry(BaseModel):
    """Audit entry model."""

class ShadowAuditGit:
    """Shadow audit git implementation."""

class GitJournal:
    """Git journal implementation."""

class GitJournalAsync(GitJournal):
    """Async git journal."""

__all__ = ["AuditEntry", "ShadowAuditGit", "GitJournal", "GitJournalAsync"]
