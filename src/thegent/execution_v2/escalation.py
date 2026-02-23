"""Escalation module. Extracted from execution.py."""
from pathlib import Path

class EscalationQueue:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
    def add(self, run_id: str, reason: str) -> None:
        pass
    def list_pending(self, limit: int = 50):
        return []

class DLQManager:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
    def enqueue(self, run_meta, error: str) -> None:
        pass

__all__ = ["EscalationQueue", "DLQManager"]
