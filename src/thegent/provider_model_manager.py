"""Provider and model manager for thegent."""

from __future__ import annotations

from typing import Literal


def resolve_provider_for_model(model: str) -> str:
    """Resolve the provider for a given model.
    
    Args:
        model: Model name or alias
        
    Returns:
        Provider name (e.g., 'anthropic', 'google', 'openai')
    """
    # Map of known model prefixes to providers
    model_provider_map: dict[str, str] = {
        'gpt': 'openai',
        'claude': 'anthropic',
        'gemini': 'google',
        'sonnet': 'anthropic',
        'opus': 'anthropic',
        'haiku': 'anthropic',
        'flash': 'google',
        'ultra': 'anthropic',
        'dex': 'anthropic',
        'max': 'openai',
        'high': 'anthropic',
        'xhigh': 'anthropic',
        'glm': 'google',
    }
    
    model_lower = model.lower()
    for prefix, provider in model_provider_map.items():
        if model_lower.startswith(prefix):
            return provider
    
    # Default based on common patterns
    return 'anthropic'


def run_provider_form() -> None:
    """Launch the legacy provider form interface."""
    # Stub implementation - actual form not implemented
    pass
