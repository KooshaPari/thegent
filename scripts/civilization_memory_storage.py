"""Phase 6a: Memory Storage Backend - SQLite and JSONL implementations.

Provides abstraction layer for memory storage with multiple backends:
- SQLiteMemoryStorage: High-performance indexed SQL backend
- JSONLMemoryStorage: Original file-based JSONL backend (fallback)
"""

import json
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import memory types from Phase 5B
try:
    from civilization_agent_memory import AgentMemory, MemoryType

    MEMORY_AVAILABLE = True
except ImportError:
    try:
        from scripts.civilization_agent_memory import AgentMemory, MemoryType

        MEMORY_AVAILABLE = True
    except ImportError:
        AgentMemory = None
        MemoryType = None
        MEMORY_AVAILABLE = False


class MemoryStorage(ABC):
    """Abstract base class for memory storage backends."""

    @abstractmethod
    def store(self, memory: "AgentMemory") -> bool:
        """Store a memory record."""

    @abstractmethod
    def query(
        self,
        agent_id: str,
        memory_type: Optional[Any] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list["AgentMemory"]:
        """Query memories with optional filters."""

    @abstractmethod
    def get_stats(self, agent_id: str) -> dict[str, Any]:
        """Get aggregated statistics for an agent."""

    @abstractmethod
    def purge_old(self, agent_id: str, ttl_seconds: int) -> int:
        """Delete old memories older than TTL."""

    @abstractmethod
    def clear(self, agent_id: str) -> bool:
        """Delete all memories for an agent."""


class SQLiteMemoryStorage(MemoryStorage):
    """SQLite-backed memory storage with indexing and full-text search."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize SQLite memory storage.

        Args:
            db_path: Path to SQLite database file.
                    If None, uses ~/.claude/civilization/memories.db
        """
        if db_path is None:
            self.db_path = Path.home() / ".claude" / "civilization" / "memories.db"
        else:
            self.db_path = db_path

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                importance REAL,
                verified BOOLEAN
            )
        """)

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON memories (agent_id, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_type ON memories (agent_id, memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories (timestamp DESC)")

        # Create memory index table for full-text search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_index (
                id INTEGER PRIMARY KEY,
                memory_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                frequency INTEGER,
                FOREIGN KEY(memory_id) REFERENCES memories(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON memory_index (keyword)")

        # Create memory relationships table (Phase 6.3)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id_1 TEXT NOT NULL,
                memory_id_2 TEXT NOT NULL,
                strength REAL NOT NULL DEFAULT 0.5,
                relationship_type TEXT NOT NULL DEFAULT 'related',
                created_at REAL NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_m1 ON memory_relationships(memory_id_1)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_m2 ON memory_relationships(memory_id_2)")

        conn.commit()
        conn.close()

    def store(self, memory: "AgentMemory") -> bool:
        """Store a memory record in SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert memory to dict
            memory_dict = asdict(memory)
            memory_type_str = (
                memory.memory_type.value if hasattr(memory.memory_type, "value") else str(memory.memory_type)
            )

            # Insert memory
            cursor.execute(
                """
                INSERT OR REPLACE INTO memories
                (id, agent_id, memory_type, timestamp, content, context, importance, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.memory_id,
                    memory.agent_id,
                    memory_type_str,
                    memory.timestamp,
                    json.dumps(memory.content),
                    json.dumps(memory.context),
                    memory.importance,
                    memory.verified,
                ),
            )

            # Index keywords from content
            self._index_memory_keywords(cursor, memory)

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing memory in SQLite: {e}")
            return False

    def _index_memory_keywords(self, cursor, memory: "AgentMemory"):
        """Extract and index keywords from memory content."""
        # Extract keywords from content
        keywords = self._extract_keywords(memory.content)

        for keyword in keywords:
            cursor.execute(
                """
                INSERT OR REPLACE INTO memory_index (memory_id, keyword, frequency)
                VALUES (?, ?, 1)
                """,
                (memory.memory_id, keyword),
            )

    def _extract_keywords(self, content: dict[str, Any]) -> list[str]:
        """Extract keywords from memory content."""
        keywords = []

        # Extract from all string values in content
        for value in content.values():
            if isinstance(value, str):
                # Simple keyword extraction: split by spaces, remove punctuation
                words = value.lower().split()
                for word in words:
                    word = word.strip(".,!?;:")
                    if len(word) > 3:  # Only keep words > 3 chars
                        keywords.append(word)

        return list(set(keywords))  # Deduplicate

    def query(
        self,
        agent_id: str,
        memory_type: Optional[Any] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list["AgentMemory"]:
        """Query memories from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build query
            sql = "SELECT * FROM memories WHERE agent_id = ?"
            params = [agent_id]

            if memory_type:
                type_str = memory_type.value if hasattr(memory_type, "value") else str(memory_type)
                sql += " AND memory_type = ?"
                params.append(type_str)

            if start_time is not None:
                sql += " AND timestamp >= ?"
                params.append(start_time)

            if end_time is not None:
                sql += " AND timestamp <= ?"
                params.append(end_time)

            sql += " ORDER BY timestamp DESC"

            if limit:
                sql += " LIMIT ?"
                params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Convert rows to AgentMemory objects
            memories = []
            for row in rows:
                (mem_id, ag_id, mem_type, ts, content_json, context_json, importance, verified) = row
                memory = AgentMemory(
                    memory_id=mem_id,
                    agent_id=ag_id,
                    memory_type=self._str_to_memory_type(mem_type),
                    timestamp=ts,
                    content=json.loads(content_json),
                    context=json.loads(context_json) if context_json else {},
                    importance=importance or 0.5,
                    verified=bool(verified),
                )
                memories.append(memory)

            conn.close()
            return memories
        except Exception as e:
            print(f"Error querying memories from SQLite: {e}")
            return []

    def _str_to_memory_type(self, type_str: str) -> Any:
        """Convert string to MemoryType enum."""
        if not MEMORY_AVAILABLE:
            return type_str

        for member in MemoryType:
            if member.value == type_str:
                return member
        return type_str

    def search(self, agent_id: str, query: str, limit: int = 10) -> list["AgentMemory"]:
        """Search memories by keywords (Phase 6 feature)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Extract keywords from query
            keywords = self._extract_keywords({"query": query})

            # Find memory IDs that match keywords
            if not keywords:
                conn.close()
                return []

            placeholders = ",".join("?" * len(keywords))
            cursor.execute(
                f"""
                SELECT DISTINCT memory_id FROM memory_index
                WHERE keyword IN ({placeholders})
                LIMIT ?
                """,
                keywords + [limit],
            )
            memory_ids = [row[0] for row in cursor.fetchall()]

            # Get full memories
            if not memory_ids:
                conn.close()
                return []

            placeholders = ",".join("?" * len(memory_ids))
            cursor.execute(
                f"""
                SELECT * FROM memories
                WHERE id IN ({placeholders})
                ORDER BY timestamp DESC
                """,
                memory_ids,
            )
            rows = cursor.fetchall()

            memories = []
            for row in rows:
                (mem_id, ag_id, mem_type, ts, content_json, context_json, importance, verified) = row
                memory = AgentMemory(
                    memory_id=mem_id,
                    agent_id=ag_id,
                    memory_type=self._str_to_memory_type(mem_type),
                    timestamp=ts,
                    content=json.loads(content_json),
                    context=json.loads(context_json) if context_json else {},
                    importance=importance or 0.5,
                    verified=bool(verified),
                )
                memories.append(memory)

            conn.close()
            return memories
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def get_stats(self, agent_id: str) -> dict[str, Any]:
        """Get statistics for an agent from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get basic stats
            cursor.execute(
                "SELECT COUNT(*) FROM memories WHERE agent_id = ?",
                (agent_id,),
            )
            total_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT memory_type, COUNT(*) FROM memories WHERE agent_id = ? GROUP BY memory_type",
                (agent_id,),
            )
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute(
                "SELECT AVG(importance) FROM memories WHERE agent_id = ?",
                (agent_id,),
            )
            avg_importance = cursor.fetchone()[0] or 0.0

            cursor.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM memories WHERE agent_id = ?",
                (agent_id,),
            )
            first_ts, last_ts = cursor.fetchone()

            # Calculate success rate
            exec_count = type_counts.get("execution", 0)
            error_count = type_counts.get("error", 0)
            success_rate = 0.0
            if exec_count > 0:
                success_rate = (exec_count - error_count) / exec_count

            stats = {
                "agent_id": agent_id,
                "total_memories": total_count,
                "memory_types": type_counts,
                "success_rate": round(success_rate, 2),
                "error_count": error_count,
                "learning_count": type_counts.get("learning", 0),
                "decision_count": type_counts.get("decision", 0),
                "milestone_count": type_counts.get("milestone", 0),
                "average_importance": round(avg_importance, 2),
                "first_memory": first_ts,
                "last_memory": last_ts,
            }

            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting stats from SQLite: {e}")
            return {
                "agent_id": agent_id,
                "total_memories": 0,
                "memory_types": {},
                "success_rate": 0.0,
                "error_count": 0,
                "learning_count": 0,
                "decision_count": 0,
                "milestone_count": 0,
                "average_importance": 0.0,
                "first_memory": None,
                "last_memory": None,
            }

    def purge_old(self, agent_id: str, ttl_seconds: int = 86400 * 30) -> int:
        """Delete old memories older than TTL."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = time.time() - ttl_seconds

            # Delete memories and their indexes
            cursor.execute(
                "SELECT id FROM memories WHERE agent_id = ? AND timestamp < ?",
                (agent_id, cutoff_time),
            )
            memory_ids = [row[0] for row in cursor.fetchall()]

            if memory_ids:
                placeholders = ",".join("?" * len(memory_ids))
                cursor.execute(f"DELETE FROM memory_index WHERE memory_id IN ({placeholders})", memory_ids)
                cursor.execute(
                    "DELETE FROM memories WHERE agent_id = ? AND timestamp < ?",
                    (agent_id, cutoff_time),
                )

            conn.commit()
            conn.close()
            return len(memory_ids)
        except Exception as e:
            print(f"Error purging old memories: {e}")
            return 0

    def clear(self, agent_id: str) -> bool:
        """Delete all memories for an agent."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete all memories and indexes for agent
            cursor.execute(
                "SELECT id FROM memories WHERE agent_id = ?",
                (agent_id,),
            )
            memory_ids = [row[0] for row in cursor.fetchall()]

            if memory_ids:
                placeholders = ",".join("?" * len(memory_ids))
                cursor.execute(f"DELETE FROM memory_index WHERE memory_id IN ({placeholders})", memory_ids)
                cursor.execute("DELETE FROM memories WHERE agent_id = ?", (agent_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False

    # Valid relationship types for link_memories
    VALID_RELATIONSHIP_TYPES = {"caused_by", "helps_with", "similar_to", "contradicts", "related"}

    def link_memories(
        self,
        memory_id_1: str,
        memory_id_2: str,
        strength: float = 0.5,
        relationship_type: str = "related",
    ) -> bool:
        """Link two memories with a typed relationship.

        Args:
            memory_id_1: First memory ID.
            memory_id_2: Second memory ID.
            strength: Relationship strength 0.0-1.0.
            relationship_type: One of caused_by, helps_with, similar_to, contradicts, related.

        Returns:
            True on success, False on error.

        Raises:
            ValueError: If strength is out of range or relationship_type is invalid.
        """
        if not (0.0 <= strength <= 1.0):
            raise ValueError(f"strength must be between 0.0 and 1.0, got {strength}")
        if relationship_type not in self.VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Invalid relationship_type '{relationship_type}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_RELATIONSHIP_TYPES))}"
            )
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memory_relationships
                (memory_id_1, memory_id_2, strength, relationship_type, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (memory_id_1, memory_id_2, strength, relationship_type, time.time()),
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error linking memories: {e}")
            return False

    def get_related_memories(self, memory_id: str, min_strength: float = 0.0) -> list[dict[str, Any]]:
        """Get memories related to a given memory.

        Args:
            memory_id: The memory ID to find relationships for.
            min_strength: Minimum relationship strength to include.

        Returns:
            List of dicts with memory_id, strength, and relationship_type,
            ordered by strength descending.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT memory_id_1, memory_id_2, strength, relationship_type
                FROM memory_relationships
                WHERE (memory_id_1 = ? OR memory_id_2 = ?)
                  AND strength >= ?
                ORDER BY strength DESC
                """,
                (memory_id, memory_id, min_strength),
            )
            rows = cursor.fetchall()
            conn.close()

            results = []
            for mid1, mid2, strength, rel_type in rows:
                other_id = mid2 if mid1 == memory_id else mid1
                results.append(
                    {
                        "memory_id": other_id,
                        "strength": strength,
                        "relationship_type": rel_type,
                    }
                )
            return results
        except Exception as e:
            print(f"Error getting related memories: {e}")
            return []

    def get_relationship_graph(self, agent_id: str) -> dict[str, Any]:
        """Get the relationship graph for all memories of an agent.

        Args:
            agent_id: The agent whose memory graph to retrieve.

        Returns:
            Dict with 'nodes' (list of memory IDs) and 'edges' (list of
            dicts with from, to, strength, type).
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all memory IDs for this agent
            cursor.execute(
                "SELECT id FROM memories WHERE agent_id = ?",
                (agent_id,),
            )
            memory_ids = [row[0] for row in cursor.fetchall()]

            if not memory_ids:
                conn.close()
                return {"nodes": [], "edges": []}

            memory_id_set = set(memory_ids)

            # Get all relationships where both ends belong to this agent
            placeholders = ",".join("?" * len(memory_ids))
            cursor.execute(
                f"""
                SELECT memory_id_1, memory_id_2, strength, relationship_type
                FROM memory_relationships
                WHERE memory_id_1 IN ({placeholders})
                  AND memory_id_2 IN ({placeholders})
                """,
                memory_ids + memory_ids,
            )
            rows = cursor.fetchall()
            conn.close()

            edges = []
            for mid1, mid2, strength, rel_type in rows:
                edges.append(
                    {
                        "from": mid1,
                        "to": mid2,
                        "strength": strength,
                        "type": rel_type,
                    }
                )

            return {"nodes": memory_ids, "edges": edges}
        except Exception as e:
            print(f"Error getting relationship graph: {e}")
            return {"nodes": [], "edges": []}


class JSONLMemoryStorage(MemoryStorage):
    """JSONL file-based memory storage (Phase 5B fallback backend)."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize JSONL memory storage.

        Args:
            base_path: Base directory for memory storage.
        """
        if base_path is None:
            self.base_path = Path.home() / ".claude" / "civilization" / "agents"
        else:
            self.base_path = base_path

        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_memory_file(self, agent_id: str) -> Path:
        """Get path to agent's memory file."""
        agent_dir = self.base_path / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir / "memory.jsonl"

    def store(self, memory: "AgentMemory") -> bool:
        """Store a memory record in JSONL."""
        try:
            memory_file = self._get_memory_file(memory.agent_id)
            with open(memory_file, "a") as f:
                memory_dict = asdict(memory)
                memory_type_str = (
                    memory.memory_type.value if hasattr(memory.memory_type, "value") else str(memory.memory_type)
                )
                memory_dict["memory_type"] = memory_type_str
                json.dump(memory_dict, f)
                f.write("\n")
            return True
        except Exception as e:
            print(f"Error storing memory in JSONL: {e}")
            return False

    def query(
        self,
        agent_id: str,
        memory_type: Optional[Any] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list["AgentMemory"]:
        """Query memories from JSONL file."""
        memory_file = self._get_memory_file(agent_id)
        if not memory_file.exists():
            return []

        memories = []
        try:
            with open(memory_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            memory_type_value = data["memory_type"]
                            for member in MemoryType:
                                if member.value == memory_type_value:
                                    data["memory_type"] = member
                                    break
                            memory = AgentMemory(**data)
                            memories.append(memory)
                        except json.JSONDecodeError, KeyError, ValueError:
                            pass
        except Exception as e:
            print(f"Error querying memories from JSONL: {e}")

        # Apply filters
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        if start_time is not None:
            memories = [m for m in memories if m.timestamp >= start_time]
        if end_time is not None:
            memories = [m for m in memories if m.timestamp <= end_time]

        memories.sort(key=lambda m: m.timestamp, reverse=True)

        if limit:
            memories = memories[:limit]

        return memories

    def search(self, agent_id: str, query: str, limit: int = 10) -> list["AgentMemory"]:
        """Search memories by content (simple text search)."""
        memories = self.query(agent_id, limit=100)
        query_lower = query.lower()

        results = []
        for memory in memories:
            # Search in content
            if any(query_lower in str(v).lower() for v in memory.content.values()):
                results.append(memory)
                if len(results) >= limit:
                    break

        return results

    def get_stats(self, agent_id: str) -> dict[str, Any]:
        """Get statistics for an agent from JSONL."""
        memories = self.query(agent_id)

        stats = {
            "agent_id": agent_id,
            "total_memories": len(memories),
            "memory_types": {},
            "success_rate": 0.0,
            "error_count": 0,
            "learning_count": 0,
            "decision_count": 0,
            "milestone_count": 0,
            "average_importance": 0.0,
            "first_memory": None,
            "last_memory": None,
        }

        if memories:
            for memory in memories:
                type_name = (
                    memory.memory_type.value if hasattr(memory.memory_type, "value") else str(memory.memory_type)
                )
                stats["memory_types"][type_name] = stats["memory_types"].get(type_name, 0) + 1

                if memory.memory_type == MemoryType.ERROR:
                    stats["error_count"] += 1
                elif memory.memory_type == MemoryType.LEARNING:
                    stats["learning_count"] += 1
                elif memory.memory_type == MemoryType.DECISION:
                    stats["decision_count"] += 1
                elif memory.memory_type == MemoryType.MILESTONE:
                    stats["milestone_count"] += 1

            avg_importance = sum(m.importance for m in memories) / len(memories)
            stats["average_importance"] = round(avg_importance, 2)

            execution_count = stats["memory_types"].get("execution", 0)
            if execution_count > 0:
                success_count = execution_count - stats["error_count"]
                stats["success_rate"] = round(success_count / execution_count, 2)

            sorted_memories = sorted(memories, key=lambda m: m.timestamp)
            stats["first_memory"] = sorted_memories[0].timestamp
            stats["last_memory"] = sorted_memories[-1].timestamp

        return stats

    def purge_old(self, agent_id: str, ttl_seconds: int = 86400 * 30) -> int:
        """Delete old memories older than TTL."""
        cutoff_time = time.time() - ttl_seconds
        memories = self.query(agent_id)

        keep_memories = [m for m in memories if m.timestamp >= cutoff_time]
        deleted_count = len(memories) - len(keep_memories)

        if deleted_count > 0:
            try:
                memory_file = self._get_memory_file(agent_id)
                with open(memory_file, "w") as f:
                    for memory in keep_memories:
                        memory_dict = asdict(memory)
                        memory_type_str = (
                            memory.memory_type.value
                            if hasattr(memory.memory_type, "value")
                            else str(memory.memory_type)
                        )
                        memory_dict["memory_type"] = memory_type_str
                        json.dump(memory_dict, f)
                        f.write("\n")
            except Exception as e:
                print(f"Error purging old memories: {e}")
                return 0

        return deleted_count

    def clear(self, agent_id: str) -> bool:
        """Delete all memories for an agent."""
        try:
            memory_file = self._get_memory_file(agent_id)
            if memory_file.exists():
                memory_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False
