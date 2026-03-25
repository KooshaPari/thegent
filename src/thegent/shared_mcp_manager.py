"""
Shared MCP Server Manager (System-Wide First)

Manages system-wide shared MCP servers, scoping down to per-project only when needed.
"""

import json
import logging
import os
import time
from errno import ESRCH
from pathlib import Path

from thegent.infra.shim_subprocess import run as shim_run

_LOG = logging.getLogger(__name__)


def _remove_lockfile(lockfile: Path, *, reason: str) -> tuple[bool, str | None]:
    try:
        lockfile.unlink()
    except FileNotFoundError:
        return True, None
    except PermissionError as exc:
        return False, f"Failed to remove {reason} lockfile ({lockfile}): {type(exc).__name__}: {exc}"
    except OSError as exc:
        return False, f"Failed to remove {reason} lockfile ({lockfile}): {type(exc).__name__}: {exc}"
    return True, None


def get_server_scope(project_root: Path | None = None) -> tuple[str, Path]:
    """
    Determine server scope (system-wide or project-scoped).
    Default: system-wide. Scope down only if project requires isolation.

    Returns:
        (scope_type, lockfile_path)
    """
    cache_dir = Path.home() / ".cache" / "thegent" / "mcp"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Default: system-wide
    system_lockfile = cache_dir / "system.lock"

    # Check if project requires isolation
    if project_root:
        project_config = project_root / ".thegent" / "isolate_servers"
        if project_config.exists():
            # Project requires isolation - scope down
            import hashlib

            project_key = hashlib.sha256(str(project_root.resolve()).encode()).hexdigest()[:16]
            project_lockfile = cache_dir / f"{project_key}.lock"
            return ("project", project_lockfile)

    # Default: system-wide
    return ("system", system_lockfile)


def ensure_shared_mcp_server(project_root: Path | None = None) -> tuple[bool, str | None]:
    """
    Ensure shared MCP server is running (system-wide by default).
    Returns: (is_new_server, server_url_or_error)
    """
    scope_type, lockfile = get_server_scope(project_root)

    # Check if server already running
    if lockfile.exists():
        try:
            with open(lockfile, encoding="utf-8") as f:
                data = json.load(f)
                pid = data.get("pid")
                port = data.get("port", 3847)

                if not isinstance(pid, int):
                    _LOG.warning(
                        "shared_mcp_lockfile_invalid_pid",
                        extra={
                            "failure_type": "invalid_pid_type",
                            "lockfile": str(lockfile),
                            "pid_type": type(pid).__name__,
                        },
                    )
                    return False, f"Invalid lockfile pid type in {lockfile}: {type(pid).__name__}"
                # Check if process still alive
                try:
                    os.kill(pid, 0)  # Check if process exists
                    return False, f"http://127.0.0.1:{port}/mcp"
                except OSError as exc:
                    if exc.errno != ESRCH:
                        return False, f"Unable to validate lockfile process {pid}: {exc}"
                    # Process dead, remove stale lockfile
                    ok, message = _remove_lockfile(lockfile, reason="stale")
                    if not ok:
                        return False, message
        except json.JSONDecodeError as exc:
            ok, message = _remove_lockfile(lockfile, reason="corrupt")
            if not ok:
                return False, message
            _LOG.warning(
                "shared_mcp_lockfile_corrupt_json",
                extra={"failure_type": "corrupt_json", "lockfile": str(lockfile), "error_message": str(exc)[:180]},
            )
        except FileNotFoundError:
            pass
        except PermissionError as exc:
            return False, f"Lockfile read permission denied ({lockfile}): {exc}"
        except OSError as exc:
            return False, f"Lockfile read failure ({lockfile}): {exc}"

    # Start new server (system-wide)
    from thegent.mcp.manage import _get_mcp_url, mcp_up
    from thegent.config import ThegentSettings as _TGSettings

    # Start MCP server via process-compose
    try:
        mcp_up()  # Returns None on success, raises on error
        # Get the actual MCP URL (may be different port)
        mcp_url = _get_mcp_url(_TGSettings())
        if not mcp_url:
            return False, "Failed to get MCP URL after startup"

        # Extract port from URL
        import re

        port_match = re.search(r":(\d+)", mcp_url)
        port = int(port_match.group(1)) if port_match else 3847

        # Find process-compose PID (look for process-compose process)

        try:
            # Find process-compose process managing MCP
            result = shim_run(
                ["pgrep", "-f", "process-compose.*mcp"], capture_output=True, text=True, check=False
            )
            pid = int(result.stdout.strip().split("\n")[0]) if result.stdout.strip() else None
        except Exception:
            pid = None

        # Create lockfile
        lockfile.write_text(
            json.dumps(
                {
                    "pid": pid or os.getpid(),
                    "port": port,
                    "url": mcp_url,
                    "scope": scope_type,
                    "project_root": str(project_root) if project_root else None,
                    "started_at": time.time(),
                }
            ),
            encoding="utf-8",
        )

        return True, mcp_url
    except Exception as e:
        return False, f"Failed to start MCP server: {e}"


def get_shared_mcp_url(project_root: Path | None = None) -> str:
    """
    Get URL for shared MCP server (system-wide by default).
    Starts server if not running.
    """
    _, url = ensure_shared_mcp_server(project_root)
    if url and not url.startswith("http"):
        # If error message, return default
        return "http://127.0.0.1:3847/mcp"
    return url or "http://127.0.0.1:3847/mcp"


def check_mcp_health(project_root: Path | None = None) -> tuple[bool, str]:
    """
    Check health of shared MCP server.
    Returns: (is_healthy, status_message)
    """
    _scope_type, lockfile = get_server_scope(project_root)

    if not lockfile.exists():
        return False, "No lockfile found - server not started"

    try:
        with open(lockfile, encoding="utf-8") as f:
            data = json.load(f)
            pid = data.get("pid")
            url = data.get("url", f"http://127.0.0.1:{data.get('port', 3847)}/mcp")

            # Check if process exists
            try:
                os.kill(pid, 0)
                # Try to connect to URL
                import httpx

                try:
                    httpx.get(f"{url}/health", timeout=2)
                    return True, f"Server healthy at {url}"
                except Exception:
                    # Health endpoint might not exist, but server is running
                    return True, f"Server running at {url} (health check unavailable)"
            except OSError:
                return False, f"Process {pid} not found - server may have crashed"
    except Exception as e:
        return False, f"Error reading lockfile: {e}"
