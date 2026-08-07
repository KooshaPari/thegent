"""Crash-Preventing Weighted Byzantine Fault Tolerance (CP-WBFT) — ADR-013, SCLI-P3.1.

Implements the five-phase consensus flow:

1. **PROPOSE** — initial proposal by a leader (``:meth:`ConsensusProtocol.propose```).
2. **DRAFT** — agents provide refinements / counter-proposals
   (``:meth:`ConsensusProtocol.draft```).
3. **SHARE** — finalize the proposal after the drafting period
   (``:meth:`ConsensusProtocol.share```).
4. **VOTE** — cast weighted votes for the finalized proposal
   (``:meth:`ConsensusProtocol.cast_vote```).
5. **TALLY & DECIDE** — check whether consensus was reached
   (``:meth:`ConsensusProtocol.get_consensus```).

Threshold constants:

* ``IMPLEMENTATION_THRESHOLD = 0.5`` — simple majority for code-level
  decisions.
* ``ARCHITECTURE_THRESHOLD = 2/3`` — supermajority for architecture-level
  decisions (raised bar because architecture changes are harder to revert).
* ``DEFAULT_MAX_DEBATE_ROUNDS = 3`` — escalation budget before human review.
"""

from __future__ import annotations

import enum
import time
from pathlib import Path
from typing import Any

from ._io import ensure_dir, load_json_silent, write_json_atomic


