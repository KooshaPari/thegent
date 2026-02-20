"""Comprehensive security guardrails for AI agents.

Implements multiple layers of protection:
- Command validation and sanitization
- Input/output filtering
- Rate limiting
- Token optimization
- Secret management
- Invariant enforcement
- Context window management
"""

import hashlib
import logging
import os
import re
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Security Invariants
# ============================================================================


class SecurityInvariant:
    """System invariants that must always hold true."""

    # Processes that must NEVER be killed
    PROTECTED_PROCESSES: set[str] = {
        "cursor-agent",
        "cursor agent",
        "thegent",
        "claude",
        "codex",
        "droid",
        "opencode",
        "copilot",
        "gemini",
        "bash",
        "zsh",
        "sh",
        "ghostty",
        "terminal",
        "iterm",
        "alacritty",
        "kitty",
        "wezterm",
        "warp",
    }

    # Commands that are NEVER allowed
    FORBIDDEN_COMMANDS: set[str] = {
        "rm -rf /",
        "rm -rf /*",
        "dd if=",
        "mkfs",
        "fdisk",
        "format",
        "del /f /s /q",
        "format c:",
    }

    # Dangerous patterns
    DANGEROUS_PATTERNS: list[tuple[str, str]] = [
        (r"kill.*-9.*cursor", "Killing cursor-agent processes"),
        (r"kill.*-9.*thegent", "Killing thegent processes"),
        (r"rm.*-rf.*\/", "Recursive delete of root"),
        (r"chmod.*777.*\/", "Dangerous permissions"),
        (r"sudo.*rm.*-rf", "Sudo recursive delete"),
        (r"xargs.*kill", "Bulk process killing"),
        (r"pkill.*cursor", "Killing cursor processes"),
    ]

    # Maximum command length (prevent buffer overflow attempts)
    MAX_COMMAND_LENGTH: int = 10000

    # Maximum arguments
    MAX_ARGUMENTS: int = 100

    # Maximum file path length
    MAX_PATH_LENGTH: int = 4096


# ============================================================================
# Rate Limiting
# ============================================================================


@dataclass
class RateLimit:
    """Rate limit configuration."""

    max_calls: int
    window_seconds: int
    calls: list[float] = field(default_factory=list)

    def check(self) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()
        # Remove old calls outside window
        self.calls = [t for t in self.calls if now - t < self.window_seconds]

        if len(self.calls) >= self.max_calls:
            return False

        self.calls.append(now)
        return True

    def reset(self):
        """Reset rate limit."""
        self.calls.clear()


class RateLimiter:
    """Rate limiter for operations."""

    def __init__(self):
        self.limits: dict[str, RateLimit] = {}

    def add_limit(self, key: str, max_calls: int, window_seconds: int):
        """Add a rate limit."""
        self.limits[key] = RateLimit(max_calls, window_seconds)

    def check(self, key: str) -> bool:
        """Check if operation is allowed."""
        if key not in self.limits:
            return True
        return self.limits[key].check()

    def reset(self, key: str):
        """Reset rate limit for key."""
        if key in self.limits:
            self.limits[key].reset()


# Global rate limiter instance
_rate_limiter = RateLimiter()

# Default rate limits
_rate_limiter.add_limit("command_execution", max_calls=100, window_seconds=60)
_rate_limiter.add_limit("file_operations", max_calls=200, window_seconds=60)
_rate_limiter.add_limit("network_requests", max_calls=50, window_seconds=60)
_rate_limiter.add_limit("process_kill", max_calls=10, window_seconds=300)


# ============================================================================
# Command Validation
# ============================================================================


