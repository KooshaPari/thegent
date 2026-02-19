"""Agent registry."""

from pathlib import Path

from thegent.agents.codex_proxy import CodexProxyRunner
from thegent.agents.cursor_api_runner import CursorApiRunner
from thegent.agents.direct_agents import DirectAgentRunner

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
]

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
}


def _resolve_agent(agent_name: str) -> str:
    """Resolve alias to canonical CLI name."""
    return _AGENT_ALIASES.get(agent_name, agent_name)


def get_runner(
    agent_name: str,
) -> DirectAgentRunner | CodexProxyRunner | CursorApiRunner | None:
    """Get runner for agent. Returns None for unknown."""
    canonical = _resolve_agent(agent_name)
    if canonical in _DIRECT_AGENTS:
        return DirectAgentRunner(canonical, default_model="")
    if canonical in _PROXY_AGENTS:
        return CodexProxyRunner(canonical)
    if canonical in _CURSOR_API_AGENTS:
        return CursorApiRunner()
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
