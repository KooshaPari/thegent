"""WP-22002: AI Scratchpad for Multi-Turn Command Drafting.
Provides a persistent buffer for drafting complex multi-line CLI commands.
Integration layer between agents and the shell buffer.
"""

import json
import logging
import os
from pathlib import Path

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class ScratchpadState(BaseModel):
    """Current state of the AI scratchpad."""

    buffer: list[str] = []
    metadata: dict = {}


class AIScratchpad:
    """Manages a persistent drafting buffer for CLI commands."""

    def __init__(self, state_path: Path | None = None) -> None:
        self.state_path = state_path or Path.home() / ".thegent" / "scratchpad.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> ScratchpadState:
        if not self.state_path.exists():
            return ScratchpadState()
        try:
            with open(self.state_path) as f:
                return ScratchpadState.model_validate_json(f.read())
        except Exception as e:
            _log.error("Failed to load scratchpad state: %s", e)
            return ScratchpadState()

    def _save_state(self) -> None:
        try:
            with open(self.state_path, "w") as f:
                f.write(self.state.model_dump_json(indent=2))
        except Exception as e:
            _log.error("Failed to save scratchpad state: %s", e)

    def add_line(self, line: str) -> None:
        """Add a command line to the buffer."""
        self.state.buffer.append(line)
        self._save_state()

    def get_content(self) -> str:
        """Get the full content of the buffer."""
        return "\n".join(self.state.buffer)

    def clear(self) -> None:
        """Clear the buffer."""
        self.state.buffer = []
        self._save_state()

    def delete_last(self) -> None:
        """Remove the last line from the buffer."""
        if self.state.buffer:
            self.state.buffer.pop()
            self._save_state()

    def set_metadata(self, key: str, value: str) -> None:
        """Set metadata for the current draft (e.g., task_id)."""
        self.state.metadata[key] = value
        self._save_state()
