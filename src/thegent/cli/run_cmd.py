"""thegent.cli.run_cmd - CLI run command module.

This module provides the run command for thegent CLI.
"""

from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# Model aliases - maps shorthand to full model names
_MODEL_ALIASES = {
    # cursor and composer both map to composer-1.5 for compatibility
    "cursor": "composer-1.5",
    "cursor-1": "cursor-1",
    "cursor-2": "cursor-2",
    "comp": "composer-1.5",  # comp is shorthand for composer
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
    # Additional aliases from tests
    "glm": "glm-4",
    "haiku": "claude-3-haiku-20240307",
    "opus": "claude-3-opus-20240229",
    "ultra": "gemini-ultra",
    "flash": "gemini-2.5-flash",
    "high": "codex-high",
    "xhigh": "codex-xhigh",
    "dex": "dex-1",
}


def _normalize_model_alias(model: str) -> str:
    """Normalize a model name/alias to canonical form."""
    if model is None:
        return ""
    
    # Lowercase for comparison
    lower = model.lower()
    
    # Check if it's an exact alias match
    if lower in _MODEL_ALIASES:
        return _MODEL_ALIASES[lower]
    
    # Check for partial matches - the input contains the alias name
    for alias, canonical in _MODEL_ALIASES.items():
        if alias in lower:
            return canonical
    
    # Return as-is if no match
    return model


def _resolve_provider_for_model(model: str) -> str:
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


def _run_model_cmd(
    model: str,
    prompt: str,
    cwd: str | None = None,
    remote: str | None = None,
    **kwargs: Any,
) -> int:
    """Execute a model command.
    
    Args:
        model: Model to use
        prompt: Prompt for the model
        cwd: Working directory
        remote: Remote execution target
        **kwargs: Additional arguments
        
    Returns:
        Exit code
    """
    # Normalize model name using alias resolution
    model = _normalize_model_alias(model)
    
    # Build command
    cmd = ["thegent", "run", "--model", model, "--prompt", prompt]
    
    if cwd:
        cmd.extend(["--cwd", cwd])
    if remote:
        cmd.extend(["--remote", remote])
    
    # Execute
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def run_cmd(
    model: str | None = None,
    prompt: str | None = None,
    cwd: str | None = None,
    remote: str | None = None,
    **kwargs: Any,
) -> int:
    """Execute the run command.
    
    Args:
        model: Model to use
        prompt: Prompt for the model
        cwd: Working directory
        remote: Remote execution target
        **kwargs: Additional arguments
        
    Returns:
        Exit code (0 for success)
    """
    if model and prompt:
        return _run_model_cmd(model, prompt, cwd, remote, **kwargs)
    return 0
