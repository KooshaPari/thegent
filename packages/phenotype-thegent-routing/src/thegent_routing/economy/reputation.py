"""WP-26003: Decentralized Reputation System.
Tracks agent performance and reliability across the global mesh.
Uses weighted feedback and consensus to build decentralized trust scores.
"""

import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class ReputationEntry(BaseModel):
    """A single reputation event for an agent."""

    agent_id: str
    reviewer_id: str
    task_id: str
    rating: float  # 0.0 to 1.0
    feedback_hash: str
    timestamp: str = datetime.now(UTC).isoformat()


class ReputationManager:
    """Manages decentralized trust and reputation for mesh agents."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.ledger: list[ReputationEntry] = []
        # agent_id -> {score, count}
        self.scores: dict[str, dict[str, float]] = {}
        self.db_path = db_path
        self._load()

    def _load(self) -> None:
        """Load reputation data from database or file."""
        if not self.db_path:
            return

        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. Load aggregate scores from reputation table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reputation'")
            if cursor.fetchone():
                cursor.execute("SELECT agent_id, trust_score, entries_count, xp, level FROM reputation")
                for row in cursor.fetchall():
                    agent_id, score, count, xp, level = row
                    self.scores[agent_id] = {"score": score, "count": float(count), "xp": xp, "level": level}

            # 2. Load history from reputation_entries table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reputation_entries'")
            if cursor.fetchone():
                cursor.execute(
                    "SELECT agent_id, rating, reviewer_id, task_id, feedback_hash, timestamp FROM reputation_entries"
                )
                for row in cursor.fetchall():
                    agent_id, rating, rev_id, task_id, fb_hash, ts = row
                    entry = ReputationEntry(
                        agent_id=agent_id,
                        rating=rating,
                        reviewer_id=rev_id,
                        task_id=task_id,
                        feedback_hash=fb_hash,
                        timestamp=ts,
                    )
                    self.ledger.append(entry)
                    # Only update memory if not already loaded from reputation table
                    if agent_id not in self.scores:
                        self._update_score_in_memory(agent_id, rating)

            conn.close()
        except Exception as e:
            _log.error(f"Failed to load reputation from DB: {e}")

    def submit_rating(self, agent_id: str, reviewer_id: str, task_id: str, rating: float, feedback: str):
        """Submit a rating for an agent's performance on a task."""
        _log.info("Submitting reputation rating for %s from %s: %.2f", agent_id, reviewer_id, rating)

        entry = ReputationEntry(
            agent_id=agent_id,
            reviewer_id=reviewer_id,
            task_id=task_id,
            rating=rating,
            feedback_hash=hashlib.sha256(feedback.encode()).hexdigest(),
        )
        self.ledger.append(entry)
        self._update_score_in_memory(agent_id, rating)
        self._persist_entry(entry)

    def _update_score_in_memory(self, agent_id: str, rating: float):
        """Update the aggregate score in memory."""
        if agent_id not in self.scores:
            self.scores[agent_id] = {"score": rating, "count": 1.0, "xp": 0, "level": 1}
        else:
            current = self.scores[agent_id]
            new_count = current["count"] + 1
            new_score = ((current["score"] * current["count"]) + rating) / new_count
            self.scores[agent_id].update({"score": new_score, "count": new_count})

    def _persist_entry(self, entry: ReputationEntry):
        """Persist reputation entry to database."""
        if not self.db_path:
            return

        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. Insert history entry
            cursor.execute(
                """
                INSERT INTO reputation_entries
                (agent_id, reviewer_id, task_id, rating, feedback_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (entry.agent_id, entry.reviewer_id, entry.task_id, entry.rating, entry.feedback_hash, entry.timestamp),
            )

            # 2. Update aggregate reputation table
            score_data = self.scores.get(entry.agent_id, {"score": entry.rating, "count": 1, "xp": 0, "level": 1})
            cursor.execute(
                """
                INSERT INTO reputation (agent_id, trust_score, entries_count, last_updated, xp, level)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    trust_score = excluded.trust_score,
                    entries_count = excluded.entries_count,
                    last_updated = excluded.last_updated
                """,
                (
                    entry.agent_id,
                    score_data["score"],
                    int(score_data["count"]),
                    entry.timestamp,
                    score_data.get("xp", 0),
                    score_data.get("level", 1),
                ),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            _log.error(f"Failed to persist reputation to DB: {e}")

    def get_trust_score(self, agent_id: str) -> float:
        """Retrieve the current trust score for an agent."""
        return self.scores.get(agent_id, {}).get("score", 0.5)  # Default 0.5 for new agents

    def get_all_scores(self) -> dict[str, float]:
        """Get all agent trust scores."""
        return {agent_id: data["score"] for agent_id, data in self.scores.items()}

    def get_reputation_report(self, agent_id: str) -> dict[str, Any]:
        """Generate a detailed reputation report for an agent."""
        score_data = self.scores.get(agent_id, {"score": 0.5, "count": 0})
        history = [e for e in self.ledger if e.agent_id == agent_id]

        return {
            "agent_id": agent_id,
            "trust_score": score_data["score"],
            "total_ratings": score_data["count"],
            "recent_history": [e.model_dump() for e in history[-5:]],
        }
