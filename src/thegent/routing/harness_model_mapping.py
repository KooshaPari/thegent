"""Provider-harness-model mapping for universal parity across Codex, LiteLLM, and CLIProxy.

Ensures consistent model resolution and metadata when requests flow through:
- Codex harness (dex) -> CLIProxy adapter -> CLIProxyAPIPlus
- LiteLLM Router -> CLIProxyAPIPlus
- Direct CLIProxy API

When clode harness pairs with minimax/kilo + MiniMax-M2.5, see Minimax clode guidance:
https://platform.minimax.io/docs/coding-plan/claude-code
"""

from __future__ import annotations

# Codex/MiniMax/GLM model aliases -> CLIProxy backend (catalog) model IDs
# Used by cliproxy_adapter for request translation and /v1/models enrichment
CODEX_TO_BACKEND_MODEL: dict[str, str] = {
    # MiniMax (Codex CLI guide: codex-MiniMax-M2.5)
    "codex-MiniMax-M2.5": "minimax-m2.5",
    "codex-minimax-m2.5": "minimax-m2.5",
    "MiniMax-M2.5": "minimax-m2.5",
    # GLM
    "codex-GLM-5": "glm-5",
    "codex-glm-5": "glm-5",
    "GLM-5": "glm-5",
    # Kilo, Roo
    "codex-kilo-default": "kilo-default",
    "codex-roo-default": "roo-default",
}


def resolve_model_for_backend(model: str) -> str:
    """Map Codex/provider-specific model ID to CLIProxy backend model ID."""
    return CODEX_TO_BACKEND_MODEL.get(model, model)