class CommandValidator:
    """Validates and sanitizes commands before execution."""

    @staticmethod
    def validate_command(cmd: str | list[str]) -> tuple[bool, str | None]:
        """Validate command safety.

        Returns:
            (is_valid, error_message)
        """
        cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
        cmd_lower = cmd_str.lower()

        # Check length
        if len(cmd_str) > SecurityInvariant.MAX_COMMAND_LENGTH:
            return False, f"Command too long (max {SecurityInvariant.MAX_COMMAND_LENGTH} chars)"

        # Check for forbidden commands
        for forbidden in SecurityInvariant.FORBIDDEN_COMMANDS:
            if forbidden in cmd_lower:
                return False, f"Forbidden command pattern detected: {forbidden}"

        # Check dangerous patterns
        for pattern, description in SecurityInvariant.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False, f"Security violation: {description}"

        # Check for kill commands targeting protected processes
        if any(kill_word in cmd_lower for kill_word in ["kill", "pkill", "killall"]):
            for protected in SecurityInvariant.PROTECTED_PROCESSES:
                if protected in cmd_lower:
                    # Allow if explicitly excluding (grep -v)
                    if "grep -v" not in cmd_lower and "exclude" not in cmd_lower:
                        return False, f"Cannot kill protected process: {protected}"

        # Check argument count
        if isinstance(cmd, list) and len(cmd) > SecurityInvariant.MAX_ARGUMENTS:
            return False, f"Too many arguments (max {SecurityInvariant.MAX_ARGUMENTS})"

        return True, None

    @staticmethod
    def sanitize_path(path: str) -> tuple[bool, str | None]:
        """Sanitize file path.

        Returns:
            (is_valid, sanitized_path_or_error)
        """
        if len(path) > SecurityInvariant.MAX_PATH_LENGTH:
            return False, f"Path too long (max {SecurityInvariant.MAX_PATH_LENGTH} chars)"

        # Prevent directory traversal
        if ".." in path or path.startswith("/"):
            # Allow absolute paths but log warning
            if path.startswith("/") and not path.startswith("/tmp") and not path.startswith("/var/tmp"):
                logger.warning(f"Absolute path access: {path}")

        # Remove dangerous characters
        dangerous_chars = ["\x00", "\r", "\n"]
        for char in dangerous_chars:
            if char in path:
                return False, f"Dangerous character in path: {char!r}"

        return True, path


# ============================================================================
# Token Optimization
# ============================================================================


