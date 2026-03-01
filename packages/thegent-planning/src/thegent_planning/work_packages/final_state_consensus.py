"""WP-45003: Final State Consensus Protocol."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class FinalStateConsensusProtocol:
    """Final state consensus protocol for distributed systems."""

    def __init__(self) -> None:
        """Initialize consensus protocol."""
        self.states: dict[str, Any] = {}
        self.votes: dict[str, list[Any]] = {}

    def propose_state(self, node_id: str, state: dict[str, Any]) -> bool:
        """Propose a state.

        Args:
            node_id: Node identifier
            state: Proposed state

        Returns:
            True if proposal accepted
        """
        proposal_id = f"{node_id}_{len(self.states)}"
        self.states[proposal_id] = {
            "node": node_id,
            "state": state,
            "votes": [],
        }
        logger.info(f"Node {node_id} proposed state {proposal_id}")
        return True

    def vote(self, proposal_id: str, node_id: str, vote: bool) -> None:
        """Vote on a proposal.

        Args:
            proposal_id: Proposal identifier
            node_id: Voting node identifier
            vote: Vote (True/False)
        """
        if proposal_id not in self.states:
            logger.warning(f"Proposal {proposal_id} not found")
            return

        if proposal_id not in self.votes:
            self.votes[proposal_id] = []

        self.votes[proposal_id].append(
            {
                "node": node_id,
                "vote": vote,
            }
        )

        logger.info(f"Node {node_id} voted {vote} on {proposal_id}")

    def reach_consensus(self, proposal_id: str, threshold: float = 0.5) -> bool:
        """Check if consensus is reached.

        Args:
            proposal_id: Proposal identifier
            threshold: Consensus threshold (0.0-1.0)

        Returns:
            True if consensus reached
        """
        votes = self.votes.get(proposal_id, [])
        if not votes:
            return False

        positive_votes = sum(1 for v in votes if v["vote"])
        consensus_ratio = positive_votes / len(votes)

        reached = consensus_ratio >= threshold
        logger.info(f"Consensus on {proposal_id}: {consensus_ratio:.2%} (threshold: {threshold:.2%})")

        return reached

    def get_final_state(self, proposal_id: str) -> dict[str, Any] | None:
        """Get final consensus state.

        Args:
            proposal_id: Proposal identifier

        Returns:
            Final state or None
        """
        if proposal_id not in self.states:
            return None

        if self.reach_consensus(proposal_id):
            return self.states[proposal_id]["state"]

        return None
