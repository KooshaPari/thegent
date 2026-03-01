"""SmolGents — minimalist agent hierarchy for thegent.

Provides a lightweight agent framework for task decomposition, tool calling,
memory, and parent/child delegation.  Designed to be "smol" by design:
no heavy deps beyond the stdlib and existing thegent requirements.

Public API::

    from thegent_agents.agents.smolgents import SmolAgent, Tool, AgentTree
"""

from thegent_agents.agents.smolgents.base import SmolAgent, SmolGentJob, SmolGentResult
from thegent_agents.agents.smolgents.hierarchy import AgentTree
from thegent_agents.agents.smolgents.tools import Tool

__all__ = [
    "AgentTree",
    "SmolAgent",
    "SmolGentJob",
    "SmolGentResult",
    "Tool",
]