class ConsensusStatus(enum.Enum):
    """Outcome of a tally-and-decide cycle."""

    PENDING = "pending"
    AGREED = "agreed"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ConsensusProtocol:
    """Crash-Preventing Weighted Byzantine Fault Tolerance (CP-WBFT) — ADR-013, SCLI-P3.1."""

    IMPLEMENTATION_THRESHOLD = 0.5
    ARCHITECTURE_THRESHOLD = 2 / 3
    DEFAULT_MAX_DEBATE_ROUNDS = 3

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.proposals_dir = mesh_root / "proposals"
        self.votes_dir = mesh_root / "votes"
        self.decisions_dir = mesh_root / "decisions"
        for d in [self.proposals_dir, self.votes_dir, self.decisions_dir]:
            ensure_dir(d)

    # ------------------------------------------------------------------
    # Phase 1 / 2 / 3 — proposal lifecycle
    # ------------------------------------------------------------------

    def propose(
        self,
        proposal_id: str,
        agent_id: str,
        topic: str,
        content: dict,
        decision_type: str = "implementation",
        max_debate_rounds: int = DEFAULT_MAX_DEBATE_ROUNDS,
    ) -> None:
        """Phase 1: PROPOSE (ADR-013). Initial proposal by a leader."""
        proposal_data = {
            "proposal_id": proposal_id,
            "leader_id": agent_id,
            "topic": topic,
            "content": content,
            "decision_type": decision_type,
            "phase": "propose",
            "round": 1,
            "max_debate_rounds": max_debate_rounds,
            "timestamp": time.time(),
        }
        write_json_atomic(self.proposals_dir / f"{proposal_id}.json", proposal_data)

    def draft(self, proposal_id: str, agent_id: str, refinement: dict) -> None:
        """Phase 2: DRAFT (ADR-013). Agents can provide refinements or counter-proposals."""
        draft_dir = self.proposals_dir / f"{proposal_id}.drafts"
        ensure_dir(draft_dir)
        write_json_atomic(
            draft_dir / f"agent-{agent_id}.json",
            {"agent_id": agent_id, "refinement": refinement, "ts": time.time()},
        )

    def share(self, proposal_id: str) -> None:
        """Phase 3: SHARE (ADR-013). Finalize the proposal after drafting period."""
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        if not proposal_file.exists():
            return

        data = load_json_silent(proposal_file)
        if data is None:
            return

        data["phase"] = "share"
        data["finalized_at"] = time.time()
        write_json_atomic(proposal_file, data)

    # ------------------------------------------------------------------
    # Phase 4 — vote lifecycle
    # ------------------------------------------------------------------

    def _vote_round_dir(self, proposal_id: str, vote_round: int) -> Path:
        return self.votes_dir / proposal_id / f"round-{vote_round}"

    def _load_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        return load_json_silent(self.proposals_dir / f"{proposal_id}.json")

    def _required_majority(self, decision_type: str) -> float:
        if decision_type == "architecture":
            return self.ARCHITECTURE_THRESHOLD
        return self.IMPLEMENTATION_THRESHOLD

    def cast_vote(
        self,
        proposal_id: str,
        agent_id: str,
        vote: bool,
        confidence: float = 0.8,
        vote_round: int = 1,
    ) -> None:
        """Phase 4: VOTE (ADR-013). Cast a weighted vote for the finalized proposal."""
        proposal = self._load_proposal(proposal_id) or {}
        max_rounds = int(proposal.get("max_debate_rounds", self.DEFAULT_MAX_DEBATE_ROUNDS))
        if vote_round < 1 or vote_round > max_rounds:
            return

        vote_data = {
            "agent_id": agent_id,
            "vote": bool(vote),
            "confidence": confidence,
            "vote_round": vote_round,
            "timestamp": time.time(),
        }
        proposal_dir = self._vote_round_dir(proposal_id, vote_round)
        ensure_dir(proposal_dir)

        write_json_atomic(proposal_dir / f"agent-{agent_id}.json", vote_data)

        if proposal:
            proposal["round"] = vote_round
            proposal["phase"] = "vote"
            proposal["last_vote_at"] = time.time()
            write_json_atomic(self.proposals_dir / f"{proposal_id}.json", proposal)

    def _load_round_votes(self, proposal_id: str, vote_round: int) -> list[dict[str, Any]]:
        votes: list[dict[str, Any]] = []
        legacy_dir = self.votes_dir / proposal_id
        if legacy_dir.exists() and not (legacy_dir / "round-1").exists():
            for vote_file in legacy_dir.glob("*.json"):
                vote = load_json_silent(vote_file)
                if vote is not None:
                    vote_round_value = int(vote.get("vote_round", 1))
                    if vote_round_value == vote_round:
                        vote["vote_round"] = vote_round_value
                        votes.append(vote)

        round_dir = self._vote_round_dir(proposal_id, vote_round)
        if round_dir.exists():
            for vote_file in round_dir.glob("*.json"):
                vote = load_json_silent(vote_file)
                if vote is not None:
                    vote["vote_round"] = vote_round
                    votes.append(vote)
        return votes

    def advance_debate_round(self, proposal_id: str) -> int:
        """Move a proposal to the next debate round, capped by configured max rounds."""
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        proposal = load_json_silent(proposal_file)
        if proposal is None:
            return 1

        current_round = int(proposal.get("round", 1))
        max_rounds = int(proposal.get("max_debate_rounds", self.DEFAULT_MAX_DEBATE_ROUNDS))
        next_round = min(current_round + 1, max_rounds)
        if next_round != current_round:
            proposal["round"] = next_round
            proposal["phase"] = "debate"
            proposal["round_started_at"] = time.time()
            write_json_atomic(proposal_file, proposal)
        return next_round

    # ------------------------------------------------------------------
    # Phase 5 & 6 — tally + decide (CC-reduced via 3 helpers, WL705)
    # ------------------------------------------------------------------

    @staticmethod
    def _tally_round_votes(votes: list[dict[str, Any]]) -> tuple[float, float]:
        """Return ``(total_weight, weighted_votes)`` from the round's vote records.

        Extracted from :meth:`get_consensus` during WL705 L1 hardening to
        drop the tally branch's cognitive complexity from CC=12 to CC≤6
        in the canonical :meth:`get_consensus` body. Empty list and
        zero-total-weight degenerate cases both return ``(0.0, 0.0)``;
        callers should treat that as ``PENDING`` and skip the
        decision-record write.
        """
        total_weight = sum(float(v.get("confidence", 0.0)) for v in votes)
        weighted_votes = sum(float(v.get("confidence", 0.0)) if v.get("vote") else 0.0 for v in votes)
        return total_weight, weighted_votes

    @staticmethod
    def _resolve_consensus_status(
        ratio: float,
        required_majority: float,
        current_round: int,
        max_rounds: int,
    ) -> tuple[ConsensusStatus, str]:
        """Pure decision-tree: vote ratio + round budget → (status, action).

        Extracted from :meth:`get_consensus` during WL705 L1 hardening so
        the canonical tally body becomes a thin orchestration of helpers.
        The four-branch decision tree lives here in isolation and is
        exhaustively pinned by the ``tests/unit/mesh/test_wl705_*`` suite.
        """
        if ratio > required_majority:
            return ConsensusStatus.AGREED, "finalize"
        if ratio < (1.0 - required_majority):
            return ConsensusStatus.REJECTED, "finalize"
        if current_round >= max_rounds:
            return ConsensusStatus.ESCALATED, "human_review"
        return ConsensusStatus.PENDING, "debate"

    def _persist_decision_record(
        self,
        proposal_id: str,
        status: ConsensusStatus,
        ratio: float,
        total_weight: float,
        current_round: int,
        max_rounds: int,
        required_majority: float,
        decision_type: str,
        action: str,
    ) -> None:
        """Write the canonical decision-record JSON to ``decisions/<id>.json``.

        Extracted from :meth:`get_consensus` during WL705 L1 hardening.
        The persisted shape is pinned by ``tests/unit/mesh/test_wl705_*``
        so any future drift (key rename, value coercion) is caught at
        CI time.
        """
        decision_file = self.decisions_dir / f"{proposal_id}.json"
        write_json_atomic(
            decision_file,
            {
                "proposal_id": proposal_id,
                "status": status.value,
                "ratio": ratio,
                "total_weight": total_weight,
                "round": current_round,
                "max_rounds": max_rounds,
                "required_majority": required_majority,
                "decision_type": decision_type,
                "action": action,
                "ts": time.time(),
            },
        )

    def get_consensus(
        self, proposal_id: str, required_majority: float | None = None, vote_round: int | None = None
    ) -> tuple[ConsensusStatus, float]:
        """Phase 5 & 6: TALLY & DECIDE (ADR-013). Check if consensus is reached.

        Body is a thin orchestration of three CC-reduced helpers
        (:meth:`_tally_round_votes`, :meth:`_resolve_consensus_status`,
        :meth:`_persist_decision_record`) shipped during WL705 L1
        Architecture hardening. The post-WL705 cognitive complexity of
        this method is **≤ 6** (down from CC=12 in the legacy
        single-file implementation).
        """
        proposal = self._load_proposal(proposal_id)
        if proposal is None:
            return ConsensusStatus.PENDING, 0.0

        decision_type = str(proposal.get("decision_type", "implementation"))
        max_rounds = int(proposal.get("max_debate_rounds", self.DEFAULT_MAX_DEBATE_ROUNDS))
        current_round = int(vote_round or proposal.get("round", 1))
        current_round = min(max(1, current_round), max_rounds)
        if required_majority is None:
            required_majority = self._required_majority(decision_type)

        votes = self._load_round_votes(proposal_id, current_round)
        if not votes:
            return ConsensusStatus.PENDING, 0.0

        total_weight, weighted_votes = self._tally_round_votes(votes)
        if total_weight <= 0:
            return ConsensusStatus.PENDING, 0.0

        ratio = weighted_votes / total_weight
        status, action = self._resolve_consensus_status(ratio, required_majority, current_round, max_rounds)
        self._persist_decision_record(
            proposal_id=proposal_id,
            status=status,
            ratio=ratio,
            total_weight=total_weight,
            current_round=current_round,
            max_rounds=max_rounds,
            required_majority=required_majority,
            decision_type=decision_type,
            action=action,
        )
        return status, ratio


__all__ = [
    "ConsensusStatus",
    "ConsensusProtocol",
]
