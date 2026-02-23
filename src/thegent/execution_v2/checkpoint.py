"""Checkpoint module. Extracted from execution.py."""
from pathlib import Path
from pydantic import BaseModel

class CheckpointMeta(BaseModel):
    checkpoint_id: str

class CheckpointRegistry:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
    def create_checkpoint(self, reason: str, dag_content: str, owner: str):
        return CheckpointMeta(checkpoint_id="stub")
    def list_checkpoints(self, limit: int = 20):
        return []

__all__ = ["CheckpointRegistry", "CheckpointMeta"]
