"""Agent runners for thegent - re-exports from thegent-agents package."""

# Lazy import pattern to avoid circular dependencies
# The thegent-agents package is the source of truth

from typing import TYPE_CHECKING, Any, Any

if TYPE_CHECKING:
    from thegent.agents.base import AgentRunner, RunResult
    from thegent.agents.direct_agents import DirectAgentRunner
    from thegent.agents.flash_agent import FlashAgent, FlashAgentConfig, FlashAgentResult, flash
    from thegent.agents.maif_runner import MAIFAgentRunner
    from thegent.agents.registry import (
        AGENT_LABELS,
        get_fallback_agents,
        get_runner,
        list_agent_names,
        list_droid_names,
        resolve_agent,
    )
    from thegent.agents.run_options import (
        ANTHROPIC_BUDGET_TOKENS,
        CODEX_AGENTS,
        CODEX_REASONING_CONFIG_KEY,
        IMAGE_CAPABLE_AGENTS,
        ReasoningEffort,
        RunOptions,
        translate_reasoning_to_anthropic_budget,
        translate_reasoning_to_codex_config,
        translate_reasoning_to_openai_effort,
    )

# Lazy load from thegent_agents if available, otherwise fall back to local imports
_agents_module = None


def __getattr__(name: str) -> Any:
    """Lazy load attributes from thegent_agents package."""
    global _agents_module

    if _agents_module is None:
        try:
            import thegent_agents as agents

            _agents_module = agents
        except ImportError:
            # Fall back to direct import if package not installed
            return _lazy_fallback_import(name)

    if hasattr(_agents_module, name):
        return getattr(_agents_module, name)

    return _lazy_fallback_import(name)


def _lazy_fallback_import(name: str) -> Any:
    """Fallback direct imports for backward compatibility."""
    fallback_map = {
        "AGENT_LABELS": "thegent.agents.registry",
        "AgentRunner": "thegent.agents.base",
        "DirectAgentRunner": "thegent.agents.direct_agents",
        "FlashAgent": "thegent.agents.flash_agent",
        "FlashAgentConfig": "thegent.agents.flash_agent",
        "FlashAgentResult": "thegent.agents.flash_agent",
        "flash": "thegent.agents.flash_agent",
        "get_fallback_agents": "thegent.agents.registry",
        "get_runner": "thegent.agents.registry",
        "list_agent_names": "thegent.agents.registry",
        "list_droid_names": "thegent.agents.registry",
        "resolve_agent": "thegent.agents.registry",
        "MAIFAgentRunner": "thegent.agents.maif_runner",
        "RunResult": "thegent.agents.base",
        "RunOptions": "thegent.agents.run_options",
        "ReasoningEffort": "thegent.agents.run_options",
        "CODEX_AGENTS": "thegent.agents.run_options",
        "CODEX_REASONING_CONFIG_KEY": "thegent.agents.run_options",
        "ANTHROPIC_BUDGET_TOKENS": "thegent.agents.run_options",
        "IMAGE_CAPABLE_AGENTS": "thegent.agents.run_options",
        "translate_reasoning_to_codex_config": "thegent.agents.run_options",
        "translate_reasoning_to_anthropic_budget": "thegent.agents.run_options",
        "translate_reasoning_to_openai_effort": "thegent.agents.run_options",
    }

    if name in fallback_map:
        module_name = fallback_map[name]
        # Import without going through this module to avoid circular imports
        module = __import__(module_name, fromlist=[name])
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AGENT_LABELS",
    "ANTHROPIC_BUDGET_TOKENS",
    "AgentRunner",
    "CODEX_AGENTS",
    "CODEX_REASONING_CONFIG_KEY",
    "DirectAgentRunner",
    "FlashAgent",
    "FlashAgentConfig",
    "FlashAgentResult",
    "IMAGE_CAPABLE_AGENTS",
    "MAIFAgentRunner",
    "ReasoningEffort",
    "RunOptions",
    "RunResult",
    "flash",
    "get_fallback_agents",
    "get_runner",
    "list_agent_names",
    "list_droid_names",
    "resolve_agent",
    "translate_reasoning_to_anthropic_budget",
    "translate_reasoning_to_codex_config",
    "translate_reasoning_to_openai_effort",
]
