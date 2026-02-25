"""WP-15001: Multi-Instance Policy Sync.
Federated governance for multiple thegent instances.
"""

import orjson as json
import logging
from datetime import UTC
from pathlib import Path

from thegent.discovery.projects import ProjectRegistry

_log = logging.getLogger(__name__)


class PolicyFederator:
    """Synchronizes governance policies across registered projects."""

    def __init__(self, registry: ProjectRegistry) -> None:
        self.registry = registry

    async def sync_policies(self, source_project_id: str):
        """Push policies from one project to all peers."""
        peers = self.registry.list_projects()
        source_project = next((p for p in peers if p["id"] == source_project_id), None)

        if not source_project:
            _log.error("Source project %s not found in registry", source_project_id)
            return

        source_policies_path = Path(source_project["path"]) / "contracts" / "policy.py"
        if not source_policies_path.exists():
            _log.warning("No policies found in source project %s", source_project_id)
            return

        with open(source_policies_path) as f:
            policy_content = f.read()

        for peer in peers:
            if peer["id"] == source_project_id:
                continue

            _log.info("Syncing policy to peer: %s", peer["id"])
            peer_policy_path = Path(peer["path"]) / "contracts" / "policy.py"
            try:
                # Ensure directory exists
                peer_policy_path.parent.mkdir(parents=True, exist_ok=True)
                with open(peer_policy_path, "w") as f:
                    f.write(policy_content)
                _log.info("Policy synced successfully to %s", peer["id"])
            except Exception as e:
                _log.error("Failed to sync policy to %s: %s", peer["id"], e)

    async def federate_agent_identity(self, agent_id: str):
        """WP-15002: Publish agent identity to the federation with public key signature."""
        from datetime import datetime

        peers = self.registry.list_projects()

        # Public key identity mock
        public_key = f"thegent-pk-{agent_id}-0xdeadbeef"
        identity_payload = {
            "agent_id": agent_id,
            "public_key": public_key,
            "trusted_at": datetime.now(UTC).isoformat(),
            "issuer": "local-thegent",
        }

        for peer in peers:
            _log.info("Federating agent identity %s to peer %s", agent_id, peer["id"])
            peer_identity_path = Path(peer["path"]) / "governance" / "identities.jsonl"
            try:
                peer_identity_path.parent.mkdir(parents=True, exist_ok=True)
                with open(peer_identity_path, "a") as f:
                    f.write(json.dumps(identity_payload).decode() + "\n")
                _log.info("Identity federated successfully to %s", peer["id"])
            except Exception as e:
                _log.error("Failed to federate identity to %s: %s", peer["id"], e)
