"""MAIF Artifact Store implementation for thegent."""

import orjson as json
import sqlite3
from pathlib import Path

from .artifacts import MAIFArtifact


class MAIFArtifactStore:
    """SQLite-based storage for MAIF artifacts."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database for artifacts."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    action_type TEXT,
                    payload TEXT,
                    signature TEXT,
                    timestamp TEXT,
                    agent_id TEXT,
                    session_id TEXT,
                    chain_of_thought TEXT,
                    verification_key_id TEXT,
                    previous_artifact_id TEXT
                )
                """
            )
            # Index for session retrieval
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON artifacts (session_id)")
            conn.commit()

    def store(self, artifact: MAIFArtifact) -> None:
        """Store artifact in local cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    artifact.artifact_id,
                    artifact.action_type,
                    json.dumps(artifact.payload).decode(),
                    artifact.signature,
                    artifact.timestamp,
                    artifact.agent_id,
                    artifact.session_id,
                    artifact.chain_of_thought,
                    artifact.verification_key_id,
                    artifact.previous_artifact_id,
                ),
            )
            conn.commit()

    def get(self, artifact_id: str) -> MAIFArtifact | None:
        """Retrieve artifact by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)).fetchone()
            if row:
                return self._row_to_artifact(row)
        return None

    def list_by_session(self, session_id: str) -> list[MAIFArtifact]:
        """List all artifacts for a given session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM artifacts WHERE session_id = ? ORDER BY timestamp ASC", (session_id,)
            ).fetchall()
            return [self._row_to_artifact(row) for row in rows]

    def _row_to_artifact(self, row: sqlite3.Row) -> MAIFArtifact:
        """Convert SQLite row to MAIFArtifact object."""
        data = dict(row)
        data["payload"] = json.loads(data["payload"])
        return MAIFArtifact(**data)
