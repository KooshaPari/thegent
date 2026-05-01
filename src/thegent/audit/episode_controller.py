"""STUB MODULE - thegent.audit.episode_controller

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

from typing import Any


class EpisodeController:
    """Stub implementation of EpisodeController."""

    def __init__(self) -> None:
        self.episodes: dict[str, Any] = {}

    def start_episode(self, episode_id: str) -> None:
        """Start an episode."""
        self.episodes[episode_id] = {"status": "active"}

    def end_episode(self, episode_id: str) -> None:
        """End an episode."""
        if episode_id in self.episodes:
            self.episodes[episode_id]["status"] = "completed"


__all__ = ["EpisodeController"]
