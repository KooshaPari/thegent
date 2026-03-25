"""Swarm coordination and shared memory for thegent (WP-1006)."""

import orjson as json
import logging
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class ACLMessage(BaseModel):
    """WP-1006: JSON-ACL Message for inter-agent communication."""

    sender_id: str
    receiver_id: str | None = None  # None for broadcast to swarm
    performative: Literal["propose", "accept", "reject", "counter", "call-for-proposal", "request-lock"]
    content: dict[str, Any]
    conversation_id: str
    reply_with: str | None = None
    in_reply_to: str | None = None
    timestamp_us: int = Field(default_factory=lambda: 0)  # Set in constructor if needed


class Blackboard:
    """WP-1006: Shared memory for multi-agent coordination."""

    def __init__(self, namespace: str = "thegent") -> None:
        self.namespace = namespace
        # In a real impl, this would use redis-py
        self._data: dict[str, Any] = {}

    def post(self, key: str, value: Any) -> None:
        """Post a finding or result to the blackboard."""
        self._data[key] = {
            "value": value,
            "posted_at": datetime.now(UTC).isoformat(),
        }
        _log.debug("Blackboard POST: %s", key)

    def read(self, key: str) -> Any | None:
        """Read a value from the blackboard."""
        entry = self._data.get(key)
        return entry["value"] if entry else None

    def list_keys(self) -> list[str]:
        """List all keys on the blackboard."""
        return list(self._data.keys())


class ConsensusManager:
    """WP-1006: Resolves conflicts when multiple agents propose solutions."""

    @staticmethod
    def resolve_by_confidence(proposals: list[dict[str, Any]]) -> dict[str, Any]:
        """Pick the proposal with the highest confidence score."""
        if not proposals:
            raise ValueError("No proposals to resolve")

        return max(proposals, key=lambda p: p.get("confidence", 0.0))

    @staticmethod
    def resolve_by_vote(proposals: list[dict[str, Any]]) -> dict[str, Any]:
        """Majority vote on identical proposal values."""
        if not proposals:
            raise ValueError("No proposals to resolve")

        counts: dict[str, int] = {}
        proposal_map: dict[str, dict[str, Any]] = {}

        for p in proposals:
            val_str = json.dumps(p.get("value"), option=json.OPT_SORT_KEYS).decode()
            counts[val_str] = counts.get(val_str, 0) + 1
            proposal_map[val_str] = p

        winner_val = max(counts, key=lambda k: counts.get(k, 0))
        return proposal_map[winner_val]


class NegotiationEngine:
    """WP-1006: Handles inter-agent negotiation and Nash Equilibrium selection."""

    def __init__(self, blackboard: Blackboard) -> None:
        self.blackboard = blackboard

    def resolve_conflict(self, proposals: list[ACLMessage]) -> ACLMessage:
        """Find the optimal proposal using utility scores."""
        if not proposals:
            raise ValueError("No proposals to resolve")

        # Competitive Mode: pick highest utility
        # Utility = Confidence / Cost
        best_proposal = proposals[0]
        max_utility = -1.0

        for p in proposals:
            confidence = float(p.content.get("confidence", 0.5))
            cost = float(p.content.get("estimated_cost", 1.0))
            utility = confidence / max(0.01, cost)

            if utility > max_utility:
                max_utility = utility
                best_proposal = p

        return best_proposal
