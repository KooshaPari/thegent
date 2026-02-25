"""Provider-specific retry and circuit breaker configuration for LLM API calls.

This module provides retry configurations optimized for each LLM provider's
rate limits, error patterns, and best practices.

Configuration is based on research from:
- MiniMax API docs and community best practices
- GLM/Zhipu API documentation
- OpenAI API rate limit handling
- Anthropic Claude API guidelines
- Google Gemini API documentation
- DeepSeek API documentation
- OpenRouter API documentation

# @trace FR-ROUTE-013
"""

from dataclasses import dataclass
from typing import Final

# Default retry configuration
DEFAULT_MAX_ATTEMPTS: Final[int] = 3
DEFAULT_MIN_WAIT: Final[float] = 1.0
DEFAULT_MAX_WAIT: Final[float] = 30.0
DEFAULT_BACKOFF_MULTIPLIER: Final[float] = 1.5


@dataclass
class ProviderRetryConfig:
    """Retry configuration for a specific LLM provider."""

    provider: str
    max_attempts: int
    min_wait: float
    max_wait: float
    backoff_multiplier: float
    timeout: int
    # Circuit breaker settings
    circuit_breaker_fail_threshold: int
    circuit_breaker_timeout: int

    @property
    def retry_after_default(self) -> int:
        """Default retry-after value in seconds."""
        return int(self.min_wait)


# Provider-specific retry configurations based on API documentation and best practices
PROVIDER_RETRY_CONFIGS: dict[str, ProviderRetryConfig] = {
    # MiniMax - Highspeed plan optimized
    "minimax": ProviderRetryConfig(
        provider="minimax",
        max_attempts=5,
        min_wait=2.0,
        max_wait=120.0,
        backoff_multiplier=2.0,
        timeout=300,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=60,
    ),
    # GLM/Zhipu
    "glm": ProviderRetryConfig(
        provider="glm",
        max_attempts=4,
        min_wait=2.0,
        max_wait=60.0,
        backoff_multiplier=1.5,
        timeout=180,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=45,
    ),
    # OpenAI
    "openai": ProviderRetryConfig(
        provider="openai",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=2.0,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # Anthropic Claude
    "claude": ProviderRetryConfig(
        provider="claude",
        max_attempts=4,
        min_wait=2.0,
        max_wait=60.0,
        backoff_multiplier=2.0,
        timeout=180,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=45,
    ),
    # Google Gemini
    "gemini": ProviderRetryConfig(
        provider="gemini",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # DeepSeek
    "deepseek": ProviderRetryConfig(
        provider="deepseek",
        max_attempts=3,
        min_wait=1.0,
        max_wait=20.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # OpenRouter
    "openrouter": ProviderRetryConfig(
        provider="openrouter",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=2.0,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # NVIDIA NIM
    "nim": ProviderRetryConfig(
        provider="nim",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=30,
    ),
    # Kilo
    "kilo": ProviderRetryConfig(
        provider="kilo",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=30,
    ),
    # Ollama (local)
    "ollama": ProviderRetryConfig(
        provider="ollama",
        max_attempts=2,
        min_wait=0.5,
        max_wait=5.0,
        backoff_multiplier=1.5,
        timeout=300,
        circuit_breaker_fail_threshold=3,
        circuit_breaker_timeout=15,
    ),
    # Codex
    "codex": ProviderRetryConfig(
        provider="codex",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=2.0,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # Cursor
    "cursor": ProviderRetryConfig(
        provider="cursor",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=2.0,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # Antigravity
    "antigravity": ProviderRetryConfig(
        provider="antigravity",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=2.0,
        timeout=120,
        circuit_breaker_fail_threshold=5,
        circuit_breaker_timeout=30,
    ),
    # Kimi
    "kimi": ProviderRetryConfig(
        provider="kimi",
        max_attempts=4,
        min_wait=2.0,
        max_wait=60.0,
        backoff_multiplier=1.5,
        timeout=180,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=45,
    ),
    # Qwen
    "qwen": ProviderRetryConfig(
        provider="qwen",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=30,
    ),
    # Meta (Llama)
    "meta": ProviderRetryConfig(
        provider="meta",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=30,
    ),
    # Roo
    "roo": ProviderRetryConfig(
        provider="roo",
        max_attempts=3,
        min_wait=1.0,
        max_wait=30.0,
        backoff_multiplier=1.5,
        timeout=120,
        circuit_breaker_fail_threshold=4,
        circuit_breaker_timeout=30,
    ),
}


def get_provider_retry_config(provider: str) -> ProviderRetryConfig:
    """Get retry configuration for a specific provider."""
    normalized = provider.lower().strip()
    return PROVIDER_RETRY_CONFIGS.get(
        normalized,
        ProviderRetryConfig(
            provider=normalized,
            max_attempts=DEFAULT_MAX_ATTEMPTS,
            min_wait=DEFAULT_MIN_WAIT,
            max_wait=DEFAULT_MAX_WAIT,
            backoff_multiplier=DEFAULT_BACKOFF_MULTIPLIER,
            timeout=120,
            circuit_breaker_fail_threshold=5,
            circuit_breaker_timeout=30,
        ),
    )


def get_all_providers() -> list[str]:
    """Get list of all configured providers."""
    return list(PROVIDER_RETRY_CONFIGS.keys())


# Error status code mappings
RETRYABLE_STATUS_CODES: dict[int, str] = {
    429: "rate_limit",
    500: "server_error",
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout",
    529: "overloaded",
}


def is_retryable_error(status_code: int) -> bool:
    """Check if an HTTP status code indicates a retryable error."""
    return status_code in RETRYABLE_STATUS_CODES


def get_error_category(status_code: int) -> str:
    """Get the category of error for a status code."""
    return RETRYABLE_STATUS_CODES.get(status_code, "unknown")
