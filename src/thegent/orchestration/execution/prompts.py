"""WP-Y5: Hierarchical prompt orchestration."""

import logging
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


class PromptOrchestrator:
    """Manages hierarchical decomposition of prompts and multi-agent routing."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings

    def decompose(self, goal: str) -> list[dict[str, Any]]:
        """
        Decompose a high-level goal into a sequence of sub-tasks.
        In a real system, this would call an LLM (Decomposer Agent).
        For now, we use a simple rule-based approach for demonstration.
        """
        sub_tasks = []

        # Primitive rule-based decomposition for common patterns
        if "and" in goal and len(goal) > 50:
            parts = goal.split("and")
            for i, p in enumerate(parts):
                sub_tasks.append(
                    {
                        "id": f"task_{i + 1}",
                        "prompt": p.strip(),
                        "agent": "free",  # Default
                        "depends_on": [f"task_{i}"] if i > 0 else [],
                    }
                )
        else:
            # Atomic task
            sub_tasks.append({"id": "task_1", "prompt": goal, "agent": "free", "depends_on": []})

        return sub_tasks

    def route_subtasks(self, sub_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Assign appropriate agents to sub-tasks based on content.
        """
        for task in sub_tasks:
            prompt = task["prompt"].lower()
            if any(kw in prompt for kw in ["test", "verify", "qa"]):
                task["agent"] = "quality-agent"
            elif any(kw in prompt for kw in ["code", "implement", "create"]):
                task["agent"] = "atoms-developer"
            else:
                task["agent"] = "interactive_agent"

        return sub_tasks
