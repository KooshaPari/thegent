"""Session state management for TUI compositor.

Handles session persistence, layout saving, and restoration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from thegent.infra.fast_yaml_parser import yaml_load, yaml_dump


@dataclass
class SessionMetadata:
    """Metadata about a session."""

    id: str
    name: str
    created_at: str
    updated_at: str
    working_dir: str = "."


@dataclass
class SessionState:
    """Manages session state and persistence.

    Handles saving/loading session layouts and metadata to disk.
    """

    SESSION_DIR: Path = field(default_factory=lambda: Path.home() / ".config" / "thegent" / "sessions")
    LAYOUTS_DIR: Path = field(default_factory=lambda: Path.home() / ".config" / "thegent" / "layouts")

    def __post_init__(self) -> None:
        """Initialize directories on instantiation."""
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        self.LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)

    def load_session(self, session_id: str | None = None) -> dict[str, Any] | None:
        """Load session state from disk.

        Args:
            session_id: Session ID to load (uses most recent if not provided)

        Returns:
            Session data dict or None if not found
        """
        if session_id is None:
            session_id = self._get_last_session_id()

        if not session_id:
            return None

        session_file = self.SESSION_DIR / f"{session_id}.yaml"
        if not session_file.exists():
            return None

        try:
            with open(session_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            return None

    def save_session(self, session_id: str, layout: dict[str, Any], metadata: SessionMetadata | None = None) -> None:
        """Save session state to disk.

        Args:
            session_id: Session identifier
            layout: Layout data to save
            metadata: Optional session metadata
        """
        now = datetime.now().isoformat()

        session_data: dict[str, Any] = {
            "id": session_id,
            "layout": layout,
            "updated_at": now,
        }

        if metadata:
            session_data["metadata"] = asdict(metadata)
        else:
            session_data["metadata"] = {
                "id": session_id,
                "name": f"Session {session_id[:8]}",
                "created_at": now,
                "updated_at": now,
                "working_dir": ".",
            }

        session_file = self.SESSION_DIR / f"{session_id}.yaml"
        with open(session_file, "w", encoding="utf-8") as f:
            yaml.dump(session_data, f, default_flow_style=False)

    def save_layout(self, layout_name: str, layout: dict[str, Any]) -> None:
        """Save layout template.

        Args:
            layout_name: Name for the layout
            layout: Layout data to save
        """
        layout_file = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        with open(layout_file, "w", encoding="utf-8") as f:
            yaml.dump(layout, f, default_flow_style=False)

    def load_layout(self, layout_name: str) -> dict[str, Any] | None:
        """Load a saved layout template.

        Args:
            layout_name: Name of the layout to load

        Returns:
            Layout data dict or None if not found
        """
        layout_file = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        if not layout_file.exists():
            return None

        try:
            with open(layout_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (OSError, yaml.YAMLError):
            return None

    def list_layouts(self) -> list[str]:
        """List available layout templates.

        Returns:
            List of layout names
        """
        return [f.stem for f in self.LAYOUTS_DIR.glob("*.yaml")]

    def list_sessions(self) -> list[str]:
        """List available sessions.

        Returns:
            List of session IDs
        """
        return [f.stem for f in self.SESSION_DIR.glob("*.yaml")]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if successful, False otherwise
        """
        session_file = self.SESSION_DIR / f"{session_id}.yaml"
        if not session_file.exists():
            return False

        try:
            session_file.unlink()
            return True
        except OSError:
            return False

    def delete_layout(self, layout_name: str) -> bool:
        """Delete a layout template.

        Args:
            layout_name: Layout to delete

        Returns:
            True if successful, False otherwise
        """
        layout_file = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        if not layout_file.exists():
            return False

        try:
            layout_file.unlink()
            return True
        except OSError:
            return False

    def _get_last_session_id(self) -> str | None:
        """Get ID of most recent session.

        Returns:
            Session ID or None if no sessions exist
        """
        sessions = sorted(self.SESSION_DIR.glob("*.yaml"))
        if not sessions:
            return None
        return sessions[-1].stem
