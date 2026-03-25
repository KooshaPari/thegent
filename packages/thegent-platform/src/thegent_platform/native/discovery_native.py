"""BKM-08: discovery client with native binary first, Python fallback second."""

from __future__ import annotations

import orjson as json
import logging
import os
import re
import shutil
import subprocess
from thegent_core.infra.shim_subprocess import run as shim_run
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


def _bounded_text(value: str | None, limit: int = 200) -> str:
    """Return a bounded single-line diagnostic string."""
    text = (value or "").strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _fallback_sessions(*, include_meta: bool = False) -> list[dict[str, Any]] | dict[str, Any]:
    """Collect tmux sessions via shell command output."""
    sessions: list[dict[str, Any]] = []
    fmt = "#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}"
    metadata: dict[str, Any] = {
        "source": "tmux",
        "status": "ok",
        "session_count": 0,
    }
    try:
        proc = shim_run(
            ["tmux", "list-sessions", "-F", fmt],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except subprocess.TimeoutExpired as exc:
        metadata.update(
            {
                "status": "probe_failed",
                "error_type": "timeout",
                "detail": _bounded_text(str(exc)),
            }
        )
        payload = {"sessions": sessions, "fallback": metadata}
        return payload if include_meta else sessions
    except FileNotFoundError as exc:
        metadata.update(
            {
                "status": "probe_failed",
                "error_type": "tmux_missing",
                "detail": _bounded_text(str(exc)),
            }
        )
        payload = {"sessions": sessions, "fallback": metadata}
        return payload if include_meta else sessions
    except OSError as exc:
        metadata.update(
            {
                "status": "probe_failed",
                "error_type": "launch_failed",
                "detail": _bounded_text(str(exc)),
            }
        )
        payload = {"sessions": sessions, "fallback": metadata}
        return payload if include_meta else sessions

    if proc.returncode != 0:
        metadata.update(
            {
                "status": "probe_failed",
                "error_type": "nonzero_exit",
                "returncode": proc.returncode,
                "detail": _bounded_text(proc.stderr),
            }
        )
        payload = {"sessions": sessions, "fallback": metadata}
        return payload if include_meta else sessions

    malformed_lines = 0
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 3)
        if len(parts) != 4:
            malformed_lines += 1
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

    metadata["session_count"] = len(sessions)
    if not malformed_lines and not sessions:
        metadata["status"] = "empty"
    if malformed_lines > 0:
        metadata["malformed_lines"] = malformed_lines
        metadata["status"] = "parse_failed"
        metadata["error_type"] = "malformed_output"

    payload = {"sessions": sessions, "fallback": metadata}
    return payload if include_meta else sessions


def _fallback_tools(*, include_meta: bool = False) -> list[dict[str, Any]] | dict[str, Any]:
    """Collect tool availability from PATH lookup."""
    tools: list[dict[str, Any]] = []
    available = 0
    for tool in _PROBE_TOOLS:
        path = shutil.which(tool)
        tools.append({"tool": tool, "available": path is not None, "path": path})
        if path is not None:
            available += 1

    metadata: dict[str, Any] = {
        "source": "path_probe",
        "status": "ok",
        "tools_count": len(_PROBE_TOOLS),
        "available_count": available,
        "command_count": len(tools),
    }
    payload: dict[str, Any] = {"tools": tools, "fallback": metadata}
    return payload if include_meta else tools


