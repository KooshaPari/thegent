"""BKM-08: Python wrapper for the thegent-discovery binary.

DiscoveryClient calls the ``thegent-discovery`` binary (built from
``crates/thegent-discovery/src/main.rs``) via a single subprocess and returns
structured Python objects.  When the binary is not found on PATH it falls back
to individual subprocess / psutil calls so the module is always usable.

Usage::

    from thegent.native.discovery_native import DiscoveryClient

    client = DiscoveryClient()
    sessions  = client.sessions()          # list[dict]
    tools     = client.tools()             # list[dict]
    processes = client.processes()         # list[dict]
    all_data  = client.all()               # dict with keys sessions/tools/processes
    client.is_native                       # True if binary is available

FR-trace: BKM-08 (PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# Tools probed by the fallback implementation (mirrors PROBE_TOOLS in main.rs)
_PROBE_TOOLS: list[str] = [
    "claude",
    "thegent",
    "tmux",
    "git",
    "npx",
    "node",
    "python3",
    "screen",
    "cargo",
]

# Default agent pattern (mirrors DEFAULT_AGENT_PATTERN in main.rs)
_DEFAULT_AGENT_PATTERN = r"claude|thegent|codex|copilot|cursor.agent|opencode|aider|gemini|droid"


# ---------------------------------------------------------------------------
# Fallback helpers (used when the binary is absent)
# ---------------------------------------------------------------------------


def _fallback_sessions() -> list[dict[str, Any]]:
    """Discover tmux/screen sessions without the native binary."""
    sessions: list[dict[str, Any]] = []

    # tmux
    sockets = [
        None,
        str(Path(tempfile.gettempdir()) / f"tmux-{os.getuid()}" / "default"),
        str(
            Path(tempfile.gettempdir())
            / ".."
            / "private"
            / f"tmux-{os.getuid()}"
            / "default"
        ),
    ]
    for socket in sockets:
        cmd = ["tmux"]
        if socket:
            cmd.extend(["-S", socket])
        cmd.extend(
            [
                "list-sessions",
                "-F",
                "#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}",
            ]
        )
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        sessions.append(
                            {
                                "session_name": parts[0],
                                "windows": int(parts[1]) if parts[1].isdigit() else 0,
                                "created": parts[2],
                                "attached": parts[3].strip() != "0",
                                "source": "tmux",
                            }
                        )
                break
        except Exception:
            continue

    # screen (best-effort)
    try:
        result = subprocess.run(
            ["screen", "-ls"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if stripped and stripped[0].isdigit():
                parts = stripped.split(".", 1)
                if len(parts) == 2:
                    name_end = parts[1].find("\t")
                    name = parts[1][:name_end] if name_end != -1 else parts[1]
                    sessions.append(
                        {
                            "session_name": name,
                            "windows": 1,
                            "created": "",
                            "attached": "(Attached)" in stripped,
                            "source": "screen",
                        }
                    )
    except Exception:
        pass

    return sessions


def _fallback_tools() -> list[dict[str, Any]]:
    """Check tool availability without the native binary."""
    results = []
    for tool in _PROBE_TOOLS:
        path = shutil.which(tool)
        results.append(
            {
                "tool": tool,
                "available": path is not None,
                "path": path,
            }
        )
    return results


def _fallback_processes(pattern: str | None = None) -> list[dict[str, Any]]:
    """Scan processes using psutil without the native binary."""
    import re

    try:
        import psutil
    except ImportError:
        _log.warning("psutil not available; process discovery skipped")
        return []

    pat = pattern or _DEFAULT_AGENT_PATTERN
    try:
        regex = re.compile(pat, re.IGNORECASE)
    except re.error:
        _log.error("Invalid regex pattern: %s", pat)
        return []

    found: list[dict[str, Any]] = []
    for proc in psutil.process_iter(
        ["pid", "ppid", "name", "cmdline", "memory_info", "cpu_percent", "create_time"]
    ):
        try:
            name = proc.info.get("name") or ""
            cmdline = proc.info.get("cmdline") or []
            cmd_str = " ".join(cmdline)
            if regex.search(name) or regex.search(cmd_str):
                mem = proc.info.get("memory_info")
                found.append(
                    {
                        "pid": proc.info["pid"],
                        "ppid": proc.info.get("ppid"),
                        "name": name,
                        "cmd": cmdline,
                        "memory_kb": (mem.rss // 1024) if mem else 0,
                        "cpu_usage": proc.info.get("cpu_percent") or 0.0,
                        "run_time_s": 0,
                    }
                )
        except Exception:
            continue

    return found


# ---------------------------------------------------------------------------
# DiscoveryClient
# ---------------------------------------------------------------------------


class DiscoveryClient:
    """Thin Python wrapper around the ``thegent-discovery`` binary (BKM-08).

    Falls back to individual subprocess / psutil calls when the binary is not
    available so that callers always get usable results.

    Attributes:
        is_native: ``True`` when the ``thegent-discovery`` binary was found on
            PATH (or via :envvar:`THGENT_DISCOVERY_BIN`).
        binary_path: Resolved path to the binary (or ``None`` for fallback).
    """

    #: Override the binary path via this environment variable
    ENV_VAR = "THGENT_DISCOVERY_BIN"
    #: Default binary name looked up via shutil.which
    BINARY_NAME = "thegent-discovery"

    def __init__(self) -> None:
        env_path = os.environ.get(self.ENV_VAR)
        if env_path and Path(env_path).is_file():
            self.binary_path: Path | None = Path(env_path)
        else:
            found = shutil.which(self.BINARY_NAME)
            self.binary_path = Path(found) if found else None

        self.is_native: bool = self.binary_path is not None
        if self.is_native:
            _log.debug("thegent-discovery binary found at %s", self.binary_path)
        else:
            _log.debug(
                "thegent-discovery binary not found; using Python fallback (BKM-08)"
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run(self, *args: str) -> Any:
        """Run the binary with the given subcommand args, return parsed JSON."""
        assert self.binary_path is not None
        cmd = [str(self.binary_path), *args]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                _log.warning(
                    "thegent-discovery exited %d: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
                return None
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            _log.error("thegent-discovery timed out running: %s", cmd)
            return None
        except json.JSONDecodeError as exc:
            _log.error("thegent-discovery returned invalid JSON: %s", exc)
            return None
        except Exception as exc:
            _log.error("thegent-discovery failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sessions(self) -> list[dict[str, Any]]:
        """Return tmux/screen sessions as a list of dicts.

        Returns:
            List of session dicts with keys: ``session_name``, ``windows``,
            ``created``, ``attached``, ``source``.
        """
        if self.is_native:
            result = self._run("sessions")
            if result is not None:
                return result

        return _fallback_sessions()

    def tools(self) -> list[dict[str, Any]]:
        """Return tool availability as a list of dicts.

        Returns:
            List of dicts with keys: ``tool``, ``available``, ``path``.
        """
        if self.is_native:
            result = self._run("tools")
            if result is not None:
                return result

        return _fallback_tools()

    def processes(self, pattern: str | None = None) -> list[dict[str, Any]]:
        """Return matching processes as a list of dicts.

        Args:
            pattern: Optional regex pattern to filter by process name or
                command line. Defaults to the built-in agent pattern.

        Returns:
            List of process dicts with keys: ``pid``, ``ppid``, ``name``,
            ``cmd``, ``memory_kb``, ``cpu_usage``, ``run_time_s``.
        """
        if self.is_native:
            args = ["processes"]
            if pattern:
                args.extend(["--pattern", pattern])
            result = self._run(*args)
            if result is not None:
                return result

        return _fallback_processes(pattern)

    def all(self, pattern: str | None = None) -> dict[str, Any]:
        """Return combined discovery: sessions + tools + processes.

        Args:
            pattern: Optional process filter regex.

        Returns:
            Dict with keys: ``sessions``, ``tools``, ``processes``.
        """
        if self.is_native:
            args = ["all"]
            if pattern:
                args.extend(["--pattern", pattern])
            result = self._run(*args)
            if result is not None:
                return result

        return {
            "sessions": _fallback_sessions(),
            "tools": _fallback_tools(),
            "processes": _fallback_processes(pattern),
        }

    def tools_map(self) -> dict[str, bool]:
        """Convenience: return ``{"tool": available}`` dict.

        Returns:
            Mapping of tool name to availability boolean.
        """
        return {entry["tool"]: entry["available"] for entry in self.tools()}
