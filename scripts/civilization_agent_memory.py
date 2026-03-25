"""Phase 5B: Agent Memory Persistence for Civilization Framework.

Stores and retrieves agent execution history, decisions, and learnings.
Enables agent self-improvement and pattern recognition.
"""

import json
import time
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

# Conditional imports for agent identity system
try:
    from agent_identity_system import GlobalAgentRegistry

    AGENT_IDENTITY_AVAILABLE = True
except ImportError:
    try:
        from scripts.agent_identity_system import GlobalAgentRegistry

        AGENT_IDENTITY_AVAILABLE = True
    except ImportError:
        GlobalAgentRegistry = None
        AGENT_IDENTITY_AVAILABLE = False


class MemoryType(Enum):
    """Types of memories an agent can store."""

    EXECUTION = "execution"  # Task completion
    LEARNING = "learning"  # Pattern learned
    DECISION = "decision"  # Decision made
    ERROR = "error"  # Error encountered
    INTERACTION = "interaction"  # Agent communication
    MILESTONE = "milestone"  # Achievement


@dataclass
class AgentMemory:
    """Record of agent execution, learning, or decision."""

    memory_id: str  # Unique ID
    agent_id: str  # Agent that owns this memory
    memory_type: MemoryType  # Type of memory
    timestamp: float  # When it occurred
    content: dict[str, Any] = field(default_factory=dict)  # Main data

    # Metadata
    context: dict[str, str] = field(default_factory=dict)  # Tags, session_id, project
    importance: float = 0.5  # 0.0-1.0 (for prioritization)
    verified: bool = False  # Validated by human or peer?


