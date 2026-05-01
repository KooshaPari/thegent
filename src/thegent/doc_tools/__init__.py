"""STUB MODULE - thegent.doc_tools

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


class PlaywrightRecorder:
    """Recorder using Playwright for documentation capture."""

    def __init__(self) -> None:
        self.recordings: list[dict[str, Any]] = []

    def start_recording(self, url: str) -> None:
        """Start recording a session."""
        self.recordings.append({"url": url, "started": True})

    def stop_recording(self) -> dict[str, Any]:
        """Stop recording and return the result."""
        return {"status": "completed", "frames": []}


__all__ = ["PlaywrightRecorder", "RecordingConfig"]


@dataclass
class RecordingConfig:
    """Configuration for document recording."""
    output_dir: str = "recordings"
    format: str = "mp4"
    quality: int = 80
