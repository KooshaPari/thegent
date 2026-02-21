"""WP-6008: Collaborative task resolution."""

import logging
from typing import Any

from thegent.config import ThegentSettings
from thegent.discovery import list_discovered_agents

_log = logging.getLogger(__name__)


class CollaborativeSession:
    """A session where multiple agents collaborate on a task."""

    def __init__(self, settings: ThegentSettings, task_id: str) -> None:
        self.settings = settings
        self.task_id = task_id
        self.participants: list[str] = []  # Agent names/IDs
        self._session_dir = settings.session_dir

    def recruit_participants(self, needed_capabilities: list[str]):
        """Recruit external agents based on capabilities (including P2P)."""
        # 1. Check local registry
        for cap in needed_capabilities:
            agents = list_discovered_agents(self._session_dir)
            matches = [a for a in agents if cap in a.get("capabilities", [])]
            if matches:
                self.participants.append(matches[0].get("agent", "unknown"))
                _log.info("Recruited local %s for capability %s", matches[0].get("agent"), cap)

        # 2. WP-13003: Decentralized P2P recruitment
        from thegent.discovery.p2p.protocol import P2PDiscovery

        # Mock P2P instance for recruitment logic
        disco = P2PDiscovery(agent_id="recruiter", port=0, capabilities=[])
        disco.start()
        import time

        time.sleep(1)  # Wait for discovery
        peers = disco.list_peers()
        disco.stop()

        for peer in peers:
            for cap in needed_capabilities:
                if cap in peer.capabilities and peer.agent_id not in self.participants:
                    self.participants.append(peer.agent_id)
                    _log.info("Recruited P2P peer %s for capability %s", peer.agent_id, cap)

    def broadcast_state(self, state: dict[str, Any]):
        """Broadcast state updates to all participants."""
        # In a real impl, this would send MCP notifications or write to shared logs
        _log.debug("Broadcasting state for task %s to %s", self.task_id, self.participants)
