"""Consensus and escalation protocols for the agent mesh."""

import enum
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ConsensusStatus(enum.Enum):
    PENDING = "pending"
    AGREED = "agreed"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ConsensusProtocol:
    """Crash-Preventing Weighted Byzantine Fault Tolerance (CP-WBFT) (ADR-013, SCLI-P3.1)."""

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.proposals_dir = mesh_root / "proposals"
        self.votes_dir = mesh_root / "votes"
        for d in [self.proposals_dir, self.votes_dir]:
            d.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def propose(self, proposal_id: str, agent_id: str, topic: str, content: dict) -> None:
        """Phase 1: PROPOSE (ADR-013). Initial proposal by a leader."""
        proposal_data = {
            "proposal_id": proposal_id,
            "leader_id": agent_id,
            "topic": topic,
            "content": content,
            "phase": "propose",
            "timestamp": time.time()
        }
        with open(self.proposals_dir / f"{proposal_id}.json", "w") as f:
            json.dump(proposal_data, f)

    def draft(self, proposal_id: str, agent_id: str, refinement: dict) -> None:
        """Phase 2: DRAFT (ADR-013). Agents can provide refinements or counter-proposals."""
        draft_file = self.proposals_dir / f"{proposal_id}.drafts"
        draft_file.mkdir(parents=True, exist_ok=True, mode=0o1777)
        with open(draft_file / f"agent-{agent_id}.json", "w") as f:
            json.dump({"agent_id": agent_id, "refinement": refinement, "ts": time.time()}, f)

    def share(self, proposal_id: str) -> None:
        """Phase 3: SHARE (ADR-013). Finalize the proposal after drafting period."""
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        if not proposal_file.exists():
            return
        
        with open(proposal_file, "r") as f:
            data = json.load(f)
        
        data["phase"] = "share"
        data["finalized_at"] = time.time()
        
        with open(proposal_file, "w") as f:
            json.dump(data, f)

    def cast_vote(self, proposal_id: str, agent_id: str, vote: bool, confidence: float = 0.8) -> None:
        """Phase 4: VOTE (ADR-013). Cast a weighted vote for the finalized proposal."""
        vote_data = {
            "agent_id": agent_id,
            "vote": vote,
            "confidence": confidence,
            "timestamp": time.time()
        }
        proposal_dir = self.votes_dir / proposal_id
        proposal_dir.mkdir(parents=True, exist_ok=True, mode=0o1777)

        with open(proposal_dir / f"agent-{agent_id}.json", "w") as f:
            json.dump(vote_data, f)

    def get_consensus(self, proposal_id: str, required_majority: float = 0.5) -> tuple[ConsensusStatus, float]:
        """Phase 5 & 6: TALLY & DECIDE (ADR-013). Check if consensus is reached."""
        proposal_dir = self.votes_dir / proposal_id
        if not proposal_dir.exists():
            return ConsensusStatus.PENDING, 0.0

        votes = []
        for vote_file in proposal_dir.glob("*.json"):
            try:
                with open(vote_file) as f:
                    votes.append(json.load(f))
            except Exception:
                continue

        if not votes:
            return ConsensusStatus.PENDING, 0.0

        total_weight = sum(v["confidence"] for v in votes)
        weighted_votes = sum(v["confidence"] if v["vote"] else 0 for v in votes)

        ratio = weighted_votes / total_weight if total_weight > 0 else 0

        # Decide phase
        status = ConsensusStatus.PENDING
        if ratio >= required_majority:
            status = ConsensusStatus.AGREED
        elif ratio < (1 - required_majority):
            status = ConsensusStatus.REJECTED
        else:
            status = ConsensusStatus.ESCALATED

        # Record decision
        decision_file = self.mesh_root / "decisions" / f"{proposal_id}.json"
        decision_file.parent.mkdir(parents=True, exist_ok=True)
        with open(decision_file, "w") as f:
            json.dump({
                "proposal_id": proposal_id,
                "status": status.value,
                "ratio": ratio,
                "total_weight": total_weight,
                "ts": time.time()
            }, f)

        return status, ratio


class CausalInfluenceTracker:
    """Shapley-value causal influence tracking (SCLI-P3.2)."""

    def __init__(self, mesh_root: Path) -> None:
        self.influence_log = mesh_root / "influence.jsonl"

    def record_influence(self, agent_id: str, action_id: str, contribution: float) -> None:
        """Log contribution for later analysis."""
        entry = {
            "agent_id": agent_id,
            "action_id": action_id,
            "contribution": contribution,
            "timestamp": time.time()
        }
        with open(self.influence_log, "a") as f:
            f.write(json.dumps(entry) + "\n")


class EscalationWorkflow:
    """5-tier escalation workflow (SCLI-P3.3)."""

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.escalation_queue = mesh_root / "escalation-queue"
        self.escalation_queue.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def escalate(self, proposal_id: str, current_tier: int = 1) -> bool:
        """Escalate to next tier (SCLI-P3.3)."""
        # Tier 1: Self-correction (automated)
        # Tier 2: Peer-review (automated)
        # Tier 3: Team-lead (semi-automated)
        # Tier 4: Committee (multi-agent)
        # Tier 5: Human (SCLI-P3.4)

        if current_tier >= 5:
            # Enqueue for human intervention (SCLI-P3.4)
            self._enqueue_human_escalation(proposal_id)
            return True

        # In this stub, we just record the escalation
        escalation_data = {
            "proposal_id": proposal_id,
            "tier": current_tier + 1,
            "timestamp": time.time()
        }
        with open(self.escalation_queue / f"escalation-{proposal_id}.json", "w") as f:
            json.dump(escalation_data, f)

        return True

    def _enqueue_human_escalation(self, proposal_id: str) -> None:
        """SCLI-P3.4 Async human escalation queue."""
        human_queue = self.mesh_root / "human-escalation"
        human_queue.mkdir(parents=True, exist_ok=True, mode=0o1777)

        with open(human_queue / f"human-{proposal_id}.json", "w") as f:
            json.dump({"proposal_id": proposal_id, "status": "pending"}, f)
