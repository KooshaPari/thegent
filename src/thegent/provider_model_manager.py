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
    """Resolve provider based on model name.

    This function maps model identifiers to the corresponding provider
    name. It is used throughout the system to determine which backend
    should handle a given model request.

    Args:
        model: The model identifier as provided by the client or
               internal code. Case-insensitive matching is performed.

    Returns:
        A string representing the canonical provider name:
        "anthropic", "openai", "google", "cohere", "mistral",
        "meta", "journey", or "unknown" if no match is found.

    Examples:
        >>> resolve_provider_for_model("gpt-4")
        'openai'
        >>> resolve_provider_for_model("claude-3-opus")
        'anthropic'
        >>> resolve_provider_for_model("gemini-pro")
        'google'
        >>> resolve_provider_for_model("unknown-model")
        'unknown'
    """
    if not model:
        return "unknown"
    
    model_lower = model.lower()
    
    # Anthropic models
    if any(claude_marker in model_lower for claude_marker in 
           ("claude", "sonnet", "haiku", "opus")):
        return "anthropic"
    
    # OpenAI models
    if any(openai_marker in model_lower for openai_marker in 
           ("gpt", "openai", "o1", "gpt-4", "gpt-3.5")):
        return "openai"
    
    # Google Gemini models
    if "gemini" in model_lower:
        return "google"
    
    # Cohere models
    if "cohere" in model_lower:
        return "cohere"
    
    # Mistral models
    if "mistral" in model_lower:
        return "mistral"
    
    # Meta/Llama models
    if "llama" in model_lower or "meta-" in model_lower:
        return "meta"
    
    # Journey models
    if "journey" in model_lower:
        return "journey"
    
    return "unknown"

def run_provider_form() -> None:
    """Launch the legacy provider form interface."""
    # This function is called from the CLI to launch the form
    # The actual form will be launched by the caller
