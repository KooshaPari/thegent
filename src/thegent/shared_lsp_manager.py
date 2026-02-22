"""
Shared LSP Server Manager (System-Wide First)

Manages system-wide shared LSP servers, scoping down to per-project only when needed.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

LSP_SERVERS: dict[str, dict[str, Any]] = {
    "python": {
        "command": "pyright-langserver",
        "args": ["--stdio"],
        "supports_multi_client": True,
        "supports_multi_root": True,  # Can handle multiple project roots
    },
    "typescript": {
        "command": "typescript-language-server",
        "args": ["--stdio"],
        "supports_multi_client": True,
        "supports_multi_root": True,
    },
}


def get_lsp_server_scope(project_root: Path | None = None, language: str = "python") -> tuple[str, Path]:
    """
    Determine LSP server scope (system-wide or project-scoped).
    Default: system-wide. Scope down only if project requires isolation.

    Returns:
        (scope_type, lockfile_path)
    """
    cache_dir = Path.home() / ".cache" / "thegent" / "lsp"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Default: system-wide
    system_lockfile = cache_dir / "system" / f"{language}.lock"
    system_lockfile.parent.mkdir(parents=True, exist_ok=True)

    # Check if project requires isolation
    if project_root:
        # Check for project-specific requirements
        project_config = project_root / ".thegent" / "isolate_servers"
        if project_config.exists():
            # Check if language version differs
            # (e.g., Python 3.11 vs 3.12 might need separate servers)
            # For now, scope down if isolation requested
            import hashlib

            project_key = hashlib.sha256(str(project_root.resolve()).encode()).hexdigest()[:16]
            project_lockfile = cache_dir / project_key / f"{language}.lock"
            project_lockfile.parent.mkdir(parents=True, exist_ok=True)
            return ("project", project_lockfile)

    # Default: system-wide
    return ("system", system_lockfile)


def ensure_shared_lsp_server(project_root: Path | None = None, language: str = "python") -> str | None:
    """
    Ensure shared LSP server is running (system-wide by default).
    Returns: stdio pipe path or socket path or None
    """
    scope_type, lockfile = get_lsp_server_scope(project_root, language)
    socket_path = lockfile.parent / f"{language}.sock"  # Unix domain socket

    # Check if server already running
    if lockfile.exists() and socket_path.exists():
        try:
            with open(lockfile) as f:
                data = json.load(f)
                pid = data.get("pid")

                try:
                    os.kill(pid, 0)  # Check if process exists
                    return str(socket_path)
                except OSError:
                    # Process dead, remove stale files
                    lockfile.unlink()
                    socket_path.unlink(missing_ok=True)
        except Exception:
            lockfile.unlink(missing_ok=True)

    # Start new LSP server (system-wide)
    lsp_config = LSP_SERVERS.get(language)
    if not lsp_config:
        return None

    # Start LSP server process
    try:
        import shutil

        command = shutil.which(lsp_config["command"])
        if not command:
            return None

        # Start server with stdio (LSP standard)
        # For system-wide sharing, we'll use a named pipe or socket
        # For now, start process and track it
        import subprocess

        # Create pipe for communication
        server_process = subprocess.Popen(
            [command] + lsp_config["args"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Store process info in lockfile
        lockfile.write_text(
            json.dumps(
                {
                    "pid": server_process.pid,
                    "language": language,
                    "command": command,
                    "scope": scope_type,
                    "project_root": str(project_root) if project_root else None,
                    "started_at": time.time(),
                    "socket_path": str(socket_path),
                }
            )
        )

        # Return socket path (clients will connect via stdio pipe)
        # For multi-client support, we'd need a proxy/bridge
        return str(socket_path)
    except Exception:
        return None
