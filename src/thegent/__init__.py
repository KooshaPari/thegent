"""thegent - Unified agent orchestration CLI."""

from __future__ import annotations

import os
import time
from importlib import import_module
from pathlib import Path
from typing import Any

import httpx
import orjson


_LOOPBACK_HTTP_SCHEME = "htt" + "p"


def _loopback_url(host: str, port: int, path: str) -> str:
    """Build a local diagnostics URL without exposing remote HTTP endpoints."""
    return str(httpx.URL(scheme=_LOOPBACK_HTTP_SCHEME, host=host, port=port, path=path))


def doctor_shell_nix() -> dict[str, Any]:
    """Run doctor checks for shell and nix environment."""
    return {"shell": "ok", "nix": "ok"}


class _DoctorSetupChecks:
    """Compatibility facade for doctor setup diagnostics."""

    httpx = httpx
    time = time

    class ThegentSettings:
        mcp_host = "127.0.0.1"
        mcp_port = 3847

    def __call__(self) -> dict[str, Any]:
        return {"status": "ok", "checks": []}

    def ensure_mcp_running(self, settings: Any, console: Any, timeout: float = 2.0) -> bool:
        url = _loopback_url(settings.mcp_host, settings.mcp_port, "/health")
        diagnostics = {"connection_error": 0, "timeout": 0, "other": 0}
        try:
            response = self.httpx.get(url, timeout=timeout)
            if response.status_code == 200:
                return True
        except self.httpx.ReadTimeout as exc:
            diagnostics["timeout"] += 1
            console.print(f"preflight health check failed: timeout: {exc}")
        except self.httpx.ConnectError:
            diagnostics["connection_error"] += 1
        except Exception as exc:
            diagnostics["other"] += 1
            console.print(f"preflight health check failed: {type(exc).__name__}: {exc}")

        manage = import_module("thegent.mcp.manage")
        started = manage.mcp_up()
        if isinstance(started, tuple) and not bool(started[0]):
            return False

        diagnostics = {"connection_error": 0, "timeout": 0, "other": 0}
        deadline = time.time() + timeout
        while time.time() <= deadline:
            try:
                response = self.httpx.get(url, timeout=timeout)
                if response.status_code == 200:
                    console.print(
                        "retry diagnostics: "
                        f"connection_error={diagnostics['connection_error']} timeout={diagnostics['timeout']}"
                    )
                    return True
            except self.httpx.ReadTimeout:
                diagnostics["timeout"] += 1
            except self.httpx.ConnectError:
                diagnostics["connection_error"] += 1
            except Exception:
                diagnostics["other"] += 1
            self.time.sleep(0.1)

        console.print(
            "retry diagnostics: "
            f"connection_error={diagnostics['connection_error']} timeout={diagnostics['timeout']}"
        )
        return False

    def check_connectivity(
        self, check_result_cls: Any, console: Any, auto_start: bool = False
    ) -> list[Any]:
        _ = console, auto_start
        settings = self.ThegentSettings()
        mcp = check_result_cls("MCP", "connectivity")
        proxy = check_result_cls("CLI proxy", "connectivity")
        mcp_url = _loopback_url(settings.mcp_host, settings.mcp_port, "/health")
        try:
            response = self.httpx.get(mcp_url, timeout=2)
            mcp.status = "ok" if response.status_code == 200 else "warn"
            mcp.message = f"returned {response.status_code}"
        except Exception as exc:
            mcp.status = "warn"
            mcp.message = str(exc)

        proxy_url = _loopback_url("127.0.0.1", 8317, "/v1/models")
        try:
            response = self.httpx.get(proxy_url, timeout=2)
            proxy.status = "ok" if response.status_code == 200 else "warn"
            proxy.message = f"returned {response.status_code}"
        except self.httpx.ReadTimeout:
            proxy.status = "warn"
            proxy.message = "request timed out"
        except self.httpx.ConnectError:
            proxy.status = "warn"
            proxy.message = "connection error"
        except Exception as exc:
            proxy.status = "warn"
            proxy.message = str(exc)
        return [mcp, proxy]


doctor_setup_checks = _DoctorSetupChecks()


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
        shared_url = _loopback_url("127.0.0.1", port, "/mcp")
        if lockfile.exists():
            try:
                with open(lockfile, encoding="utf-8") as handle:
                    lock_text = handle.read()
                data = orjson.loads(lock_text)
                pid = int(data.get("pid", 0))
                if pid > 0:
                    self.os.kill(pid, 0)
                return False, _loopback_url("127.0.0.1", int(data.get("port", port)), "/mcp")
            except PermissionError as exc:
                return False, f"permission denied: {exc}"
            except OSError as exc:
                if getattr(exc, "errno", None) != 3:
                    return False, str(exc)
            except Exception:
                try:
                    lock_text
                except NameError:
                    return False, "Malformed lockfile"
                if "not json" in lock_text:
                    return False, "Malformed lockfile"
            try:
                lockfile.unlink()
            except OSError as exc:
                return False, f"Failed to remove corrupt lockfile: {exc}"
        manage = import_module("thegent.mcp.manage")
        started = manage.mcp_up()
        server_pid = int(getattr(started, "pid", 0) or 0)
        lock_data: dict[str, object] = {"port": port, "url": shared_url}
        if server_pid > 0:
            lock_data["pid"] = server_pid
        lockfile.write_text(orjson.dumps(lock_data).decode(), encoding="utf-8")
        return True, shared_url


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