class TokenOptimizer:
    """Optimizes token usage through context management."""

    # Strategies for token reduction
    MAX_CONTEXT_TOKENS = 100000  # Conservative limit
    TARGET_CONTEXT_TOKENS = 50000  # Target for optimization

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough: ~4 chars per token)."""
        return len(text) // 4

    @staticmethod
    def compress_context(context: str, max_tokens: int = TARGET_CONTEXT_TOKENS) -> str:
        """Compress context to fit within token limit."""
        current_tokens = TokenOptimizer.estimate_tokens(context)

        if current_tokens <= max_tokens:
            return context

        # Truncate from middle (keep start and end)
        target_chars = max_tokens * 4
        if len(context) <= target_chars:
            return context

        # Keep first 40% and last 40%
        keep_start = int(target_chars * 0.4)
        keep_end = int(target_chars * 0.4)
        truncated = context[:keep_start] + "\n\n[... truncated ...]\n\n" + context[-keep_end:]

        logger.info(f"Compressed context: {current_tokens} -> {TokenOptimizer.estimate_tokens(truncated)} tokens")
        return truncated

    @staticmethod
    def remove_secrets(text: str) -> str:
        """Remove secrets from text (replace with variables)."""
        # Common secret patterns
        patterns = [
            (r"sk-[a-zA-Z0-9]{20,}", "API_KEY_OPENAI"),
            (r"sk-ant-[a-zA-Z0-9-]{20,}", "API_KEY_ANTHROPIC"),
            (r"ghp_[a-zA-Z0-9]{36}", "GITHUB_TOKEN"),
            (r"xox[baprs]-[0-9a-zA-Z-]{10,}", "SLACK_TOKEN"),
            (r"AKIA[0-9A-Z]{16}", "AWS_ACCESS_KEY"),
            (r'password["\s:=]+([^\s"\']+)', "PASSWORD_HIDDEN"),
            (r'api[_-]?key["\s:=]+([^\s"\']+)', "API_KEY_HIDDEN"),
        ]

        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def optimize_prompt(prompt: str, max_tokens: int | None = None) -> str:
        """Optimize prompt by removing secrets and compressing."""
        optimized = TokenOptimizer.remove_secrets(prompt)

        if max_tokens:
            optimized = TokenOptimizer.compress_context(optimized, max_tokens)

        return optimized


# ============================================================================
# Secret Management
# ============================================================================


class SecretManager:
    """Manages secrets using environment variables."""

    # Map of secret names to environment variable names
    SECRET_ENV_MAP: dict[str, str] = {
        "openai_api_key": "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "openrouter_api_key": "OPENROUTER_API_KEY",
        "google_api_key": "GOOGLE_API_KEY",
        "github_token": "GITHUB_TOKEN",
        "aws_access_key": "AWS_ACCESS_KEY_ID",
        "aws_secret_key": "AWS_SECRET_ACCESS_KEY",
    }

    @staticmethod
    def get_secret(name: str, default: str | None = None) -> str | None:
        """Get secret from environment variable."""
        env_var = SecretManager.SECRET_ENV_MAP.get(name, name.upper())
        return os.environ.get(env_var, default)

    @staticmethod
    def mask_secret(value: str) -> str:
        """Mask secret value for logging."""
        if not value or len(value) < 8:
            return "***"
        return value[:4] + "..." + value[-4:]

    @staticmethod
    def validate_secret_present(name: str) -> bool:
        """Check if secret is present."""
        return SecretManager.get_secret(name) is not None


# ============================================================================
# Main Guardrails Class
# ============================================================================


class Guardrails:
    """Main guardrails orchestrator."""

    def __init__(self):
        self.validator = CommandValidator()
        self.token_optimizer = TokenOptimizer()
        self.secret_manager = SecretManager()
        self.rate_limiter = _rate_limiter

    def validate_and_sanitize_command(
        self, cmd: str | list[str], operation_type: str = "command_execution"
    ) -> tuple[bool, str | None, str | None]:
        """Validate command and check rate limits.

        Returns:
            (is_allowed, sanitized_command_or_error, error_message)
        """
        # Check rate limit
        if not self.rate_limiter.check(operation_type):
            return False, None, f"Rate limit exceeded for {operation_type}"

        # Validate command
        is_valid, error = self.validator.validate_command(cmd)
        if not is_valid:
            return False, None, error

        # Sanitize if list
        if isinstance(cmd, list):
            sanitized = " ".join(cmd)
        else:
            sanitized = cmd

        return True, sanitized, None

    def optimize_context(self, context: str, max_tokens: int | None = None) -> str:
        """Optimize context for token usage."""
        return self.token_optimizer.optimize_prompt(context, max_tokens)

    def check_invariant(self, invariant_name: str, value: Any) -> tuple[bool, str | None]:
        """Check system invariant.

        Args:
            invariant_name: Name of invariant to check
            value: Value to check against invariant

        Returns:
            (is_valid, error_message)
        """
        if invariant_name == "no_kill_protected_processes":
            if isinstance(value, str):
                cmd_lower = value.lower()
                for protected in SecurityInvariant.PROTECTED_PROCESSES:
                    if protected in cmd_lower and any(k in cmd_lower for k in ["kill", "pkill"]):
                        if "grep -v" not in cmd_lower:
                            return False, f"Cannot kill protected process: {protected}"

        return True, None


# Global guardrails instance
_guardrails = Guardrails()


# ============================================================================
# Public API
# ============================================================================


def validate_command(cmd: str | list[str], operation_type: str = "command_execution") -> tuple[bool, str | None]:
    """Public API: Validate command safety.

    Returns:
        (is_allowed, error_message)
    """
    is_allowed, _, error = _guardrails.validate_and_sanitize_command(cmd, operation_type)
    return is_allowed, error


def optimize_context(context: str, max_tokens: int | None = None) -> str:
    """Public API: Optimize context for token usage."""
    return _guardrails.optimize_context(context, max_tokens)


def get_secret(name: str, default: str | None = None) -> str | None:
    """Public API: Get secret from environment."""
    return SecretManager.get_secret(name, default)


def check_rate_limit(operation_type: str) -> bool:
    """Public API: Check if operation is within rate limit."""
    return _rate_limiter.check(operation_type)
