"""BKM-08: discovery client with native binary first, Python fallback second."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

_PROBE_TOOLS: tuple[str, ...] = (
    "claude",
    "thegent",
    "tmux",
    "git",
    "npx",
    "node",
    "python3",
    "screen",
    "cargo",
)
_DEFAULT_PATTERN = r"(claude|codex|cursor|thegent|droid|clode|fanta|dex|roid)"

_log = logging.getLogger(__name__)


def _fallback_sessions() -> list[dict[str, Any]]:
    """Collect tmux sessions via shell command output."""
    sessions: list[dict[str, Any]] = []
    fmt = "#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}"
    try:
        proc = subprocess.run(
            ["tmux", "list-sessions", "-F", fmt],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                if not line.strip():
                    continue
                parts = line.split("|", 3)
                if len(parts) != 4:
                    continue
                sessions.append(
                    {
                        "session_name": parts[0],
                        "windows": int(parts[1]) if parts[1].isdigit() else 0,
                        "created": parts[2],
                        "attached": parts[3] == "1",
                        "source": "tmux",
                    }
                )
    except Exception:
        return []
    return sessions


def _fallback_tools() -> list[dict[str, Any]]:
    """Collect tool availability from PATH lookup."""
    tools: list[dict[str, Any]] = []
    for tool in _PROBE_TOOLS:
        path = shutil.which(tool)
        tools.append({"tool": tool, "available": path is not None, "path": path})
    return tools


def _fallback_processes(pattern: str | None = None) -> list[dict[str, Any]]:
    """Collect matching processes with psutil."""
    try:
        import psutil
    except Exception:
        return []

    patt = pattern or _DEFAULT_PATTERN
    try:
        regex = re.compile(patt, re.IGNORECASE)
    except re.error:
        return []

    now = time.time()
    matched: list[dict[str, Any]] = []
    for proc in psutil.process_iter(["pid", "ppid", "name", "cmdline", "memory_info", "cpu_percent", "create_time"]):
        try:
            info = proc.info
            name = str(info.get("name") or "")
            cmdline = info.get("cmdline") or []
            cmd = " ".join(cmdline) if isinstance(cmdline, list) else str(cmdline)
            target = f"{name} {cmd}".strip()
            if not regex.search(target):
                continue
            mem_obj = info.get("memory_info")
            mem_kb = int(getattr(mem_obj, "rss", 0) // 1024)
            create_time = float(info.get("create_time") or now)
            matched.append(
                {
                    "pid": int(info.get("pid") or 0),
                    "ppid": int(info.get("ppid") or 0),
                    "name": name,
                    "cmd": cmdline if isinstance(cmdline, list) else [cmd],
                    "memory_kb": mem_kb,
                    "cpu_usage": float(info.get("cpu_percent") or 0.0),
                    "run_time_s": max(0.0, now - create_time),
                }
            )
        except Exception:
            continue
    return matched


class DiscoveryClient:
    """Binary-backed discovery API with deterministic fallback behavior."""

    ENV_VAR = "THGENT_DISCOVERY_BIN"

    def __init__(self) -> None:
        env_path = os.environ.get(self.ENV_VAR, "").strip()
        if env_path and Path(env_path).exists():
            self.binary_path = Path(env_path)
        else:
            found = shutil.which("thegent-discovery")
            self.binary_path = Path(found) if found else None
        self.is_native = self.binary_path is not None

    def _run(self, *args: str) -> Any | None:
        if not self.is_native or self.binary_path is None:
            return None
        try:
            proc = subprocess.run(
                [str(self.binary_path), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

        if proc.returncode != 0:
            return None
        try:
            return json.loads(proc.stdout or "null")
        except json.JSONDecodeError:
            return None

    def sessions(self) -> list[dict[str, Any]]:
        out = self._run("sessions") if self.is_native else None
        return out if isinstance(out, list) else _fallback_sessions()

    def tools(self) -> list[dict[str, Any]]:
        out = self._run("tools") if self.is_native else None
        return out if isinstance(out, list) else _fallback_tools()

    def processes(self, pattern: str | None = None) -> list[dict[str, Any]]:
        out = self._run("processes", "--pattern", pattern) if (self.is_native and pattern) else (
            self._run("processes") if self.is_native else None
        )
        return out if isinstance(out, list) else _fallback_processes(pattern)

    def all(self, pattern: str | None = None) -> dict[str, Any]:
        out = self._run("all", "--pattern", pattern) if (self.is_native and pattern) else (
            self._run("all") if self.is_native else None
        )
        if isinstance(out, dict):
            return out
        return {
            "sessions": _fallback_sessions(),
            "tools": _fallback_tools(),
            "processes": _fallback_processes(pattern),
        }

    def tools_map(self) -> dict[str, bool]:
        return {item["tool"]: bool(item["available"]) for item in self.tools()}

    # Compatibility methods used by newer callers.
    def scan_agents(self) -> list[dict[str, Any]]:
        return self.processes()

    def get_system_info(self) -> dict[str, float]:
        return {"cpu_percent": 0.0, "memory_percent": 0.0}
