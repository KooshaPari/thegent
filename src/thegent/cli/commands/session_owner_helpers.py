"""Session owner helpers module."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def get_session_owner(session_id: str) -> str | None:
    """Get the owner of a session."""
    return None


def set_session_owner(session_id: str, owner: str) -> bool:
    """Set the owner of a session."""
    return True


__all__ = ["get_session_owner", "set_session_owner"]
