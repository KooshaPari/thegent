"""SessionState - Session persistence and management."""

import logging
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class SessionState:
    """Manages session state persistence."""

    DEFAULT_SESSION_DIR = Path.home() / ".config" / "thegent" / "sessions"

    def __init__(self, session_id: str, session_dir: Path | None = None) -> None:
        """Initialize SessionState.

        Args:
            session_id: Unique session identifier
            session_dir: Directory for storing sessions (default: ~/.config/thegent/sessions)
        """
        self.session_id = session_id
        self.session_dir = session_dir or self.DEFAULT_SESSION_DIR
        self.session_file = self.session_dir / f"{session_id}.yaml"
        self.created_at = datetime.now()
        self.last_modified = datetime.now()

        # Ensure session directory exists
        self.session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SessionState initialized: {session_id} at {self.session_dir}")

    def save(self, state_data: dict) -> bool:
        """Save session state to disk.

        Args:
            state_data: Dictionary of state to save

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Saving session state to {self.session_file}")
            state_data["session_id"] = self.session_id
            state_data["created_at"] = self.created_at.isoformat()
            state_data["last_modified"] = datetime.now().isoformat()

            with open(self.session_file, "w") as f:
                yaml.dump(state_data, f, default_flow_style=False)

            self.last_modified = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
            return False

    def load(self) -> dict | None:
        """Load session state from disk.

        Returns:
            Dictionary of state, or None if not found
        """
        try:
            if not self.session_file.exists():
                logger.warning(f"Session file not found: {self.session_file}")
                return None

            logger.debug(f"Loading session state from {self.session_file}")

            with open(self.session_file) as f:
                state_data = yaml.safe_load(f)

            if state_data:
                self.last_modified = datetime.fromisoformat(state_data.get("last_modified", datetime.now().isoformat()))

            return state_data

        except Exception as e:
            logger.error(f"Failed to load session state: {e}")
            return None

    def delete(self) -> bool:
        """Delete session state file.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.session_file.exists():
                logger.info(f"Deleting session file: {self.session_file}")
                self.session_file.unlink()
            return True

        except Exception as e:
            logger.error(f"Failed to delete session state: {e}")
            return False

    def list_sessions(self) -> list[str]:
        """List all available sessions.

        Returns:
            List of session IDs
        """
        try:
            sessions = []
            if self.session_dir.exists():
                for file in self.session_dir.glob("*.yaml"):
                    sessions.append(file.stem)
            logger.debug(f"Found {len(sessions)} sessions")
            return sorted(sessions)

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