class MemoryService:
    """Manages agent memory storage, retrieval, and aggregation."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize memory service with optional custom base path.

        Args:
            base_path: Base directory for memory storage.
                      If None, uses ~/.claude/civilization/agents/
        """
        if base_path is None:
            self.base_path = Path("~/.claude/civilization/agents").expanduser()
        else:
            self.base_path = base_path

        self.base_path.mkdir(parents=True, exist_ok=True)
        self.memory_cache: dict[str, list[AgentMemory]] = {}  # In-memory cache

    def _get_agent_dir(self, agent_id: str) -> Path:
        """Get directory for agent's memories.

        Args:
            agent_id: Agent ID

        Returns:
            Path to agent's memory directory
        """
        agent_dir = self.base_path / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir

    def _get_memory_file(self, agent_id: str) -> Path:
        """Get path to agent's memory file (JSONL format).

        Args:
            agent_id: Agent ID

        Returns:
            Path to memory.jsonl file
        """
        return self._get_agent_dir(agent_id) / "memory.jsonl"

    def _get_stats_file(self, agent_id: str) -> Path:
        """Get path to agent's stats file.

        Args:
            agent_id: Agent ID

        Returns:
            Path to stats.json file
        """
        return self._get_agent_dir(agent_id) / "stats.json"

    def store_memory(self, memory: AgentMemory) -> bool:
        """Store a memory record for an agent.

        Args:
            memory: AgentMemory to store

        Returns:
            True if successfully stored
        """
        try:
            memory_file = self._get_memory_file(memory.agent_id)

            # Append to JSONL file
            with open(memory_file, "a") as f:
                memory_dict = asdict(memory)
                memory_dict["memory_type"] = memory.memory_type.value
                json.dump(memory_dict, f)
                f.write("\n")

            # Update in-memory cache
            if memory.agent_id not in self.memory_cache:
                self.memory_cache[memory.agent_id] = []
            self.memory_cache[memory.agent_id].append(memory)

            # Update stats
            self._update_agent_stats(memory.agent_id, memory)

            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False

    def _load_agent_memories(self, agent_id: str) -> list[AgentMemory]:
        """Load all memories for an agent from disk.

        Args:
            agent_id: Agent ID

        Returns:
            List of AgentMemory records
        """
        if agent_id in self.memory_cache:
            return self.memory_cache[agent_id]

        memories = []
        memory_file = self._get_memory_file(agent_id)

        if not memory_file.exists():
            return memories

        try:
            with open(memory_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            # Convert memory_type value (e.g., "execution") to enum
                            memory_type_value = data["memory_type"]
                            # Find the enum member by value
                            for member in MemoryType:
                                if member.value == memory_type_value:
                                    data["memory_type"] = member
                                    break
                            memory = AgentMemory(**data)
                            memories.append(memory)
                        except json.JSONDecodeError, KeyError, ValueError:
                            pass  # Skip malformed lines

            self.memory_cache[agent_id] = memories
        except Exception as e:
            print(f"Error loading memories: {e}")

        return memories

    def query_memory(
        self,
        agent_id: str,
        memory_type: Optional[MemoryType] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[AgentMemory]:
        """Query agent memories with optional filters.

        Args:
            agent_id: Agent ID to query
            memory_type: Filter by memory type (optional)
            start_time: Filter to memories after this Unix timestamp
            end_time: Filter to memories before this Unix timestamp
            limit: Maximum number of results to return

        Returns:
            List of matching AgentMemory records
        """
        memories = self._load_agent_memories(agent_id)

        # Apply filters
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        if start_time is not None:
            memories = [m for m in memories if m.timestamp >= start_time]

        if end_time is not None:
            memories = [m for m in memories if m.timestamp <= end_time]

        # Sort by timestamp (newest first)
        memories.sort(key=lambda m: m.timestamp, reverse=True)

        # Apply limit
        if limit:
            memories = memories[:limit]

        return memories

    def _compute_fresh_stats(self, agent_id: str) -> dict[str, Any]:
        """Compute fresh statistics from all memories for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Dictionary with statistics
        """
        # Compute stats from memories
        memories = self._load_agent_memories(agent_id)

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
            # Count by type
            for memory in memories:
                type_name = memory.memory_type.value
                stats["memory_types"][type_name] = stats["memory_types"].get(type_name, 0) + 1

                # Count specific types
                if memory.memory_type == MemoryType.ERROR:
                    stats["error_count"] += 1
                elif memory.memory_type == MemoryType.LEARNING:
                    stats["learning_count"] += 1
                elif memory.memory_type == MemoryType.DECISION:
                    stats["decision_count"] += 1
                elif memory.memory_type == MemoryType.MILESTONE:
                    stats["milestone_count"] += 1

            # Calculate average importance
            avg_importance = sum(m.importance for m in memories) / len(memories)
            stats["average_importance"] = round(avg_importance, 2)

            # Calculate success rate
            execution_count = stats["memory_types"].get("execution", 0)
            if execution_count > 0:
                success_count = execution_count - stats["error_count"]
                stats["success_rate"] = round(success_count / execution_count, 2)

            # First and last timestamps
            sorted_memories = sorted(memories, key=lambda m: m.timestamp)
            stats["first_memory"] = sorted_memories[0].timestamp
            stats["last_memory"] = sorted_memories[-1].timestamp

        return stats

    def get_agent_stats(self, agent_id: str) -> dict[str, Any]:
        """Get aggregated statistics for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Dictionary with statistics
        """
        stats_file = self._get_stats_file(agent_id)

        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    return json.load(f)
            except Exception:
                pass

        # Compute fresh stats
        stats = self._compute_fresh_stats(agent_id)

        # Save stats
        self._save_stats(stats)

        return stats

    def _save_stats(self, stats: dict[str, Any]) -> None:
        """Save stats to disk.

        Args:
            stats: Statistics dictionary
        """
        try:
            stats_file = self._get_stats_file(stats["agent_id"])
            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2)
        except Exception:
            pass

    def _update_agent_stats(self, agent_id: str, memory: AgentMemory) -> None:
        """Incrementally update agent stats (faster than recomputing all).

        Args:
            agent_id: Agent ID
            memory: New memory that was added
        """
        # Load existing stats file or start with default
        stats_file = self._get_stats_file(agent_id)
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    stats = json.load(f)
            except Exception:
                # If can't read, initialize fresh
                stats = {
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
        else:
            # Start with defaults for first memory
            stats = {
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

        # Update counts
        stats["total_memories"] = stats.get("total_memories", 0) + 1
        type_name = memory.memory_type.value
        stats["memory_types"][type_name] = stats["memory_types"].get(type_name, 0) + 1

        # Update specific counts
        if memory.memory_type == MemoryType.ERROR:
            stats["error_count"] = stats.get("error_count", 0) + 1
        elif memory.memory_type == MemoryType.LEARNING:
            stats["learning_count"] = stats.get("learning_count", 0) + 1
        elif memory.memory_type == MemoryType.DECISION:
            stats["decision_count"] = stats.get("decision_count", 0) + 1
        elif memory.memory_type == MemoryType.MILESTONE:
            stats["milestone_count"] = stats.get("milestone_count", 0) + 1

        # Recalculate averages
        total_importance = (stats.get("average_importance", 0) * (stats["total_memories"] - 1)) + memory.importance
        stats["average_importance"] = round(total_importance / stats["total_memories"], 2)

        # Update timestamps
        if stats.get("last_memory") is None or memory.timestamp > stats["last_memory"]:
            stats["last_memory"] = memory.timestamp
        if stats.get("first_memory") is None or memory.timestamp < stats["first_memory"]:
            stats["first_memory"] = memory.timestamp

        # Recalculate success rate when execution or error memories change
        if memory.memory_type in (MemoryType.EXECUTION, MemoryType.ERROR):
            execution_count = stats["memory_types"].get("execution", 0)
            if execution_count > 0:
                success_count = execution_count - stats.get("error_count", 0)
                stats["success_rate"] = round(success_count / execution_count, 2)

        self._save_stats(stats)

    def purge_old_memories(
        self,
        agent_id: str,
        ttl_seconds: int = 86400 * 30,  # 30 days default
    ) -> int:
        """Delete old memories older than TTL.

        Args:
            agent_id: Agent ID
            ttl_seconds: Time-to-live in seconds

        Returns:
            Number of memories deleted
        """
        cutoff_time = time.time() - ttl_seconds
        memories = self._load_agent_memories(agent_id)

        # Filter to keep
        keep_memories = [m for m in memories if m.timestamp >= cutoff_time]
        deleted_count = len(memories) - len(keep_memories)

        # Rewrite JSONL file with kept memories
        if deleted_count > 0:
            try:
                memory_file = self._get_memory_file(agent_id)
                with open(memory_file, "w") as f:
                    for memory in keep_memories:
                        memory_dict = asdict(memory)
                        memory_dict["memory_type"] = memory.memory_type.value
                        json.dump(memory_dict, f)
                        f.write("\n")

                # Update cache
                self.memory_cache[agent_id] = keep_memories

                # Recompute stats
                self.get_agent_stats(agent_id)
            except Exception as e:
                print(f"Error purging memories: {e}")
                return 0

        return deleted_count

    def get_memories_by_importance(
        self,
        agent_id: str,
        min_importance: float = 0.5,
        limit: int = 10,
    ) -> list[AgentMemory]:
        """Get agent's most important memories.

        Args:
            agent_id: Agent ID
            min_importance: Minimum importance score (0.0-1.0)
            limit: Maximum results

        Returns:
            List of important AgentMemory records
        """
        memories = self._load_agent_memories(agent_id)

        # Filter by importance
        important = [m for m in memories if m.importance >= min_importance]

        # Sort by importance (descending) then timestamp
        important.sort(key=lambda m: (-m.importance, -m.timestamp))

        return important[:limit]

    def get_learning_summary(self, agent_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get agent's recent learnings in summarized form.

        Args:
            agent_id: Agent ID
            limit: Maximum learnings to return

        Returns:
            List of learning summaries
        """
        learnings = self.query_memory(agent_id, MemoryType.LEARNING, limit=limit)

        summaries = []
        for learning in learnings:
            summary = {
                "timestamp": learning.timestamp,
                "importance": learning.importance,
                "learning": learning.content.get("learning", "Unknown"),
                "context": learning.context.get("context", ""),
            }
            summaries.append(summary)

        return summaries

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Delete all memories for an agent (use with caution).

        Args:
            agent_id: Agent ID

        Returns:
            True if successful
        """
        try:
            agent_dir = self._get_agent_dir(agent_id)

            # Delete memory file
            memory_file = self._get_memory_file(agent_id)
            if memory_file.exists():
                memory_file.unlink()

            # Delete stats file
            stats_file = self._get_stats_file(agent_id)
            if stats_file.exists():
                stats_file.unlink()

            # Clear cache
            if agent_id in self.memory_cache:
                del self.memory_cache[agent_id]

            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False
