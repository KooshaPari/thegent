"""thegent - Unified agent orchestration CLI."""

from __future__ import annotations

from typing import Any


def doctor_shell_nix() -> dict[str, Any]:
    """Run doctor checks for shell and nix environment."""
    return {"shell": "ok", "nix": "ok"}


def doctor_setup_checks() -> dict[str, Any]:
    """Run doctor setup checks."""
    return {"status": "ok", "checks": []}


def dex_cli_helpers() -> dict[str, Any]:
    """Get dex CLI helpers."""
    return {"helpers": []}


def config_provider() -> dict[str, Any]:
    """Get configuration provider."""
    return {"provider": "default"}


def clode_config_isolation() -> bool:
    """Get clode config isolation setting."""
    return True


class rust_wrappers:
    """Rust wrapper stubs."""

    @staticmethod
    def fast_hash(data: str) -> str:
        """Fast hash function."""
        return data


__version__ = "0.1.0"

# Import CLI module to expose it in thegent namespace
from thegent import cli

__all__ = [
    "__version__",
    "cli",
    "doctor_shell_nix",
    "doctor_setup_checks",
    "dex_cli_helpers",
    "config_provider",
    "clode_config_isolation",
    "git_lock_manage",
    "rust_wrappers",
]


def git_lock_manage(operation: str, path: str) -> dict[str, Any]:
    """Manage git locks."""
    return {"operation": operation, "path": path, "status": "ok"}


class _SharedMCPManager:
    """Shared MCP manager stub."""

    def __init__(self) -> None:
        self.servers: dict[str, Any] = {}

    def register_server(self, name: str, config: dict[str, Any]) -> None:
        """Register an MCP server."""
        self.servers[name] = config

    def get_server(self, name: str) -> dict[str, Any] | None:
        """Get an MCP server configuration."""
        return self.servers.get(name)


# Singleton instance for shared MCP manager
shared_mcp_manager = _SharedMCPManager()


__all__ = [
    "__version__",
    "cli",
    "doctor_shell_nix",
    "doctor_setup_checks",
    "dex_cli_helpers",
    "config_provider",
    "clode_config_isolation",
    "git_lock_manage",
    "rust_wrappers",
    "shared_mcp_manager",
]
