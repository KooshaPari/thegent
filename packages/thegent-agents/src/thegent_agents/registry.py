"""Agent registry.

Phase 2C DI migration
---------------------
The module-level functions (get_runner, get_fallback_agents, etc.) are
retained for backward compatibility but are now also available as methods
on the injectable ``AgentRegistry`` class.

A module-level ``_registry`` singleton is provided via ``get_agent_registry()``
so new code can depend on an injected AgentRegistry while old call sites
continue to work without modification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from thegent_agents.codex_proxy import CodexProxyRunner
from thegent_agents.cursor_api_runner import CursorApiRunner
from thegent_agents.direct_agents import DirectAgentRunner

if TYPE_CHECKING:
    from thegent_agents.teammate_runner import TeammateRunner

AGENT_NAMES = [
    "gemini",
    "codex",
    "copilot",
    "opencode",
    "cursor-agent",
    "cursor-api",
    "claude",
    "antigravity",
    "minimax",
    "glm",
    "zen",
    "cliproxy",
    "roo",
    "kilo",
    "summarizer",
]

_logger = logging.getLogger(__name__)

# Agents with native CLIs - use DirectAgentRunner (no proxy required)
# Note: gemini, copilot, claude, codex can have issues; use antigravity/minimax/etc via proxy instead
_DIRECT_AGENTS = frozenset({"cursor-agent", "opencode"})
# Agents that run via CLIProxyAPIPlus (antigravity, minimax, glm, cliproxy, roo, kilo use same backend)
# codex, claude, copilot, gemini moved here for reliability via proxy
_PROXY_AGENTS = frozenset(
    {"antigravity", "minimax", "glm", "zen", "cliproxy", "roo", "kilo", "codex", "claude", "copilot", "gemini"}
)
# Cursor via cursor-api (wisdgod) - OpenAI-compat HTTP backend
_CURSOR_API_AGENTS = frozenset({"cursor-api"})

# Fallback chain when provider hits usage limit (subscription/quota exhausted).
# Order: try next provider in list. Using proxy-based agents for reliability.
_PROVIDER_FALLBACK_CHAIN: list[list[str]] = [
    ["glm", "zen", "minimax", "antigravity", "cliproxy", "roo", "kilo"],
    ["minimax", "glm", "antigravity", "cliproxy", "roo", "kilo"],
    ["zen", "glm", "minimax", "antigravity", "cliproxy", "roo", "kilo"],
    ["antigravity", "minimax", "glm", "cliproxy", "roo", "kilo"],
    ["cliproxy", "antigravity", "minimax", "glm", "roo", "kilo"],
    ["roo", "kilo", "cliproxy", "antigravity", "minimax", "glm"],
    ["kilo", "roo", "cliproxy", "antigravity", "minimax", "glm"],
    # Native CLIs now use proxy - fallback to proxy agents instead
    ["gemini", "antigravity", "minimax", "glm"],
    ["codex", "antigravity", "minimax", "glm"],
    ["copilot", "antigravity", "minimax", "glm"],
    ["claude", "antigravity", "minimax", "glm"],
    ["cursor-agent", "antigravity", "minimax", "glm"],
    ["cursor-api", "antigravity", "minimax", "glm"],
]

# Label (display/metadata) -> CLI name. Frontmatter/agent_hint use label; run/bg use CLI name.
AGENT_LABELS: dict[str, str] = {"cursor-agent": "cursor", "cursor-api": "cursor-api"}

# Alias (label) -> canonical CLI name.
_AGENT_ALIASES: dict[str, str] = {
    "cursor": "cursor-agent",
    "oc": "opencode",
    "free": "copilot",
    "summarize": "gemini",
    "research": "claude",
    "review": "claude",
    "explain": "gemini",
    "fix": "claude",
    "code": "claude",
    "architect": "claude",
}


def _resolve_agent(agent_name: str) -> str:
    """Resolve alias to canonical CLI name."""
    return _AGENT_ALIASES.get(agent_name, agent_name)


def get_runner(
    agent_name: str,
) -> DirectAgentRunner | CodexProxyRunner | CursorApiRunner | TeammateRunner | None:
    """Get runner for agent. Returns None for unknown."""
    canonical = _resolve_agent(agent_name)
    if canonical in _DIRECT_AGENTS:
        return DirectAgentRunner(canonical, default_model="")
    if canonical in _PROXY_AGENTS or canonical == "summarizer":
        return CodexProxyRunner(canonical)
    if canonical in _CURSOR_API_AGENTS:
        return CursorApiRunner()

    # WP-16001: Support teammates
    from thegent_agents.teammate_runner import TeammateRunner

    try:
        return TeammateRunner(agent_name)
    except ValueError as exc:
        _logger.debug("No teammate found for '%s': %s", agent_name, exc)
        return None
    except Exception as exc:
        raise RuntimeError(f"Failed to create teammate runner for '{agent_name}'") from exc

    return None


def get_fallback_agents(agent_name: str) -> list[str]:
    """Return fallback agents when this provider hits usage limit. Excludes current agent."""
    canonical = _resolve_agent(agent_name)
    for chain in _PROVIDER_FALLBACK_CHAIN:
        if chain and chain[0] == canonical:
            return [a for a in chain[1:] if a != canonical]
    return []


def resolve_agent(agent_name: str | None) -> str | None:
    """Resolve label/alias to canonical CLI name. E.g. 'cursor' -> 'cursor-agent'."""
    if agent_name is None:
        return None
    return _AGENT_ALIASES.get(agent_name, agent_name)


def list_agent_names() -> list[str]:
    """List available agent names (canonical CLI names)."""
    return list(AGENT_NAMES)


def list_droid_names(droids_dir: Path) -> list[str]:
    """List available droid names from .md files (legacy; droids disabled)."""
    d = droids_dir.expanduser().resolve()
    if not d.exists():
        return []
    return [f.stem for f in d.glob("*.md")]


class AgentRegistry:
    """Injectable registry for agent runner resolution.

    Encapsulates the formerly module-level ``get_runner`` / ``get_fallback_agents``
    functions so callers can depend on an AgentRegistry instance that can be
    swapped out in tests without touching global state.

    Attributes:
        direct_agents: Frozenset of agent names that use DirectAgentRunner.
        proxy_agents: Frozenset of agent names that use CodexProxyRunner.
        cursor_api_agents: Frozenset of agents that use CursorApiRunner.
        aliases: Alias → canonical name mapping.
        fallback_chain: Provider fallback chains.
    """

    def __init__(
        self,
        *,
        direct_agents: frozenset[str] = _DIRECT_AGENTS,
        proxy_agents: frozenset[str] = _PROXY_AGENTS,
        cursor_api_agents: frozenset[str] = _CURSOR_API_AGENTS,
        aliases: dict[str, str] | None = None,
        fallback_chain: list[list[str]] | None = None,
    ) -> None:
        self.direct_agents = direct_agents
        self.proxy_agents = proxy_agents
        self.cursor_api_agents = cursor_api_agents
        self.aliases: dict[str, str] = aliases if aliases is not None else dict(_AGENT_ALIASES)
        self.fallback_chain: list[list[str]] = (
            fallback_chain if fallback_chain is not None else list(_PROVIDER_FALLBACK_CHAIN)
        )

    def resolve_name(self, agent_name: str) -> str:
        """Resolve alias to canonical CLI name."""
        return self.aliases.get(agent_name, agent_name)

    def get_runner(
        self,
        agent_name: str,
    ) -> DirectAgentRunner | CodexProxyRunner | CursorApiRunner | Any | None:
        """Get runner for agent.  Returns None for unknown agents."""
        canonical = self.resolve_name(agent_name)
        if canonical in self.direct_agents:
            return DirectAgentRunner(canonical, default_model="")
        if canonical in self.proxy_agents or canonical == "summarizer":
            return CodexProxyRunner(canonical)
        if canonical in self.cursor_api_agents:
            return CursorApiRunner()

        # Support teammates (lazy import to avoid circular deps)
        from thegent_agents.teammate_runner import TeammateRunner  # type: ignore[import]

        try:
            return TeammateRunner(agent_name)
        except ValueError as exc:
            _logger.debug("No teammate found for '%s': %s", agent_name, exc)
            return None
        except Exception as exc:
            raise RuntimeError(f"Failed to create teammate runner for '{agent_name}'") from exc

    def get_fallback_agents(self, agent_name: str) -> list[str]:
        """Return fallback agents when *agent_name*'s provider hits a usage limit."""
        canonical = self.resolve_name(agent_name)
        for chain in self.fallback_chain:
            if chain and chain[0] == canonical:
                return [a for a in chain[1:] if a != canonical]
        return []

    def list_agent_names(self) -> list[str]:
        """Return all known agent names."""
        return list(AGENT_NAMES)


