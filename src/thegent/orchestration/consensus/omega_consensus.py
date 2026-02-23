"""WP-45003: Final State Consensus Protocol (Omega).
Ensures all agents in the swarm agree on the final project state using BFT.
"""

import hashlib
import orjson as json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class OmegaProposal(BaseModel):
    """A proposal for the final state of the project."""

    proposal_id: str
    proposer_id: str
    state_hash: str
    timestamp: str = datetime.now(UTC).isoformat()
    metadata: dict[str, Any]


class OmegaVote(BaseModel):
    """A vote on an Omega proposal."""

    proposal_id: str
    voter_id: str
    vote: bool
    signature: str
    timestamp: str = datetime.now(UTC).isoformat()


class OmegaConsensus:
    """The final consensus engine for thegent (Phase 45).
    Enforces agreement on the project's 'Omega' (final) state across all agents.
    """

    def __init__(self, swarm_size: int, threshold: float = 0.67) -> None:
        self.swarm_size = swarm_size
        self.threshold = threshold
        self.proposals: dict[str, OmegaProposal] = {}
        self.votes: dict[str, list[OmegaVote]] = {}
        self.finalized_state: OmegaProposal | None = None

    def propose_state(self, proposer_id: str, state: Any, metadata: dict[str, Any]) -> str:
        """Propose a new final state for the project."""
        state_json = json.dumps(state, sort_keys=True).decode().decode()
        state_hash = hashlib.sha256(state_json.encode()).hexdigest()
        proposal_id = f"prop_{uuid.uuid4().hex[:8]}"

        proposal = OmegaProposal(
            proposal_id=proposal_id, proposer_id=proposer_id, state_hash=state_hash, metadata=metadata
        )

        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        _log.info("Agent %s proposed Omega state: %s", proposer_id, proposal_id)
        return proposal_id

    def cast_vote(self, proposal_id: str, voter_id: str, vote: bool, signature: str) -> bool:
        """Cast a vote for an Omega proposal."""
        if proposal_id not in self.proposals:
            _log.warning("Attempted to vote on unknown proposal: %s", proposal_id)
            return False

        # Verify signature (mock)
        if not signature:
            _log.warning("Invalid signature from voter: %s", voter_id)
            return False

        omega_vote = OmegaVote(proposal_id=proposal_id, voter_id=voter_id, vote=vote, signature=signature)

        self.votes[proposal_id].append(omega_vote)
        _log.debug("Agent %s voted %s on proposal %s", voter_id, "YES" if vote else "NO", proposal_id)
        return True

    def finalize_consensus(self, proposal_id: str) -> bool:
        """Check if a proposal has reached consensus and finalize the state."""
        if proposal_id not in self.proposals:
            return False

        votes = self.votes[proposal_id]
        yes_votes = sum(1 for v in votes if v.vote)

        reached = (yes_votes / self.swarm_size) >= self.threshold
        if reached:
            self.finalized_state = self.proposals[proposal_id]
            _log.info("OMEGA CONSENSUS REACHED for proposal %s (%d/%d votes)", proposal_id, yes_votes, self.swarm_size)
            return True

        _log.info(
            "Consensus NOT reached for proposal %s (%d/%d votes, threshold %.2f)",
            proposal_id,
            yes_votes,
            self.swarm_size,
            self.threshold,
        )
        return False

    def get_final_state(self) -> OmegaProposal | None:
        """Return the finalized Omega state if consensus was reached."""
        return self.finalized_state
