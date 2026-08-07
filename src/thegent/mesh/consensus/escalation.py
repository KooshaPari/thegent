"""5-tier escalation workflow — SCLI-P3.3 with SCLI-P3.4 async human queue.

Implements the canonical mesh escalation ladder:

* Tier 1: self
* Tier 2: peer
* Tier 3: lead
* Tier 4: committee
* Tier 5: human

When a proposal escalates beyond tier 5 (i.e. ``escalate`` is called with
``current_tier=5``) the proposal is enqueued for asynchronous human
intervention via :meth:`EscalationWorkflow._enqueue_human_escalation`,
which writes to the ``human-escalation/`` directory. The
:meth:`EscalationWorkflow.list_pending_human_escalations` and
:meth:`EscalationWorkflow.resolve_human_escalation` pair provides the
canonical operator-facing read/resolve interface for that queue.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ._io import ensure_dir, load_json_silent, write_json_atomic


class EscalationWorkflow:
    """5-tier escalation workflow (SCLI-P3.3)."""

    def __init__(self, mesh_root: Path) -> None:
        self.mesh_root = mesh_root
        self.escalation_queue = mesh_root / "escalation-queue"
        self.human_escalation = mesh_root / "human-escalation"
        self.tiers = {
            1: "self",
            2: "peer",
            3: "lead",
            4: "committee",
            5: "human",
        }
        ensure_dir(self.escalation_queue)
        ensure_dir(self.human_escalation)

    def _next_tier(self, current_tier: int) -> int:
        return 5 if current_tier >= 5 else current_tier + 1

    def escalate(
        self,
        proposal_id: str,
        current_tier: int = 1,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Escalate to next tier (SCLI-P3.3).

        Returns ``True`` whether the escalation was recorded as a tier-N
        transition (1 → 2 → … → 5) or enqueued for human intervention
        (tier 5 → human queue). The canonical SCLI-P3.4 path is triggered
        when ``current_tier >= 5`` at call time.
        """
        next_tier = self._next_tier(current_tier)
        if current_tier >= 5:
            # Enqueue for human intervention (SCLI-P3.4).
            self._enqueue_human_escalation(proposal_id, reason=reason, metadata=metadata)
            return True

        escalation_data = {
            "proposal_id": proposal_id,
            "from_tier": current_tier,
            "to_tier": next_tier,
            "from_label": self.tiers.get(current_tier, "unknown"),
            "to_label": self.tiers.get(next_tier, "unknown"),
            "reason": reason,
            "metadata": metadata or {},
            "status": "pending",
            "timestamp": time.time(),
        }
        write_json_atomic(
            self.escalation_queue / f"escalation-{proposal_id}.json",
            escalation_data,
        )
        return True

    def _enqueue_human_escalation(
        self, proposal_id: str, reason: str = "", metadata: dict[str, Any] | None = None
    ) -> None:
        """SCLI-P3.4 Async human escalation queue."""
        write_json_atomic(
            self.human_escalation / f"human-{proposal_id}.json",
            {
                "proposal_id": proposal_id,
                "reason": reason,
                "status": "pending",
                "metadata": metadata or {},
                "timestamp": time.time(),
            },
        )

    def list_pending_human_escalations(self) -> list[dict[str, Any]]:
        """List pending asynchronous human escalations (SCLI-P3.4)."""
        pending: list[dict[str, Any]] = []
        for item_path in self.human_escalation.glob("*.json"):
            item = load_json_silent(item_path)
            if item is not None and item.get("status") == "pending":
                pending.append(item)
        pending.sort(key=lambda item: float(item.get("timestamp", 0.0)))
        return pending

    def resolve_human_escalation(self, proposal_id: str, status: str = "resolved") -> bool:
        """Resolve a queued human escalation item."""
        item_path = self.human_escalation / f"human-{proposal_id}.json"
        item = load_json_silent(item_path)
        if item is None:
            return False

        item["status"] = status
        item["resolved_at"] = time.time()
        write_json_atomic(item_path, item)
        return True


__all__ = ["EscalationWorkflow"]
