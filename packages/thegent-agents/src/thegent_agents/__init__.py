"""Thegent agents package - agent orchestration and persona management."""

# Import and re-export key components for backward compatibility
from thegent_agents.registry import AGENT_LABELS
from thegent_agents.registry import list_agent_names
from thegent_agents.registry import list_droid_names
from thegent_agents.registry import resolve_agent

__all__ = [
    "AGENT_LABELS",
    "list_agent_names",
    "list_droid_names",
    "resolve_agent",
]
