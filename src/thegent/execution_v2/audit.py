"""Audit module.

Extracted from execution.py.
"""

from pathlib import Path
from pydantic import BaseModel


class AuditEntry(BaseModel):
    """Audit entry model."""
    run_id: str
    action: str


class AuditRegistry:
    """Manages audit registry."""
    
    def __init__(self, audit_path: Path) -> None:
        self.audit_path = audit_path
    
    def record(self, entry: AuditEntry) -> None:
        """Record audit entry."""
        pass


__all__ = ["AuditEntry", "AuditRegistry"]
