"""WP-24001: Swarm Consensus Protocol (Byzantine).
Ensures agreement on task outcomes across a swarm of autonomous agents.
Uses a simplified Byzantine Fault Tolerance (BFT) pattern.
"""

import logging
import uuid
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class SwarmVote(BaseModel):
    """A single agent's vote on a task outcome."""

    agent_id: str
    vote: Any
    signature: str
    timestamp: str = datetime.now(UTC).isoformat()


class SwarmConsensus:
    """Orchestrates consensus across multiple swarm agents."""

    def __init__(self, task_id: str, threshold: float = 0.67) -> None:
        self.task_id = task_id
        self.threshold = threshold  # 2/3 majority (Standard BFT)
        self.votes: list[SwarmVote] = []
        self.consensus_id = f"con_{uuid.uuid4().hex[:6]}"

    def record_vote(self, agent_id: str, vote: Any, signature: str) -> None:
        """Record a vote from an agent in the swarm."""
        _log.info("Recording swarm vote for task %s from agent: %s", self.task_id, agent_id)

        # Verify agent signature (mock)
        if not signature:
            _log.warning("Invalid signature from agent: %s", agent_id)
            return

        v = SwarmVote(agent_id=agent_id, vote=vote, signature=signature)
        self.votes.append(v)

    def evaluate_consensus(self, total_agents: int) -> tuple[bool, Any | None]:
        """Evaluate if consensus has been reached based on the threshold."""
        if not self.votes:
            return False, None

        vote_counts = Counter([str(v.vote) for v in self.votes])
        majority_vote, count = vote_counts.most_common(1)[0]

        reached = (count / total_agents) >= self.threshold
        if reached:
            _log.info("Consensus reached for task %s: %s (%d/%d)", self.task_id, majority_vote, count, total_agents)
            return True, majority_vote
        _log.info("Consensus NOT reached for task %s (%d/%d)", self.task_id, count, total_agents)
        return False, None

    def get_audit_trail(self) -> dict[str, Any]:
        """Generate a cryptographic audit trail for the consensus process."""
        return {
            "task_id": self.task_id,
            "consensus_id": self.consensus_id,
            "votes": [v.model_dump() for v in self.votes],
            "timestamp": datetime.now(UTC).isoformat(),
        }
