"""WP-16001/16002: Specialized teammate agents and delegation."""

import logging

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class TeammateAgent:
    """A specialized teammate agent capable of handling delegated sub-tasks."""

    def __init__(self, id: str, expertise: list[str]) -> None:
        self.id = id
        self.expertise = expertise


class TeammateManager:
    """Manages teammate discovery and task delegation."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.teammates = [
            TeammateAgent("ux-expert", ["ui", "ux", "frontend"]),
            TeammateAgent("security-auditor", ["security", "auth", "audit"]),
            TeammateAgent("ops-engineer", ["deploy", "docker", "infra"]),
        ]

    def find_specialist(self, task_description: str) -> TeammateAgent | None:
        """Find the best teammate for a task based on description."""
        for t in self.teammates:
            if any(e in task_description.lower() for e in t.expertise):
                return t
        return None

    def delegate(self, teammate_id: str, prompt: str, parent_run_id: str | None = None) -> str:
        """Delegate a task to a teammate."""
        _log.info("Delegating to %s: %s", teammate_id, prompt)
        # WP-16002: This would spawn a new AgentRunner or call an external service
        return f"run_delegated_{teammate_id}_{parent_run_id}"
