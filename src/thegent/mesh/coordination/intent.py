"""Agent edit intents + IntentRegistry + ConflictPrediction (TGNT-P7.2).

Canonical home for ``EditIntent``, ``ConflictPrediction``, and
``IntentRegistry``. Backed by ``src/thegent/mesh/coordination/intent.py``.
The legacy flat path ``from thegent.mesh.coordination import (EditIntent,
ConflictPrediction, IntentRegistry)`` is preserved as a re-export in
``src/thegent/mesh/coordination/__init__.py``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from .hlc import HLCTimestamp


@dataclass
class EditIntent:
    """Describes an agent's planned edit operation (TGNT-P7.2).

    An intent captures *what* an agent plans to do before it commits,
    enabling trial-merge conflict prediction.
    """

    agent_id: str
    file_path: str
    operation: str  # "modify", "create", "delete"
    line_ranges: list[tuple[int, int]] = field(default_factory=list)
    new_content: str | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = str(HLCTimestamp().update())


@dataclass
class ConflictPrediction:
    """Result of a trial-merge conflict prediction (TGNT-P7.2)."""

    has_conflict: bool
    conflicting_files: list[str] = field(default_factory=list)
    details: str = ""


class IntentRegistry:
    """Registry for agent edit intents (TGNT-P7.2).

    Agents register their planned edits before committing. The registry
    enables trial-merge conflict prediction by comparing intents.
    """

    def __init__(self, mesh_root: Path) -> None:
        self.intents_dir = mesh_root / "intents"
        self.intents_dir.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def register_intent(self, intent: EditIntent) -> Path:
        """Register an agent's edit intent."""
        intent_id = hashlib.sha256(f"{intent.agent_id}:{intent.file_path}:{intent.timestamp}".encode()).hexdigest()
        intent_file = self.intents_dir / f"{intent_id}.json"
        data = {
            "agent_id": intent.agent_id,
            "file_path": intent.file_path,
            "operation": intent.operation,
            "line_ranges": intent.line_ranges,
            "new_content": intent.new_content,
            "timestamp": intent.timestamp,
        }
        with open(intent_file, "w") as f:
            json.dump(data, f)
        return intent_file

    def _load_intent(self, intent_file: Path, agent_id: str | None) -> EditIntent | None:
        """Load an intent from file, optionally filtering by agent_id."""
        with open(intent_file) as f:
            data = json.load(f)
        if agent_id is None or data["agent_id"] == agent_id:
            return EditIntent(
                agent_id=data["agent_id"],
                file_path=data["file_path"],
                operation=data["operation"],
                line_ranges=data.get("line_ranges", []),
                new_content=data.get("new_content"),
                timestamp=data.get("timestamp"),
            )
        return None

    def _delete_intent_if_owned(self, intent_file: Path, agent_id: str) -> bool:
        """Delete an intent file if owned by the specified agent. Returns True if deleted."""
        with open(intent_file) as f:
            data = json.load(f)
        if data["agent_id"] == agent_id:
            intent_file.unlink()
            return True
        return False

    def get_intents(self, agent_id: str | None = None) -> list[EditIntent]:
        """Retrieve registered intents, optionally filtered by agent."""
        intents: list[EditIntent] = []
        for intent_file in self.intents_dir.glob("*.json"):
            intent = self._load_intent(intent_file, agent_id)
            if intent is not None:
                intents.append(intent)
        return intents

    def clear_intents(self, agent_id: str) -> int:
        """Clear all intents for a given agent (post-commit cleanup)."""
        count = 0
        for intent_file in self.intents_dir.glob("*.json"):
            if self._delete_intent_if_owned(intent_file, agent_id):
                count += 1
        return count


__all__ = ["EditIntent", "ConflictPrediction", "IntentRegistry"]
