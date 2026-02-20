"""Model metadata registry for all models."""

from typing import Any

# Comprehensive model metadata registry
MODEL_METADATA: dict[str, dict[str, Any]] = {
    # Anthropic Claude
    "claude-haiku-4.5": {
        "context_window": 200000,
        "cost_per_mtok": 0.50,
        "provider": "claude",
        "backend": "direct",
    },
    "claude-sonnet-4.5": {
        "context_window": 200000,
        "cost_per_mtok": 3.00,
        "provider": "claude",
        "backend": "direct",
    },
    "claude-sonnet-4.6": {
        "context_window": 200000,
        "cost_per_mtok": 3.00,
        "provider": "claude",
        "backend": "direct",
    },
    "claude-opus-4.6": {
        "context_window": 200000,
        "cost_per_mtok": 15.00,
        "provider": "claude",
        "backend": "direct",
    },
    "claude-opus-4.6-1m": {
        "context_window": 1000000,
        "cost_per_mtok": 18.00,
        "provider": "claude",
        "backend": "direct",
    },
    # Google Gemini
    "gemini-2.0-flash": {
        "context_window": 1000000,
        "cost_per_mtok": 0.15,
        "provider": "gemini",
        "backend": "direct",
    },
    "gemini-2.5-flash": {
        "context_window": 1000000,
        "cost_per_mtok": 0.15,
        "provider": "gemini",
        "backend": "direct",
    },
    "gemini-3-flash": {
        "context_window": 1000000,
        "cost_per_mtok": 0.15,
        "provider": "gemini",
        "backend": "direct",
    },
    "gemini-3.1-pro": {
        "context_window": 200000,
        "cost_per_mtok": 3.50,
        "provider": "gemini",
        "backend": "direct",
    },
    # OpenAI / Codex
    "gpt-4o": {
        "context_window": 128000,
        "cost_per_mtok": 2.50,
        "provider": "openai",
        "backend": "direct",
    },
    "gpt-4o-mini": {
        "context_window": 128000,
        "cost_per_mtok": 0.15,
        "provider": "openai",
        "backend": "direct",
    },
    "gpt-5-mini": {
        "context_window": 128000,
        "cost_per_mtok": 0.15,
        "provider": "copilot",
        "backend": "direct",
    },
    "gpt-5.3-codex-spark": {
        "context_window": 128000,
        "cost_per_mtok": 1.20,
        "provider": "codex",
        "backend": "direct",
    },
    "gpt-5.3-codex": {
        "context_window": 128000,
        "cost_per_mtok": 3.00,
        "provider": "codex",
        "backend": "direct",
    },
    "gpt-5.3-codex-high": {
        "context_window": 128000,
        "cost_per_mtok": 5.00,
        "provider": "codex",
        "backend": "direct",
    },
    "gpt-5.3-codex-max": {
        "context_window": 128000,
        "cost_per_mtok": 10.00,
        "provider": "codex",
        "backend": "direct",
    },
    # Zhipu GLM
    "glm-5": {
        "context_window": 128000,
        "cost_per_mtok": 0.40,
        "provider": "glm",
        "backend": "proxy",
    },
    "GLM-5": {
        "context_window": 128000,
        "cost_per_mtok": 0.40,
        "provider": "glm",
        "backend": "proxy",
    },
    "z-ai/glm-5": {
        "context_window": 128000,
        "cost_per_mtok": 0.40,
        "provider": "nim",
        "backend": "proxy",
    },
    # MiniMax
    "minimax-m2.5": {
        "context_window": 128000,
        "cost_per_mtok": 0.40,
        "provider": "minimax",
        "backend": "proxy",
    },
    "MiniMax-M2.5": {
        "context_window": 128000,
        "cost_per_mtok": 0.40,
        "provider": "minimax",
        "backend": "proxy",
    },
    # Kilo
    "kilo-default": {
        "context_window": 128000,
        "cost_per_mtok": 0.50,
        "provider": "kilo",
        "backend": "proxy",
    },
    # Roo
    "roo-default": {
        "context_window": 128000,
        "cost_per_mtok": 0.50,
        "provider": "roo",
        "backend": "proxy",
    },
    # DeepSeek
    "deepseek-v3.2": {
        "context_window": 64000,
        "cost_per_mtok": 0.50,
        "provider": "deepseek",
        "backend": "direct",
    },
    # Kimi
    "kimi-k2.5": {
        "context_window": 200000,
        "cost_per_mtok": 0.50,
        "provider": "kimi",
        "backend": "proxy",
    },
    # Qwen
    "qwen3-coder": {
        "context_window": 32000,
        "cost_per_mtok": 0.30,
        "provider": "qwen",
        "backend": "proxy",
    },
    # Meta
    "llama-nemotron-ultra": {
        "context_window": 128000,
        "cost_per_mtok": 0.20,
        "provider": "meta",
        "backend": "proxy",
    },
    # Cursor
    "composer-1": {
        "context_window": 128000,
        "cost_per_mtok": 0.25,
        "provider": "cursor-agent",
        "backend": "direct",
    },
    "composer-1.5": {
        "context_window": 128000,
        "cost_per_mtok": 0.30,
        "provider": "cursor-agent",
        "backend": "direct",
    },
}


def get_model_metadata(model_id: str) -> dict[str, Any] | None:
    """Get comprehensive metadata for a model.

    Args:
        model_id: Model identifier (may be alias or canonical name)

    Returns:
        Model metadata dict or None if not found
    """
    # Direct lookup
    if model_id in MODEL_METADATA:
        return MODEL_METADATA[model_id]

    # Normalize and try variations
    normalized = model_id.lower().replace("-", "").replace(".", "").replace("/", "").replace("_", "")

    for key, metadata in MODEL_METADATA.items():
        key_normalized = key.lower().replace("-", "").replace(".", "").replace("/", "").replace("_", "")
        if key_normalized == normalized:
            return metadata

    return None


def has_model_metadata(model_id: str) -> bool:
    """Check if model has metadata available.

    Args:
        model_id: Model identifier

    Returns:
        True if metadata exists, False otherwise
    """
    return get_model_metadata(model_id) is not None


def get_all_models_with_metadata() -> list[str]:
    """Get list of all models with metadata.

    Returns:
        List of model IDs
    """
    return list(MODEL_METADATA.keys())
