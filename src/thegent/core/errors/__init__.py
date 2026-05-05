"""Core error types for thegent.

Shared exception classes used across execution, agents, models, and routing layers.
No dependencies on other thegent modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ErrorContext:
    """Rich context for error reporting."""

    error_type: str
    error_message: str
    what_happened: str
    why_it_happened: str
    how_to_fix: list[str]
    related_files: list[str] | None = None
    related_config: dict[str, Any] | None = None
    documentation_link: str | None = None
    command_suggestion: str | None = None

    def __post_init__(self) -> None:
        if self.related_files is None:
            self.related_files = []
        if self.related_config is None:
            self.related_config = {}


class TheGentError(Exception):
    """Base exception for all thegent errors."""

    def __init__(
        self,
        message: str,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext(
            error_type=self.__class__.__name__,
            error_message=message,
            what_happened="An error occurred",
            why_it_happened="Unknown cause",
            how_to_fix=["Check the error message and try again"],
        )
        self.cause = cause


class ExecutionError(TheGentError):
    """Error during task execution."""


class AgentError(TheGentError):
    """Error related to agent operations."""


class ModelError(TheGentError):
    """Error related to LLM model operations."""


class RouterError(TheGentError):
    """Error during routing or dispatch."""


class ValidationError(TheGentError):
    """Error during validation."""


class ConfigurationError(TheGentError):
    """Error related to configuration."""


class ParseError(TheGentError):
    """Error during parsing."""

    def __init__(
        self,
        message: str,
        raw_output: str | None = None,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message, context, cause)
        self.raw_output = raw_output


__all__ = [
    "ErrorContext",
    "TheGentError",
    "ExecutionError",
    "AgentError",
    "ModelError",
    "RouterError",
    "ValidationError",
    "ConfigurationError",
    "ParseError",
]
