"""Agent runners for thegent."""

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.direct_agents import DirectAgentRunner
from thegent.agents.flash_agent import FlashAgent, FlashAgentConfig, FlashAgentResult, flash
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
    "FlashAgent",
    "FlashAgentConfig",
    "FlashAgentResult",
    "MAIFAgentRunner",
    "RunResult",
    "flash",
    "get_fallback_agents",
    "get_runner",
    "list_agent_names",
    "list_droid_names",
    "resolve_agent",
]

from thegent.agents.maif_runner import MAIFAgentRunner
