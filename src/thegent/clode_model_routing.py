"""Model-first routing tables and helpers for clode."""

from collections import Counter

MODEL_ALIAS: dict[str, str] = {
    "dex": "gpt-5.3-codex",
    "codex": "gpt-5.3-codex",
    "comp": "composer-1",
    "composer": "composer-1.5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "opus1m": "claude-opus-4.6-1m",
    "sonnet": "anthropic/claude-sonnet-4-20250514",
    "glm": "glm-5",
    "glm5": "glm-5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "step": "step-3.5-flash",
    "flash": "gemini-3-flash",
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
}

MODEL_PROVIDER_SETS: dict[str, tuple[str, ...]] = {
    "gpt-5.3-codex": ("codex",),
    "gpt-5.3-codex-high": ("codex",),
    "gpt-5.3-codex-xhigh": ("codex",),
    "composer-1": ("cursor",),
    "composer-1.5": ("cursor",),
    "glm-5": ("glm", "kilo", "nim", "minimax"),
    "minimax-m2.5": ("minimax", "kilo"),
    "claude-haiku-4.5": ("claude", "antigravity", "codex", "kiro"),
    "claude-opus-4.6": ("claude", "antigravity", "kiro"),
    "anthropic/claude-sonnet-4-20250514": ("openrouter",),
    "step-3.5-flash": ("nim",),
    "gemini-3-flash": ("gemini",),
    "gpt-5-mini": ("copilot",),
}

MODEL_COUNTER: Counter[str] = Counter()

MODEL_PROVIDERS: dict[str, tuple[str, ...]] = {
    "composer-1": ("cursor",),
    "composer-1.5": ("cursor",),
    "minimax-m2.5": ("minimax", "kilo"),
    "deepseek-v3.2": ("kilo", "nim"),
    "glm-5": ("glm", "kilo", "nim"),
    "step-3.5-flash": ("nim",),
    "claude-haiku-4.5": ("claude", "antigravity", "codex", "kiro"),
    "claude-opus-4.6": ("claude", "antigravity", "kiro"),
    "claude-opus-4.6-1m": ("claude", "antigravity", "kiro"),
    "anthropic/claude-sonnet-4-20250514": ("openrouter",),
}

CLODE_PROVIDER_MODEL: dict[str, str] = {
    "cursor": "composer-1.5",
    "nim": "glm-5",
    "minimax": "MiniMax-M2.5",
    "kilo": "MiniMax-M2.5",
    "glm": "glm-5",
    "openrouter": "anthropic/claude-sonnet-4-20250514",
    "copilot": "gpt-5-mini",
    "gemini": "gemini-3-flash",
}


def resolve_provider_for_model(model_alias: str) -> str:
    """Resolve provider for model-first routing with round-robin balancing."""
    canonical = MODEL_ALIAS.get(model_alias.lower(), model_alias)
    providers = MODEL_PROVIDER_SETS.get(canonical)
    if not providers:
        return "nim"
    idx = MODEL_COUNTER[canonical]
    selected = providers[idx % len(providers)]
    MODEL_COUNTER[canonical] = (idx + 1) % len(providers)
    return selected


def model_for_provider(provider: str) -> str:
    """Default model for a provider derived from model->provider mapping."""
    if provider == "kiro":
        return "claude-haiku-4.5"
    for model, providers in MODEL_PROVIDERS.items():
        if provider in providers:
            return model
    return "minimax-m2.5"
