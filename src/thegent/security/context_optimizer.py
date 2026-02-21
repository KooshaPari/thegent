"""Context and token optimization for LLM interactions.

Implements strategies to reduce token usage while maintaining context quality.
"""

import logging
import re

logger = logging.getLogger(__name__)


class ContextOptimizer:
    """Optimizes context for LLM interactions."""

    # Token estimation: ~4 characters per token (conservative)
    CHARS_PER_TOKEN = 4

    # Default limits
    DEFAULT_MAX_TOKENS = 50000
    DEFAULT_TARGET_TOKENS = 30000

    def __init__(self, max_tokens: int | None = None, target_tokens: int | None = None) -> None:
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.target_tokens = target_tokens or self.DEFAULT_TARGET_TOKENS

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return len(text) // self.CHARS_PER_TOKEN

    def remove_secrets(self, text: str) -> str:
        """Remove secrets and replace with variable names."""
        patterns = [
            # API keys
            (r"sk-[a-zA-Z0-9]{20,}", "${OPENAI_API_KEY}"),
            (r"sk-ant-[a-zA-Z0-9-]{20,}", "${ANTHROPIC_API_KEY}"),
            (r"ghp_[a-zA-Z0-9]{36}", "${GITHUB_TOKEN}"),
            (r"xox[baprs]-[0-9a-zA-Z-]{10,}", "${SLACK_TOKEN}"),
            (r"AKIA[0-9A-Z]{16}", "${AWS_ACCESS_KEY_ID}"),
            # Passwords
            (r'password["\s:=]+([^\s"\']{8,})', 'password="${PASSWORD}"'),
            (r'passwd["\s:=]+([^\s"\']{8,})', 'passwd="${PASSWORD}"'),
            # Connection strings
            (r"postgresql://[^:\s]+:[^@\s]+@", "postgresql://${DB_USER}:${DB_PASSWORD}@"),
            (r"mysql://[^:\s]+:[^@\s]+@", "mysql://${DB_USER}:${DB_PASSWORD}@"),
            (r"redis://[^:\s]+:[^@\s]+@", "redis://${DB_USER}:${DB_PASSWORD}@"),
        ]

        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def compress_whitespace(self, text: str) -> str:
        """Compress excessive whitespace."""
        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Replace multiple spaces with single space
        text = re.sub(r" {2,}", " ", text)
        return text

    def truncate_smart(self, text: str, max_tokens: int) -> str:
        """Smart truncation keeping important parts."""
        target_chars = max_tokens * self.CHARS_PER_TOKEN

        if len(text) <= target_chars:
            return text

        # Keep first 45% and last 45%, truncate middle
        keep_start = int(target_chars * 0.45)
        keep_end = int(target_chars * 0.45)

        # Try to break at sentence boundaries
        start_part = text[:keep_start]
        end_part = text[-keep_end:]

        # Find last sentence end in start part
        last_period = start_part.rfind(".")
        if last_period > keep_start * 0.8:
            start_part = start_part[: last_period + 1]

        # Find first sentence start in end part
        first_period = end_part.find(".")
        if first_period < keep_end * 0.2 and first_period > 0:
            end_part = end_part[first_period + 1 :]

        truncated = f"{start_part}\n\n[... {len(text) - keep_start - keep_end} characters truncated ...]\n\n{end_part}"

        logger.debug(
            f"Truncated context: {len(text)} -> {len(truncated)} chars ({self.estimate_tokens(truncated)} tokens)"
        )
        return truncated

    def optimize(self, context: str, remove_secrets: bool = True) -> str:
        """Optimize context for token usage.

        Args:
            context: Original context
            remove_secrets: Whether to remove secrets

        Returns:
            Optimized context
        """
        optimized = context

        # Remove secrets first
        if remove_secrets:
            optimized = self.remove_secrets(optimized)

        # Compress whitespace
        optimized = self.compress_whitespace(optimized)

        # Check if truncation needed
        tokens = self.estimate_tokens(optimized)
        if tokens > self.max_tokens:
            optimized = self.truncate_smart(optimized, self.max_tokens)
        elif tokens > self.target_tokens:
            # Soft truncation to target
            optimized = self.truncate_smart(optimized, self.target_tokens)

        return optimized

    def optimize_prompt(self, prompt: str, system_prompt: str | None = None) -> tuple[str, str | None]:
        """Optimize prompt and system prompt separately.

        Returns:
            (optimized_prompt, optimized_system_prompt)
        """
        optimized_prompt = self.optimize(prompt)
        optimized_system = self.optimize(system_prompt) if system_prompt else None

        return optimized_prompt, optimized_system


# Global optimizer instance
_default_optimizer = ContextOptimizer()


def optimize_context(context: str, max_tokens: int | None = None, remove_secrets: bool = True) -> str:
    """Public API: Optimize context."""
    optimizer = ContextOptimizer(max_tokens=max_tokens) if max_tokens else _default_optimizer
    return optimizer.optimize(context, remove_secrets=remove_secrets)
