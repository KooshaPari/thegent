"""WP-30001: Agent Service Registry (Global).
A decentralized marketplace for agent services.
Enables agents to list capabilities and for clients to discover and bind to them.
"""

import orjson as json
import logging
from pathlib import Path

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class AgentService(BaseModel):
    """Metadata for an agent service listing."""

    service_id: str
    agent_id: str
    capability: str
    price_per_call_usd: float
    endpoint: str
    status: str = "active"
    verified: bool = False


class GlobalServiceRegistry:
    """Manages global agent service listings and discovery."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.services: dict[str, AgentService] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            for k, v in data.items():
                self.services[k] = AgentService(**v)

    def list_service(self, service: AgentService):
        """Publish a service listing to the registry."""
        _log.info("Listing new agent service: %s (%s)", service.service_id, service.capability)
        self.services[service.service_id] = service
        self._save()

    def discover_services(self, capability: str) -> list[AgentService]:
        """Find active services for a given capability."""
        return [s for s in self.services.values() if s.capability == capability and s.status == "active"]

    def run_auction(self, task_id: str, capability: str, budget: float) -> AgentService | None:
        """WP-30002: Run a reverse auction for a task requirement."""
        _log.info("Running agent auction for task %s (Cap: %s, Budget: $%.2f)", task_id, capability, budget)

        candidates = self.discover_services(capability)
        # Filter by budget
        qualified = [s for s in candidates if s.price_per_call_usd <= budget]

        if not qualified:
            _log.warning("No agents met the budget criteria for auction.")
            return None

        # Winner is the one with the lowest price (reverse auction)
        winner = min(qualified, key=lambda x: x.price_per_call_usd)
        _log.info("Auction winner for %s: %s ($%.4f)", task_id, winner.agent_id, winner.price_per_call_usd)
        return winner

    def _save(self):
        data = {k: v.model_dump() for k, v in self.services.items()}
        self.storage_path.write_bytes(json.dumps(data, option=json.OPT_INDENT_2))
