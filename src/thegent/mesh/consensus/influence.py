"""Shapley-value causal influence tracking — SCLI-P3.2.

Records per-agent contributions for a given action, then computes
per-agent Shapley-style normalised attribution when the action is
queried. Used by the mesh consensus protocol to weight votes by
historical causal influence rather than uniform confidence.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


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
            "timestamp": time.time(),
        }
        with self.influence_log.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def compute_shapley_values(self, action_id: str) -> dict[str, float]:
        """Compute per-agent causal influence using Shapley-style normalized attribution."""
        if not self.influence_log.exists():
            return {}

        totals: dict[str, float] = defaultdict(float)
        with self.influence_log.open() as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("action_id") != action_id:
                    continue
                totals[str(entry.get("agent_id", "unknown"))] += float(entry.get("contribution", 0.0))

        if not totals:
            return {}

        total_abs = sum(abs(value) for value in totals.values())
        if total_abs == 0:
            return dict.fromkeys(totals, 0.0)
        return {agent: value / total_abs for agent, value in totals.items()}


__all__ = ["CausalInfluenceTracker"]
