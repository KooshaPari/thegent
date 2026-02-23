import sqlite3
import time
import json
from typing import List, Optional


class MemorySharingService:
    """Enable read-only cross-agent memory access and learning transfer tracking."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    memory_type TEXT,
                    timestamp REAL,
                    content TEXT,
                    importance REAL DEFAULT 0.5
                );
                CREATE INDEX IF NOT EXISTS idx_mem_agent ON memories(agent_id);

                CREATE TABLE IF NOT EXISTS learning_transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_memory_id TEXT NOT NULL,
                    source_agent_id TEXT NOT NULL,
                    target_agent_id TEXT NOT NULL,
                    transfer_timestamp REAL NOT NULL,
                    effectiveness REAL NOT NULL DEFAULT 0.5,
                    feedback TEXT DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_lt_source ON learning_transfers(source_agent_id);
                CREATE INDEX IF NOT EXISTS idx_lt_target ON learning_transfers(target_agent_id);
            """)

    def store_memory(self, memory_id: str, agent_id: str, memory_type: str,
                     content: dict, importance: float = 0.5, timestamp: Optional[float] = None) -> bool:
        """Helper for test setup - store a memory directly."""
        try:
            ts = timestamp or time.time()
            with self._conn:
                self._conn.execute(
                    "INSERT OR REPLACE INTO memories (id, agent_id, memory_type, timestamp, content, importance) VALUES (?, ?, ?, ?, ?, ?)",
                    (memory_id, agent_id, memory_type, ts, json.dumps(content), importance)
                )
            return True
        except Exception:
            return False

    def get_agent_learnings(self, source_agent_id: str, min_importance: float = 0.5) -> list:
        """Get learnings from an agent (memory_type LIKE '%learning%'), filtered by importance."""
        cursor = self._conn.execute(
            "SELECT * FROM memories WHERE agent_id=? AND memory_type LIKE '%learning%' AND importance >= ? ORDER BY importance DESC",
            (source_agent_id, min_importance)
        )
        rows = cursor.fetchall()
        return [{"memory_id": r["id"], "agent_id": r["agent_id"], "memory_type": r["memory_type"],
                 "timestamp": r["timestamp"], "content": json.loads(r["content"]), "importance": r["importance"]}
                for r in rows]

    def record_learning_transfer(self, source_memory_id: str, source_agent_id: str,
                                  target_agent_id: str, effectiveness: float = 0.5,
                                  feedback: str = "") -> bool:
        """Record that target_agent learned from source_agent's memory."""
        if not 0.0 <= effectiveness <= 1.0:
            raise ValueError(f"effectiveness must be 0.0-1.0, got {effectiveness}")
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO learning_transfers (source_memory_id, source_agent_id, target_agent_id, transfer_timestamp, effectiveness, feedback) VALUES (?, ?, ?, ?, ?, ?)",
                    (source_memory_id, source_agent_id, target_agent_id, time.time(), effectiveness, feedback)
                )
            return True
        except Exception:
            return False

    def get_transfer_history(self, agent_id: str, as_source: bool = True) -> list:
        """Get transfer records. as_source=True: transfers FROM agent. as_source=False: transfers TO agent."""
        col = "source_agent_id" if as_source else "target_agent_id"
        cursor = self._conn.execute(
            f"SELECT * FROM learning_transfers WHERE {col}=? ORDER BY transfer_timestamp DESC",
            (agent_id,)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_most_shared_learnings(self, limit: int = 10) -> list:
        """Return memories ordered by how many times they've been transferred."""
        cursor = self._conn.execute("""
            SELECT m.id as memory_id, m.agent_id as source_agent_id, m.content,
                   COUNT(lt.id) as transfer_count
            FROM memories m
            LEFT JOIN learning_transfers lt ON lt.source_memory_id = m.id
            GROUP BY m.id
            ORDER BY transfer_count DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [{"memory_id": r["memory_id"], "source_agent_id": r["source_agent_id"],
                 "content": json.loads(r["content"]), "transfer_count": r["transfer_count"]}
                for r in rows]

    def calculate_transfer_effectiveness(self, target_agent_id: str) -> float:
        """Average effectiveness of all transfers TO target_agent. Returns 0.0 if none."""
        cursor = self._conn.execute(
            "SELECT AVG(effectiveness) as avg_eff FROM learning_transfers WHERE target_agent_id=?",
            (target_agent_id,)
        )
        result = cursor.fetchone()
        return float(result["avg_eff"]) if result and result["avg_eff"] is not None else 0.0
