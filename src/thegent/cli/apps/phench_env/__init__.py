"""CLI phench_env module.

This module provides CLI phench environment configuration.
"""

from __future__ import annotations

from typing import Any, Callable


def register_env_commands(
    app: object,
    run_env_doctor_for_target_fn: Callable[..., Any] | None = None,
    set_env_profile_fn: Callable[..., Any] | None = None,
    get_env_profile_fn: Callable[..., Any] | None = None,
    **kwargs: Any,
) -> None:
    """Register environment commands with the CLI app.

    Args:
        app: The CLI application to register commands with.
    """
    pass


__all__ = ["register_env_commands"]
