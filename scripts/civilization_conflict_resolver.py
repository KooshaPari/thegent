"""Phase 5A: Conflict Resolution Protocol for Civilization Framework.

Handles duplicate agent registrations, state conflicts, and provides
multiple resolution strategies (Last-Write-Wins, Voting, Merge).
"""

import json
import time
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
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


class ConflictType(Enum):
    """Types of conflicts that can occur in the civilization framework."""

    DUPLICATE_REGISTRATION = "duplicate_registration"  # Same agent ID registered twice
    PARENT_REFERENCE_CONFLICT = "parent_reference_conflict"  # Inconsistent parent links
    CIRCULAR_DEPENDENCY = "circular_dependency"  # Circular parent-child relationships
    STATE_DIVERGENCE = "state_divergence"  # Heartbeat/state inconsistencies
    ORPHANED_REFERENCE = "orphaned_reference"  # Reference to non-existent agent


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    LAST_WRITE_WINS = "last_write_wins"  # Keep agent with latest heartbeat
    VOTING = "voting"  # Let other agents vote on winner
    MERGE = "merge"  # Combine agents' capabilities and children


@dataclass
class ConflictRecord:
    """Record of a detected and resolved conflict."""

    conflict_id: str
    conflict_type: ConflictType
    detected_at: float
    resolved_at: Optional[float] = None
    involved_agents: list[str] = field(default_factory=list)
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_winner: Optional[str] = None
    resolution_details: dict = field(default_factory=dict)
    resolved: bool = False


