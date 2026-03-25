"""Session query interface. Breaks cli ↔ execution circular dependency.

This port allows execution modules to query session state without importing from cli.
The concrete implementation (ps_impl, _find_session_meta) lives in cli but is injected.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from thegent.config import ThegentSettings


class SessionQuerier(Protocol):
    """Query running sessions and their metadata.

    Implementations: session_ops_list_impl.ps_impl, session_meta_impl._find_session_meta
    """

    def list_sessions(
        self,
        owner: str | None = None,
        all: bool = False,
        agent: str | None = None,
        status: str | None = None,
        limit: int = 50,
        scan_ide: bool = False,
        include_contract: bool = False,
    ) -> list[dict[str, Any]]:
        """List agent sessions.

        Args:
            owner: Filter by session owner
            all: Include all sessions
            agent: Filter by agent name
            status: Filter by session status
            limit: Maximum number of sessions
            scan_ide: Scan IDE for sessions
            include_contract: Include contract details

        Returns:
            List of session dictionaries with id, status, etc.
        """
        ...

    def find_session_meta(self, settings: ThegentSettings, session_id: str) -> Path:
        """Find session metadata file path.

        Args:
            settings: Thegent settings with session_dir
            session_id: Session ID to find

        Returns:
            Path to session metadata JSON file

        Raises:
            typer.BadParameter: If session not found
        """
        ...


__all__ = ["SessionQuerier"]
