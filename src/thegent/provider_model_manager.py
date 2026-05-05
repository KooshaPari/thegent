"""thegent.provider_model_manager - Provider model management."""

from __future__ import annotations

from __future__ import annotations

_MODEL_ALIASES = {
    "cursor": "composer-1.5",
    "cursor-1": "cursor-1",
    "cursor-2": "cursor-2",
    "comp": "composer-1.5",
    "composer": "composer-1.5",
    "composer-1": "composer-1",
    "composer-1.5": "composer-1.5",
    "claude": "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
    "sonnet": "claude-3-5-sonnet-20241022",
    "gpt": "gpt-4o",
    "gpt-4": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "gemini": "gemini-2-5-pro-preview-06-05",
    "gemini-2": "gemini-2-5-pro-preview-06-05",
    "o1": "o1-preview",
    "o1-preview": "o1-preview",
    "o1-mini": "o1-mini",
    "glm": "glm-4",
    "haiku": "claude-3-haiku-20240307",
    "opus": "claude-3-opus-20240229",
    "ultra": "gemini-ultra",
    "flash": "gemini-2.5-flash",
    "high": "codex-high",
    "xhigh": "codex-xhigh",
    "dex": "dex-1",
}


def get_alias(model: str) -> str:
    """Get the canonical alias for a model."""
    if model is None:
        return ""
    lower = model.lower()
    if lower in _MODEL_ALIASES:
        return _MODEL_ALIASES[lower]
    for alias, canonical in _MODEL_ALIASES.items():
        if alias in lower:
            return canonical
    return model


def resolve_provider_for_model(model: str) -> str:
    """Resolve provider based on model name."""
    model_lower = model.lower()
    if "claude" in model_lower or "sonnet" in model_lower or "haiku" in model_lower or "opus" in model_lower:
        return "anthropic"
    elif "gpt" in model_lower or "openai" in model_lower or "o1" in model_lower:
        return "openai"
    elif "gemini" in model_lower or "ultra" in model_lower or "flash" in model_lower:
        return "google"
    elif "cursor" in model_lower or "composer" in model_lower or "comp" in model_lower:
        return "anthropic"
    elif "glm" in model_lower:
        return "zhipuai"
    else:
        return "unknown"


def run_provider_form() -> None:
    """Launch the legacy provider form interface."""
    # This function is called from the CLI to launch the form
    # The actual form will be launched by the caller