# ---------------------------------------------------------------------------
# Module-level singleton — backward-compat shim
# ---------------------------------------------------------------------------

#: Module-level AgentRegistry instance.
_registry: AgentRegistry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Return the module-level AgentRegistry singleton."""
    return _registry


def set_agent_registry(registry: AgentRegistry) -> None:
    """Replace the module-level AgentRegistry singleton (for testing)."""
    global _registry
    _registry = registry


class LearningCandidate:
    """Represents a candidate model or configuration for autonomous learning."""

    def __init__(self, model_id: str, baseline_id: str) -> None:
        self.model_id = model_id
        self.baseline_id = baseline_id
        self.trust_score = 0.0
        self.calibration = 0.0
        self.metrics: dict[str, list[float]] = {}

    def add_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)


class LearningRegistry:
    """Registry for autonomous learning models and metrics (WP-14001)."""

    def __init__(self) -> None:
        self.canaries: dict[str, LearningCandidate] = {}
        self.active_model: str = "baseline-v1"

    def register_canary(self, canary_id: str, baseline_id: str):
        """Register a new canary model for testing."""
        self.canaries[canary_id] = LearningCandidate(canary_id, baseline_id)

    def record_metric(self, model_id: str, name: str, value: float):
        """Record a performance metric for a model."""
        if model_id in self.canaries:
            self.canaries[model_id].add_metric(name, value)

    def should_rollback(self, canary_id: str) -> bool:
        """Determine if a canary model should be rolled back to baseline."""
        candidate = self.canaries.get(canary_id)
        if not candidate:
            return False

        # Simple heuristic: if any latency > 2s, rollback
        latencies = candidate.metrics.get("latency", [])
        if latencies and any(lat > 2.0 for lat in latencies):
            self.active_model = candidate.baseline_id
            return True
        return False

    def get_active_model(self) -> str:
        """Get the currently active model ID."""
        return self.active_model

    def promote(self, canary_id: str, require_approval: bool = True) -> bool:
        """Promote a canary model to default status."""
        if require_approval:
            # In a real impl, this would check a HITL signal
            return False

        if canary_id in self.canaries:
            self.active_model = canary_id
            return True
        return False

    def record_feedback(self, model_id: str, success: bool, quality_score: float):
        """Record human or system feedback for a learning candidate."""
        candidate = self.canaries.get(model_id)
        if candidate:
            candidate.trust_score += 0.1 if success else -0.2
            candidate.calibration = (candidate.calibration + quality_score) / 2.0

    def get_candidate(self, model_id: str) -> LearningCandidate | None:
        """Get candidate metadata."""
        return self.canaries.get(model_id)
