"""Session persistence for TUI compositor.

Saves and restores session state including layouts, history, and settings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .layouts.manager import LayoutManager, LayoutState


@dataclass
class SessionInfo:
    """Session metadata."""

    session_id: str
    start_time: str
    last_active: str
    agent_name: str | None = None
    cwd: str | None = None
    layout_name: str = "default"
    state: dict[str, Any] = field(default_factory=dict)


class SessionPersistence:
    """Manages session persistence to disk."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._storage_dir = storage_dir or Path.home() / ".cache" / "thegent" / "sessions"
        self._sessions: dict[str, SessionInfo] = {}
        self._current_session: str | None = None
        self._layout_manager = LayoutManager()
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load all saved sessions from disk."""
        sessions_dir = self._storage_dir / "session_data"
        if not sessions_dir.exists():
            return

        for session_file in sessions_dir.glob("*.json"):
            try:
                data = json.loads(session_file.read_text())
                session = SessionInfo(
                    session_id=data.get("session_id", session_file.stem),
                    start_time=data.get("start_time", ""),
                    last_active=data.get("last_active", ""),
                    agent_name=data.get("agent_name"),
                    cwd=data.get("cwd"),
                    layout_name=data.get("layout_name", "default"),
                    state=data.get("state", {}),
                )
                self._sessions[session.session_id] = session
            except Exception:
                pass

    def _save_session(self, session: SessionInfo) -> None:
        """Save a session to disk."""
        sessions_dir = self._storage_dir / "session_data"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "last_active": session.last_active,
            "agent_name": session.agent_name,
            "cwd": session.cwd,
            "layout_name": session.layout_name,
            "state": session.state,
        }
        (sessions_dir / f"{session.session_id}.json").write_text(json.dumps(data, indent=2))

    def create_session(
        self,
        session_id: str,
        agent_name: str | None = None,
        cwd: str | None = None,
    ) -> SessionInfo:
        """Create a new session."""
        now = datetime.now().isoformat()
        session = SessionInfo(
            session_id=session_id,
            start_time=now,
            last_active=now,
            agent_name=agent_name,
            cwd=cwd,
            layout_name="default",
        )
        self._sessions[session_id] = session
        self._current_session = session_id
        self._save_session(session)
        return session

    def get_session(self, session_id: str) -> SessionInfo | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def update_session(
        self,
        session_id: str,
        **kwargs,
    ) -> SessionInfo | None:
        """Update session fields."""
        session = self._sessions.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.last_active = datetime.now().isoformat()
            self._save_session(session)
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            session_file = self._storage_dir / "session_data" / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            if self._current_session == session_id:
                self._current_session = None
            return True
        return False

    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session."""
        if session_id in self._sessions:
            self._current_session = session_id
            return True
        return False

    def get_current_session(self) -> SessionInfo | None:
        """Get the current session."""
        if self._current_session:
            return self._sessions.get(self._current_session)
        return None

    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        return list(self._sessions.keys())

    def save_layout_for_session(
        self,
        session_id: str,
        layout_state: LayoutState,
    ) -> bool:
        """Save a layout for a specific session."""
        session = self._sessions.get(session_id)
        if session:
            self._layout_manager.create_layout(
                name=f"session-{session_id}",
                root=layout_state.root,
                sidebar_visible=layout_state.sidebar_visible,
                sidebar_width=layout_state.sidebar_width,
                output_maximized=layout_state.output_maximized,
                metadata={"session_id": session_id},
            )
            session.layout_name = layout_state.name
            self._save_session(session)
            return True
        return False

    def get_layout_for_session(self, session_id: str) -> LayoutState | None:
        """Get the saved layout for a session."""
        return self._layout_manager.get_layout(f"session-{session_id}")

    def save_state(self, session_id: str, key: str, value: Any) -> bool:
        """Save arbitrary state for a session."""
        session = self._sessions.get(session_id)
        if session:
            session.state[key] = value
            self._save_session(session)
            return True
        return False

    def load_state(self, session_id: str, key: str, default: Any = None) -> Any:
        """Load state for a session."""
        session = self._sessions.get(session_id)
        if session:
            return session.state.get(key, default)
        return default

    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Delete sessions older than max_age_days."""
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        deleted = 0

        for session_id, session in list(self._sessions.items()):
            try:
                last_active = datetime.fromisoformat(session.last_active)
                if last_active.timestamp() < cutoff:
                    self.delete_session(session_id)
                    deleted += 1
            except Exception:
                pass

        return deleted

    def get_statistics(self) -> dict[str, Any]:
        """Get session statistics."""
        total = len(self._sessions)
        now = datetime.now()

        recent_24h = 0
        recent_7d = 0

        for session in self._sessions.values():
            try:
                last_active = datetime.fromisoformat(session.last_active)
                age_hours = (now - last_active).total_seconds() / 3600
                if age_hours < 24:
                    recent_24h += 1
                if age_hours < 168:  # 7 days
                    recent_7d += 1
            except Exception:
                pass

        return {
            "total_sessions": total,
            "sessions_24h": recent_24h,
            "sessions_7d": recent_7d,
            "saved_layouts": len(self._layout_manager.list_layouts()),
            "storage_dir": str(self._storage_dir),
        }
