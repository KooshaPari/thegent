"""Session state management for the TUI compositor.

Handles persistence of layout and session configuration to disk.
"""

from pathlib import Path
from typing import Any

from thegent.infra.fast_yaml_parser import yaml_dump, yaml_load


class SessionState:
    """Manages session persistence for the compositor.

    Attributes:
        session_name: Name of the current session
        session_dir: Directory where session files are stored
    """

    def __init__(self, session_name: str = "default") -> None:
        """Initialize session state.

        Args:
            session_name: Name of the session (default: "default")
        """
        self.session_name = session_name
        self.session_dir = Path.home() / ".config" / "thegent" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / f"{session_name}.yaml"
        self.layout_data: dict | None = None

    def save_session(self, layout: dict[str, Any]) -> bool:
        """Save session state to disk.

        Args:
            layout: Pane layout dictionary to save

        Returns:
            True if save was successful, False otherwise
        """
        try:
            session_data = {
                "session_name": self.session_name,
                "layout": layout,
                "theme": "dark",  # Default theme
            }

            with self.session_file.open("w", encoding="utf-8") as file_handle:
                yaml_dump(session_data, file_handle, default_flow_style=False)

            self.layout_data = layout
            return True
        except Exception:
            return False

    def load_session(self) -> dict | None:
        """Load session state from disk.

        Returns:
            Layout dictionary if session exists, None otherwise
        """
        if not self.session_file.exists():
            return None

        try:
            with self.session_file.open(encoding="utf-8") as file_handle:
                data = yaml_load(file_handle)

            if data is None:
                return None

            self.layout_data = data.get("layout")
            return self.layout_data
        except Exception:
            return None

    def delete_session(self) -> bool:
        """Delete the session file.

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except Exception:
            return False

    def list_sessions(self) -> list[str]:
        """List all available sessions.

        Returns:
            List of session names
        """
        try:
            sessions = [f.stem for f in self.session_dir.glob("*.yaml")]
            return sorted(sessions)
        except Exception:
            return []

    def session_exists(self) -> bool:
        """Check if the session file exists.

        Returns:
            True if session file exists, False otherwise
        """
        return self.session_file.exists()