def _fallback_processes(
    pattern: str | None = None, *, include_meta: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """Collect matching processes with psutil."""
    metadata: dict[str, Any] = {
        "source": "psutil",
        "status": "ok",
        "process_count": 0,
        "pattern": pattern or _DEFAULT_PATTERN,
    }
    try:
        import psutil
    except Exception:
        metadata.update({"status": "probe_failed", "error_type": "psutil_missing"})
        payload: dict[str, Any] = {"processes": [], "fallback": metadata}
        return payload if include_meta else payload["processes"]

    patt = pattern or _DEFAULT_PATTERN
    try:
        regex = re.compile(patt, re.IGNORECASE)
    except re.error:
        metadata.update({"status": "probe_failed", "error_type": "invalid_pattern"})
        payload = {"processes": [], "fallback": metadata}
        return payload if include_meta else payload["processes"]

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
    metadata["process_count"] = len(matched)
    payload = {"processes": matched, "fallback": metadata}
    return payload if include_meta else matched


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
        self._last_run_diagnostics: dict[str, Any] | None = None
        self._last_fallback_metadata: dict[str, Any] = {}

    @property
    def last_run_diagnostics(self) -> dict[str, Any] | None:
        return self._last_run_diagnostics

    @property
    def last_fallback_metadata(self) -> dict[str, Any]:
        return dict(self._last_fallback_metadata)

    def _normalize_fallback_payload(self, component: str, payload: Any) -> list[dict[str, Any]]:
        items: Any = []
        fallback_payload: dict[str, Any] | None = None
        if isinstance(payload, dict):
            if component in payload and isinstance(payload[component], list):
                items = payload[component]
            fallback_payload = payload.get("fallback")
            if not isinstance(fallback_payload, dict):
                fallback_payload = None
        elif isinstance(payload, list):
            items = payload

        self._last_fallback_metadata[component] = self._fallback_metadata(component, fallback_payload)
        if isinstance(items, list):
            return items
        return []

    def _record_run_diagnostic(self, payload: dict[str, Any], *, log_warning: bool = False) -> None:
        self._last_run_diagnostics = payload
        if log_warning:
            _log.warning("discovery_native_run_failed %s", payload)

    def _fallback_metadata(self, component: str, fallback_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "component": component,
            "source": "native_fallback",
        }
        if fallback_payload is not None:
            merged_payload = {k: v for k, v in fallback_payload.items() if k != "status"}
            fallback_status = str(fallback_payload.get("status", "degraded") or "degraded")
            metadata.update(merged_payload)
            metadata["status"] = fallback_status
        else:
            metadata["status"] = "degraded"

        if self.is_native:
            if self.last_run_diagnostics:
                metadata["native_run"] = self.last_run_diagnostics
            elif self.binary_path is not None:
                metadata["native_run"] = {"status": "not_executed", "reason": "unexpected_payload_shape"}
        else:
            metadata["native_run"] = {"status": "disabled", "reason": "missing_discovery_binary"}

        return metadata

    def _run(self, *args: str) -> Any | None:
        if not self.is_native or self.binary_path is None:
            self._last_run_diagnostics = None
            return None
        try:
            proc = shim_run(
                [str(self.binary_path), *args],
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
        except subprocess.TimeoutExpired as exc:
            self._record_run_diagnostic(
                {
                    "status": "error",
                    "error_type": "timeout",
                    "args": list(args),
                    "detail": _bounded_text(str(exc)),
                }
            )
            return None
        except FileNotFoundError as exc:
            self._record_run_diagnostic(
                {
                    "status": "error",
                    "error_type": "binary_missing",
                    "args": list(args),
                    "detail": _bounded_text(str(exc)),
                },
                log_warning=True,
            )
            return None
        except OSError as exc:
            self._record_run_diagnostic(
                {
                    "status": "error",
                    "error_type": "launch_failed",
                    "args": list(args),
                    "detail": _bounded_text(str(exc)),
                },
                log_warning=True,
            )
            return None

        if proc.returncode != 0:
            self._record_run_diagnostic(
                {
                    "status": "error",
                    "error_type": "nonzero_exit",
                    "args": list(args),
                    "returncode": proc.returncode,
                    "stderr": _bounded_text(proc.stderr),
                },
                log_warning=True,
            )
            return None
        try:
            parsed = json.loads(proc.stdout or "null")
        except json.JSONDecodeError as exc:
            self._record_run_diagnostic(
                {
                    "status": "error",
                    "error_type": "invalid_json",
                    "args": list(args),
                    "detail": _bounded_text(str(exc)),
                    "stdout_snippet": _bounded_text(proc.stdout),
                },
                log_warning=True,
            )
            return None
        self._last_run_diagnostics = {"status": "ok", "args": list(args)}
        return parsed

    def sessions(self) -> list[dict[str, Any]]:
        out = self._run("sessions") if self.is_native else None
        if isinstance(out, list):
            self._last_fallback_metadata.pop("sessions", None)
            return out
        payload = _fallback_sessions(include_meta=True)
        return self._normalize_fallback_payload("sessions", payload)

    def tools(self) -> list[dict[str, Any]]:
        out = self._run("tools") if self.is_native else None
        if isinstance(out, list):
            self._last_fallback_metadata.pop("tools", None)
            return out
        payload = _fallback_tools(include_meta=True)
        return self._normalize_fallback_payload("tools", payload)

    def processes(self, pattern: str | None = None) -> list[dict[str, Any]]:
        out = (
            self._run("processes", "--pattern", pattern)
            if (self.is_native and pattern)
            else (self._run("processes") if self.is_native else None)
        )
        if isinstance(out, list):
            self._last_fallback_metadata.pop("processes", None)
            return out
        payload = _fallback_processes(pattern, include_meta=True)
        return self._normalize_fallback_payload("processes", payload)

    def all(self, pattern: str | None = None) -> dict[str, Any]:
        out = (
            self._run("all", "--pattern", pattern)
            if (self.is_native and pattern)
            else (self._run("all") if self.is_native else None)
        )
        if isinstance(out, dict):
            return out
        session_payload = _fallback_sessions(include_meta=True)
        tools_payload = _fallback_tools(include_meta=True)
        processes_payload = _fallback_processes(pattern, include_meta=True)
        return {
            "sessions": self._normalize_fallback_payload("sessions", session_payload),
            "tools": self._normalize_fallback_payload("tools", tools_payload),
            "processes": self._normalize_fallback_payload("processes", processes_payload),
            "fallback_metadata": dict(self._last_fallback_metadata),
        }

    def tools_map(self) -> dict[str, bool]:
        return {item["tool"]: bool(item["available"]) for item in self.tools()}

    # Compatibility methods used by newer callers.
    def scan_agents(self) -> list[dict[str, Any]]:
        return self.processes()

    def get_system_info(self) -> dict[str, float]:
        return {"cpu_percent": 0.0, "memory_percent": 0.0}
