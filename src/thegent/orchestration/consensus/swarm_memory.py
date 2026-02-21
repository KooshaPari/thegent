"""WP-24003: Swarm Memory Consolidation.
Consolidates distributed agent memories into a unified swarm knowledge base.
Uses cross-agent memory synthesis to eliminate redundancy and conflicts.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from thegent.orchestration.state.memory import MemorySystem

_log = logging.getLogger(__name__)


class SwarmMemoryConsolidator:
    """Synthesizes memory artifacts from multiple agents into a unified view."""

    def __init__(self, swarm_id: str, local_memory: MemorySystem) -> None:
        self.swarm_id = swarm_id
        self.local_memory = local_memory
        self.consolidated_path = f"swarm_memory_{swarm_id}.json"

    def consolidate(self, peer_memories: list[dict[str, Any]]) -> dict[str, Any]:
        """Consolidate peer memories with local memory."""
        _log.info("Consolidating swarm memory for: %s", self.swarm_id)

        unified_artifacts = {}

        # 1. Start with local fragments
        for fragment in self.local_memory.get_recent(limit=500):
            unified_artifacts[fragment.id] = {
                "id": fragment.id,
                "timestamp": fragment.timestamp,
                "content": fragment.content,
                "category": fragment.category,
                "agent": fragment.source_agent,
            }

        # 2. Merge peer artifacts
        for peer_mem in peer_memories:
            peer_id = peer_mem.get("agent_id", "unknown")
            artifacts = peer_mem.get("artifacts", [])

            for art in artifacts:
                art_id = art["id"]
                if art_id in unified_artifacts:
                    _log.debug("Conflict detected for artifact %s from %s. Using latest.", art_id, peer_id)
                    # Simplified resolution: keep newer timestamp
                    if art["timestamp"] > unified_artifacts[art_id]["timestamp"]:
                        unified_artifacts[art_id] = art
                else:
                    unified_artifacts[art_id] = art

        _log.info("Consolidated %d artifacts for swarm %s", len(unified_artifacts), self.swarm_id)

        return {
            "swarm_id": self.swarm_id,
            "consolidated_at": datetime.now(UTC).isoformat(),
            "artifact_count": len(unified_artifacts),
            "artifacts": list(unified_artifacts.values()),
        }
