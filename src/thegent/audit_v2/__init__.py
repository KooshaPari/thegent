"""Audit package for thegent."""

from pydantic import BaseModel

class AuditEntry(BaseModel):
    """Audit entry model."""
    pass

class ShadowAuditGit:
    """Shadow audit git implementation."""
    pass

class GitJournal:
    """Git journal implementation."""
    pass

class GitJournalAsync(GitJournal):
    """Async git journal."""
    pass

__all__ = ["AuditEntry", "ShadowAuditGit", "GitJournal", "GitJournalAsync"]
