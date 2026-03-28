"""WP-4003: One-click safe fallback options."""

import logging

from thegent_core.config import ThegentSettings

_log = logging.getLogger(__name__)


class FallbackOption:
    """A safe fallback action for the operator."""

    def __init__(self, id: str, label: str, description: str, command: str) -> None:
        self.id = id
        self.label = label
        self.description = description
        self.command = command


class FallbackRegistry:
    """Registry of safe fallback options based on failure context."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.options = [
            FallbackOption(
                "retry_standard", "Retry Standard", "Retry with standard timeout and lane", "thegent retry {run_id}"
            ),
            FallbackOption(
                "retry_critical",
                "Escalate to Critical",
                "Retry in critical lane with higher priority",
                "thegent retry {run_id} --lane critical",
            ),
            FallbackOption(
                "rollback_checkpoint", "Rollback DAG", "Rollback to last stable checkpoint", "thegent plan rollback"
            ),
            FallbackOption(
                "human_takeover",
                "Human Takeover",
                "Attach to session for manual intervention",
                "thegent takeover {run_id}",
            ),
            FallbackOption(
                "switch_agent",
                "Switch Agent",
                "Retry with a different provider",
                "thegent retry {run_id} --agent gemini",
            ),
        ]

    def get_recommendations(self, failure_kind: str) -> list[FallbackOption]:
        """Return recommended fallback options based on failure type."""
        if failure_kind == "usage_limit":
            return [o for o in self.options if o.id in ["switch_agent", "human_takeover"]]
        if failure_kind == "timeout":
            return [o for o in self.options if o.id in ["retry_critical", "human_takeover"]]
        if failure_kind == "logic_error":
            return [o for o in self.options if o.id in ["rollback_checkpoint", "human_takeover"]]

        return self.options[:2]  # Default recommendations
