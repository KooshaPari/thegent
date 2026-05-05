"""Shared CLI utilities.

This module provides shared utilities used across CLI commands.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_session_dir() -> Path:
    """Get the session directory from environment or default.
    
    Returns:
        Path to the session directory.
    """
    session_dir = os.environ.get("THGENT_SESSION_DIR", "/tmp/thegent/sessions")
    path = Path(session_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_owner_dir(owner: str, session_dir: Path | None = None) -> Path:
    """Resolve the directory for a specific owner.
    
    Args:
        owner: The owner tag.
        session_dir: Optional session directory.
        
    Returns:
        Path to the owner's session directory.
    """
    if session_dir is None:
        session_dir = get_session_dir()
    
    owner_dir = session_dir / owner.replace(":", "_")
    owner_dir.mkdir(parents=True, exist_ok=True)
    return owner_dir


__all__ = [
    "get_session_dir",
    "resolve_owner_dir",
]
