"""Model catalog and selection for thegent.

Provides unified access to model metadata, pricing, and configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal


class ModelTier(str, Enum):
    """Model quality/cost tiers."""
    FREE = "free"
    CHEAP = "cheap"
    STANDARD = "standard"
    PREMIUM = "premium"
    RESEARCH = "research"


class Provider(str, Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    COHERE = "cohere"
    GROQ = "groq"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


@dataclass
class ModelSpec:
    """Model specification with metadata."""
    id: str
    provider: Provider
    tier: ModelTier
    context_window: int
    max_output_tokens: int
    supports_vision: bool
    supports_function_calling: bool
    supports_json_mode: bool
    input_cost_per_1k: float  # USD
    output_cost_per_1k: float  # USD
    latency_tier: Literal["fast", "balanced", "slow"]
    aliases: list[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class ModelCatalog:
    """Central registry of available models and their specifications."""

    # Standard model catalog - centralized model definitions
    MODELS: dict[str, ModelSpec] = {
        "gpt-4o": ModelSpec(
            id="gpt-4o",
            provider=Provider.OPENAI,
            tier=ModelTier.PREMIUM,
            context_window=128_000,
            max_output_tokens=16_384,
            supports_vision=True,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.0025,
            output_cost_per_1k=0.01,
            latency_tier="balanced",
            aliases=["gpt-4o-latest"],
        ),
        "gpt-4o-mini": ModelSpec(
            id="gpt-4o-mini",
            provider=Provider.OPENAI,
            tier=ModelTier.CHEAP,
            context_window=128_000,
            max_output_tokens=16_384,
            supports_vision=True,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.00015,
            output_cost_per_1k=0.0006,
            latency_tier="fast",
            aliases=["gpt-4o-mini-latest"],
        ),
        "claude-3-5-sonnet": ModelSpec(
            id="claude-3-5-sonnet",
            provider=Provider.ANTHROPIC,
            tier=ModelTier.PREMIUM,
            context_window=200_000,
            max_output_tokens=8_192,
            supports_vision=True,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.015,
            latency_tier="balanced",
            aliases=["claude-sonnet-3.5"],
        ),
        "claude-3-haiku": ModelSpec(
            id="claude-3-haiku",
            provider=Provider.ANTHROPIC,
            tier=ModelTier.CHEAP,
            context_window=200_000,
            max_output_tokens=4_096,
            supports_vision=False,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.00025,
            output_cost_per_1k=0.00125,
            latency_tier="fast",
            aliases=["claude-haiku"],
        ),
        "gemini-2.0-flash": ModelSpec(
            id="gemini-2.0-flash",
            provider=Provider.GOOGLE,
            tier=ModelTier.STANDARD,
            context_window=1_000_000,
            max_output_tokens=8_192,
            supports_vision=True,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.0001,
            output_cost_per_1k=0.0004,
            latency_tier="fast",
            aliases=["gemini-flash"],
        ),
        "gemini-2.0-pro": ModelSpec(
            id="gemini-2.0-pro",
            provider=Provider.GOOGLE,
            tier=ModelTier.PREMIUM,
            context_window=2_000_000,
            max_output_tokens=8_192,
            supports_vision=True,
            supports_function_calling=True,
            supports_json_mode=True,
            input_cost_per_1k=0.001,
            output_cost_per_1k=0.004,
            latency_tier="balanced",
            aliases=["gemini-pro"],
        ),
    }

    @classmethod
    def get(cls, model_id: str) -> ModelSpec | None:
        """Get model specification by ID."""
        # Direct match
        if model_id in cls.MODELS:
            return cls.MODELS[model_id]

        # Check aliases
        for spec in cls.MODELS.values():
            if model_id in spec.aliases:
                return spec

        return None

    @classmethod
    def list_by_tier(cls, tier: ModelTier) -> list[ModelSpec]:
        """List all models in a specific tier."""
        return [m for m in cls.MODELS.values() if m.tier == tier]

    @classmethod
    def list_by_provider(cls, provider: Provider) -> list[ModelSpec]:
        """List all models for a specific provider."""
        return [m for m in cls.MODELS.values() if m.provider == provider]

    @classmethod
    def select_for_task(
        cls,
        task_complexity: Literal["simple", "standard", "complex"] = "standard",
        budget_tier: ModelTier = ModelTier.STANDARD,
        requires_vision: bool = False,
        requires_functions: bool = False,
    ) -> ModelSpec | None:
        """Select appropriate model for task requirements."""
        candidates = [m for m in cls.MODELS.values() if m.tier.value == budget_tier.value]

        if requires_vision:
            candidates = [m for m in candidates if m.supports_vision]

        if requires_functions:
            candidates = [m for m in candidates if m.supports_function_calling]

        # Prefer models matching task complexity
        if task_complexity == "simple":
            # Prefer fast latency for simple tasks
            fast = [m for m in candidates if m.latency_tier == "fast"]
            if fast:
                return fast[0]

        if task_complexity == "complex":
            # Prefer premium tier for complex tasks
            premium = [m for m in candidates if m.tier == ModelTier.PREMIUM]
            if premium:
                return premium[0]

        return candidates[0] if candidates else None

    @classmethod
    def estimate_cost(
        cls,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float | None:
        """Estimate cost for a request."""
        spec = cls.get(model_id)
        if not spec:
            return None

        input_cost = (input_tokens / 1000) * spec.input_cost_per_1k
        output_cost = (output_tokens / 1000) * spec.output_cost_per_1k

        return input_cost + output_cost


# Export public API
__all__ = [
    "ModelCatalog",
    "ModelSpec",
    "ModelTier",
    "Provider",
]
