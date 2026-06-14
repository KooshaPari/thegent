"""Stub module."""

from typing import TYPE_CHECKING, Any


class SubAgentDispatcher:
    """Sub-agent dispatcher stub."""

    def __init__(self) -> None:
        self.agents: dict[str, Any] = {}

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        return {"dispatched": True}


__all__ = ["SubAgentDispatcher", "CapabilityIndex", "_CLI_HARNESSES", "is_cli_harness"]


def is_cli_harness(path: str) -> bool:
    """Check if a path is a CLI harness.

    Args:
        path: Path to check.

    Returns:
        True if the path is a CLI harness.
    """
    import os

    return os.path.exists(path) and os.access(path, os.X_OK)


_CLI_HARNESSES = {
    "bash": "/usr/bin/bash",
    "zsh": "/bin/zsh",
    "sh": "/bin/sh",
}


def _CLI_HARNESSES_get_shell(shell_name: str) -> str | None:
    """Get the path for a shell harness.

    Args:
        shell_name: Name of the shell.

    Returns:
        Path to the shell or None if not found.
    """
    return _CLI_HARNESSES.get(shell_name)


class CapabilityIndex:
    """Index for agent capabilities."""

    def __init__(self) -> None:
        self.capabilities: dict[str, list[str]] = {}

    def register(self, agent_id: str, capabilities: list[str]) -> None:
        """Register capabilities for an agent."""
        self.capabilities[agent_id] = capabilities

    def get(self, agent_id: str) -> list[str]:
        """Get capabilities for an agent."""
        return self.capabilities.get(agent_id, [])
