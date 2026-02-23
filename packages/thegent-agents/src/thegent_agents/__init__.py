<<<<<<< HEAD
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
=======
"""thegent-agents: Agent runner and orchestration sub-package.

This package encapsulates agent persona definitions, the agent runner strategy
pattern, and agent lifecycle management. During the split transition (Track 4.2-4.3),
it delegates to the monolith's src/thegent/agents module.
"""

__version__ = "0.1.0"

# Public API will be expanded here as agents are split out
# Currently delegates to monolith for compatibility
>>>>>>> chore/thegent-provider-plane-pr3