class ConflictResolver:
    """Detects and resolves conflicts in the civilization framework."""

    def __init__(self, registry: Optional[Any] = None):
        """Initialize conflict resolver with optional registry.

        Args:
            registry: GlobalAgentRegistry instance. If None, creates new one.
        """
        self.registry = registry
        if self.registry is None and AGENT_IDENTITY_AVAILABLE and GlobalAgentRegistry:
            self.registry = GlobalAgentRegistry()

        # Conflict log storage
        self.conflict_log_path = Path(os.path.expanduser("~/.claude/civilization/conflicts.json"))
        self.conflict_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.conflicts: list[ConflictRecord] = self._load_conflict_log()

    def _load_conflict_log(self) -> list[ConflictRecord]:
        """Load conflict log from disk."""
        if not self.conflict_log_path.exists():
            return []

        try:
            with open(self.conflict_log_path) as f:
                data = json.load(f)
                return [self._deserialize_conflict_record(item) for item in data]
        except json.JSONDecodeError, KeyError:
            return []

    def _deserialize_conflict_record(self, data: dict) -> ConflictRecord:
        """Deserialize conflict record from JSON."""
        data_copy = data.copy()
        data_copy["conflict_type"] = ConflictType[data_copy["conflict_type"]]
        if data_copy.get("resolution_strategy"):
            data_copy["resolution_strategy"] = ResolutionStrategy[data_copy["resolution_strategy"]]
        return ConflictRecord(**data_copy)

    def _save_conflict_log(self) -> None:
        """Save conflict log to disk."""
        conflict_dicts = []
        for conflict in self.conflicts:
            conflict_dict = asdict(conflict)
            conflict_dict["conflict_type"] = conflict.conflict_type.name
            if conflict.resolution_strategy:
                conflict_dict["resolution_strategy"] = conflict.resolution_strategy.name
            conflict_dicts.append(conflict_dict)

        with open(self.conflict_log_path, "w") as f:
            json.dump(conflict_dicts, f, indent=2)

    def detect_conflicts(self) -> list[ConflictRecord]:
        """Detect all conflicts in the current registry state.

        Returns:
            List of newly detected conflicts.
        """
        if not self.registry or not hasattr(self.registry, "agents"):
            return []

        new_conflicts = []

        # Check for duplicate registrations
        duplicates = self._detect_duplicate_registrations()
        for duplicate_pair in duplicates:
            conflict = ConflictRecord(
                conflict_id=f"duplicate_{int(time.time() * 1000)}",
                conflict_type=ConflictType.DUPLICATE_REGISTRATION,
                detected_at=time.time(),
                involved_agents=list(duplicate_pair),
            )
            self.conflicts.append(conflict)
            new_conflicts.append(conflict)

        # Check for parent reference conflicts
        parent_conflicts = self._detect_parent_reference_conflicts()
        for agent_id, issue in parent_conflicts:
            conflict = ConflictRecord(
                conflict_id=f"parent_{int(time.time() * 1000)}",
                conflict_type=ConflictType.PARENT_REFERENCE_CONFLICT,
                detected_at=time.time(),
                involved_agents=[agent_id],
                resolution_details={"issue": issue},
            )
            self.conflicts.append(conflict)
            new_conflicts.append(conflict)

        # Check for circular dependencies
        circular = self._detect_circular_dependencies()
        for cycle in circular:
            conflict = ConflictRecord(
                conflict_id=f"circular_{int(time.time() * 1000)}",
                conflict_type=ConflictType.CIRCULAR_DEPENDENCY,
                detected_at=time.time(),
                involved_agents=list(cycle),
            )
            self.conflicts.append(conflict)
            new_conflicts.append(conflict)

        self._save_conflict_log()
        return new_conflicts

    def _detect_duplicate_registrations(self) -> list[tuple[str, str]]:
        """Detect agents registered under different IDs.

        Returns:
            List of (agent_id1, agent_id2) pairs with duplicates.
        """
        duplicates = []
        if not self.registry or not hasattr(self.registry, "agents"):
            return duplicates

        agents = list(self.registry.agents.values())
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i + 1 :]:
                # Check if they're the same agent (same project, uuid, level, role)
                # but have different agent_ids (shouldn't happen in normal operation)
                if (
                    agent1.project == agent2.project
                    and agent1.uuid == agent2.uuid
                    and agent1.level == agent2.level
                    and agent1.role == agent2.role
                    and agent1.agent_id != agent2.agent_id
                ):
                    duplicates.append((agent1.agent_id, agent2.agent_id))

        return duplicates

    def _detect_parent_reference_conflicts(self) -> list[tuple[str, str]]:
        """Detect agents with invalid parent references.

        Returns:
            List of (agent_id, issue_description) tuples.
        """
        conflicts = []
        if not self.registry or not hasattr(self.registry, "agents"):
            return conflicts

        agents_dict = self.registry.agents
        for agent_id, agent in agents_dict.items():
            # Check if parent exists (if not root)
            if hasattr(agent, "parent_agent_id") and agent.parent_agent_id:
                if agent.parent_agent_id not in agents_dict:
                    conflicts.append((agent_id, f"Parent {agent.parent_agent_id} does not exist"))

        return conflicts

    def _detect_circular_dependencies(self) -> list[set[str]]:
        """Detect circular parent-child relationships.

        Returns:
            List of sets of agent_ids forming cycles.
        """
        cycles = []
        if not self.registry or not hasattr(self.registry, "agents"):
            return cycles

        agents_dict = self.registry.agents
        visited = set()
        rec_stack = set()

        def has_cycle(agent_id: str, path: set[str]) -> Optional[set[str]]:
            """DFS to detect cycles."""
            visited.add(agent_id)
            path.add(agent_id)

            agent = agents_dict.get(agent_id)
            if not agent:
                return None

            # Check all children
            if hasattr(agent, "child_agent_ids") and agent.child_agent_ids:
                for child_id in agent.child_agent_ids:
                    if child_id not in visited:
                        cycle = has_cycle(child_id, path.copy())
                        if cycle:
                            return cycle
                    elif child_id in path:
                        # Found a cycle
                        return path | {child_id}

            return None

        for agent_id in agents_dict:
            if agent_id not in visited:
                cycle = has_cycle(agent_id, set())
                if cycle:
                    cycles.append(cycle)

        return cycles

    def resolve_conflict(
        self,
        conflict: ConflictRecord,
        strategy: Optional[ResolutionStrategy] = None,
    ) -> Optional[ConflictRecord]:
        """Resolve a conflict using specified strategy.

        Args:
            conflict: ConflictRecord to resolve
            strategy: Resolution strategy. If None, auto-select based on type.

        Returns:
            Resolved conflict record, or None if resolution failed.
        """
        if conflict.resolved:
            return conflict

        if strategy is None:
            strategy = self._auto_select_strategy(conflict)

        try:
            if strategy == ResolutionStrategy.LAST_WRITE_WINS:
                winner = self._resolve_lww(conflict)
            elif strategy == ResolutionStrategy.VOTING:
                winner = self._resolve_voting(conflict)
            elif strategy == ResolutionStrategy.MERGE:
                winner = self._resolve_merge(conflict)
            else:
                return None

            if winner:
                conflict.resolution_strategy = strategy
                conflict.resolution_winner = winner
                conflict.resolved = True
                conflict.resolved_at = time.time()
                conflict.resolution_details["strategy"] = strategy.value
                self._save_conflict_log()
                return conflict

        except Exception as e:
            conflict.resolution_details["error"] = str(e)

        return None

    def _auto_select_strategy(self, conflict: ConflictRecord) -> ResolutionStrategy:
        """Auto-select best resolution strategy based on conflict type.

        Args:
            conflict: Conflict to select strategy for

        Returns:
            ResolutionStrategy to use
        """
        if conflict.conflict_type == ConflictType.DUPLICATE_REGISTRATION:
            return ResolutionStrategy.LAST_WRITE_WINS
        if conflict.conflict_type == ConflictType.CIRCULAR_DEPENDENCY:
            return ResolutionStrategy.MERGE
        if conflict.conflict_type == ConflictType.PARENT_REFERENCE_CONFLICT:
            return ResolutionStrategy.LAST_WRITE_WINS
        return ResolutionStrategy.LAST_WRITE_WINS

    def _resolve_lww(self, conflict: ConflictRecord) -> Optional[str]:
        """Resolve using Last-Write-Wins strategy.

        Keeps the agent with the most recent heartbeat.

        Args:
            conflict: Conflict to resolve

        Returns:
            ID of winning agent, or None
        """
        if not conflict.involved_agents or len(conflict.involved_agents) < 2:
            return None

        if not self.registry or not hasattr(self.registry, "agents"):
            return None

        agents_dict = self.registry.agents
        candidate_agents = []

        for agent_id in conflict.involved_agents:
            agent = agents_dict.get(agent_id)
            if agent and hasattr(agent, "last_heartbeat"):
                candidate_agents.append((agent_id, agent.last_heartbeat))

        if not candidate_agents:
            return None

        # Sort by heartbeat (most recent first)
        candidate_agents.sort(key=lambda x: x[1], reverse=True)
        winner = candidate_agents[0][0]
        losers = [agent_id for agent_id, _ in candidate_agents[1:]]

        # Unregister losers
        for loser_id in losers:
            try:
                self.registry.unregister_agent(loser_id)
            except Exception:
                pass

        return winner

    def _resolve_voting(self, conflict: ConflictRecord) -> Optional[str]:
        """Resolve using voting strategy (stub implementation).

        In a real implementation, this would send messages to other agents
        asking them to vote on which registration is correct.

        Args:
            conflict: Conflict to resolve

        Returns:
            ID of winning agent, or None
        """
        # For now, voting defaults to LWW
        # Real implementation would integrate with message broker
        return self._resolve_lww(conflict)

    def _resolve_merge(self, conflict: ConflictRecord) -> Optional[str]:
        """Resolve using merge strategy.

        Combines agents' capabilities and children into first agent.

        Args:
            conflict: Conflict to resolve

        Returns:
            ID of merged agent, or None
        """
        if not conflict.involved_agents or len(conflict.involved_agents) < 2:
            return None

        if not self.registry or not hasattr(self.registry, "agents"):
            return None

        agents_dict = self.registry.agents
        primary_id = conflict.involved_agents[0]
        primary_agent = agents_dict.get(primary_id)

        if not primary_agent:
            return None

        # Collect all capabilities and children
        all_children = set(primary_agent.child_agent_ids or [])
        all_capabilities = set(primary_agent.capabilities or [])
        all_scope_tags = dict(primary_agent.scope_tags or {})

        for agent_id in conflict.involved_agents[1:]:
            other_agent = agents_dict.get(agent_id)
            if other_agent:
                if hasattr(other_agent, "child_agent_ids") and other_agent.child_agent_ids:
                    all_children.update(other_agent.child_agent_ids)
                if hasattr(other_agent, "capabilities") and other_agent.capabilities:
                    all_capabilities.update(other_agent.capabilities)
                if hasattr(other_agent, "scope_tags") and other_agent.scope_tags:
                    all_scope_tags.update(other_agent.scope_tags)

                # Unregister the merged agent
                try:
                    self.registry.unregister_agent(agent_id)
                except Exception:
                    pass

        # Update primary agent with merged state
        primary_agent.child_agent_ids = list(all_children)
        primary_agent.capabilities = list(all_capabilities)
        primary_agent.scope_tags = all_scope_tags

        return primary_id

    def get_conflicts_by_agent(self, agent_id: str) -> list[ConflictRecord]:
        """Get all conflicts involving a specific agent.

        Args:
            agent_id: Agent to query

        Returns:
            List of conflicts involving this agent
        """
        return [c for c in self.conflicts if agent_id in c.involved_agents]

    def get_unresolved_conflicts(self) -> list[ConflictRecord]:
        """Get all unresolved conflicts.

        Returns:
            List of unresolved ConflictRecords
        """
        return [c for c in self.conflicts if not c.resolved]

    def get_conflicts_since(self, timestamp: float) -> list[ConflictRecord]:
        """Get all conflicts detected since a specific time.

        Args:
            timestamp: Unix timestamp

        Returns:
            List of conflicts detected after timestamp
        """
        return [c for c in self.conflicts if c.detected_at >= timestamp]

    def get_conflict_summary(self) -> dict:
        """Get summary statistics about conflicts.

        Returns:
            Dictionary with conflict counts and summaries
        """
        return {
            "total_conflicts": len(self.conflicts),
            "resolved_conflicts": len([c for c in self.conflicts if c.resolved]),
            "unresolved_conflicts": len(self.get_unresolved_conflicts()),
            "conflicts_by_type": {
                conflict_type.value: len([c for c in self.conflicts if c.conflict_type == conflict_type])
                for conflict_type in ConflictType
            },
            "resolution_strategies_used": {
                strategy.value: len([c for c in self.conflicts if c.resolution_strategy == strategy])
                for strategy in ResolutionStrategy
            },
        }
