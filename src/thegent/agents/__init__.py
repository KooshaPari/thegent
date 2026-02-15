"""Agent runners for thegent."""

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.direct_agents import DirectAgentRunner
from thegent.agents.registry import (
    get_fallback_agents,
    get_runner,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)

__all__ = [
    "AgentRunner",
    "DirectAgentRunner",
    "RunResult",
    "get_fallback_agents",
    "get_runner",
    "list_agent_names",
    "list_droid_names",
    "resolve_agent",
]
