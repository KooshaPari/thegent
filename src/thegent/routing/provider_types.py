"""Provider type classification for execution path routing."""

from enum import Enum, auto
from typing import Final


class ExecutionPath(Enum):
    """Execution path for LLM provider."""

    NATIVE_CLI = auto()  # codex, claude, opencode (interactive/agent harness)
    LITELLM_API = auto()  # minimax, nim, glm, kilo, zen (API keys)
    CLIPROXY_API = auto()  # LOGIN-auth providers via CLIProxyAPIPlus


# Immutable provider classifications
NATIVE_CLI_PROVIDERS: Final[frozenset[str]] = frozenset({"codex", "claude", "opencode"})
API_KEY_PROVIDERS: Final[frozenset[str]] = frozenset({"minimax", "nim", "glm", "kilo", "zen", "openrouter", "ollama"})
LOGIN_AUTH_PROVIDERS: Final[frozenset[str]] = frozenset({"antigravity", "cursor", "kiro", "gemini", "copilot"})

_PROVIDER_ALIASES: Final[dict[str, str]] = {
    "ollama-local": "ollama",
    "local-ollama": "ollama",
    "ollama-localhost": "ollama",
    "ollama@localhost": "ollama",
}


def normalize_provider_name(provider: str) -> str:
    """Normalize provider aliases into canonical routing names."""
    value = (provider or "").strip().lower()
    return _PROVIDER_ALIASES.get(value, value)


def get_execution_path(provider: str) -> ExecutionPath:
    """Determine execution path for a provider.

    Args:
        provider: Provider name (e.g., "codex", "minimax", "antigravity")

    Returns:
        ExecutionPath enum value
    """
    normalized = normalize_provider_name(provider)
    if normalized in NATIVE_CLI_PROVIDERS:
        return ExecutionPath.NATIVE_CLI
    if normalized in API_KEY_PROVIDERS:
        return ExecutionPath.LITELLM_API
    return ExecutionPath.CLIPROXY_API
