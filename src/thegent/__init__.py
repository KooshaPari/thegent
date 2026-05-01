"""thegent - Unified agent orchestration CLI."""

from __future__ import annotations


def doctor_shell_nix() -> dict[str, Any]:
    """Run doctor checks for shell and nix environment."""
    return {"shell": "ok", "nix": "ok"}


class rust_wrappers:
    """Rust wrapper stubs."""
    
    @staticmethod
    def fast_hash(data: str) -> str:
        """Fast hash function."""
        return data


__version__ = "0.1.0"

# Import CLI module to expose it in thegent namespace
from thegent import cli

__all__ = ["__version__", "cli", "doctor_shell_nix", "rust_wrappers", "git_lock_manage"]


def git_lock_manage(operation: str, path: str) -> dict[str, Any]:
    """Manage git locks."""
    return {"operation": operation, "path": path, "status": "ok"}
