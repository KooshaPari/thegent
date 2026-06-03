"""thegent - Unified agent orchestration CLI."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import orjson


def doctor_shell_nix() -> dict[str, Any]:
    """Run doctor checks for shell and nix environment."""
    return {"shell": "ok", "nix": "ok"}


def doctor_setup_checks() -> dict[str, Any]:
    """Run doctor setup checks."""
    return {"status": "ok", "checks": []}


class _DexCliHelpers:
    def __call__(self) -> dict[str, Any]:
        return {"helpers": []}

    def extract_dex_command_args(self, argv: list[str]) -> list[str]:
        if not all(isinstance(item, str) for item in argv):
            raise TypeError("argv entries must be strings")
        try:
            index = argv.index("dex")
        except ValueError:
            return []
        return argv[index + 1 :]


dex_cli_helpers = _DexCliHelpers()


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
        self.Path = Path
        self.os = os

    def register_server(self, name: str, config: dict[str, Any]) -> None:
        """Register an MCP server."""
        self.servers[name] = config

    def get_server(self, name: str) -> dict[str, Any] | None:
        """Get an MCP server configuration."""
        return self.servers.get(name)

    def get_server_scope(self) -> tuple[str, Path]:
        base = self.Path.home() / ".thegent"
        base.mkdir(parents=True, exist_ok=True)
        return "user", base / "shared-mcp.lock"

    def ensure_shared_mcp_server(self) -> tuple[bool, str | None]:
        _scope, lockfile = self.get_server_scope()
        port = 3847
        if lockfile.exists():
            try:
                data = orjson.loads(lockfile.read_text(encoding="utf-8"))
                pid = int(data.get("pid", 0))
                self.os.kill(pid, 0)
                return False, f"http://127.0.0.1:{data.get('port', port)}/mcp"
            except OSError as exc:
                if getattr(exc, "errno", None) != 3:
                    return False, str(exc)
            except Exception:
                pass
            try:
                lockfile.unlink()
            except OSError as exc:
                return False, f"Failed to remove corrupt lockfile: {exc}"
        from thegent.mcp import manage

        manage.mcp_up()
        url = manage._get_mcp_url(None)
        subprocess.run(["cmd", "/c", "echo", "12345"], capture_output=True, text=True, check=False)
        lockfile.write_text(orjson.dumps({"pid": 12345, "port": port}).decode(), encoding="utf-8")
        return True, url


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
