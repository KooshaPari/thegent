"""Session diagnostics TUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import psutil
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from thegent.cli.commands.impl import ps_impl, session_meta_impl


class SessionTUI:
    """Render session summaries with degraded-state diagnostics."""

    def __init__(self) -> None:
        self.running = False
        self._last_diag: dict[str, Any] | None = None

    def run(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def _diag(self, component: str, session_id: str, failure_type: str, message: str) -> dict[str, Any]:
        return {
            "component": component,
            "session_id": session_id,
            "failure_type": failure_type,
            "error_message": message,
        }

    def _get_subagents_for_session(self, session_id: str) -> list[dict[str, Any]]:
        meta = session_meta_impl(session_id)
        if meta.get("error"):
            self._last_diag = self._diag("subagents", session_id, "metadata_error", str(meta["error"]))
            return []
        pid = int(meta.get("pid") or 0)
        if pid <= 0 or not _is_pid_running(pid):
            return []
        try:
            children = psutil.Process(pid).children(recursive=True)
        except Exception as exc:  # noqa: BLE001 - surfaced as diagnostics.
            self._last_diag = self._diag("subagents", session_id, "process_probe_error", str(exc))
            return []
        entries: list[dict[str, Any]] = []
        for child in children:
            cmdline = _safe_call(child.cmdline, [])
            command = " ".join(cmdline)
            entries.append(
                {
                    "pid": child.pid,
                    "ppid": _safe_call(child.ppid, None),
                    "agent": _agent_name(command),
                    "cmdline": cmdline,
                    "cpu_percent": _safe_call(child.cpu_percent, 0.0),
                    "memory_rss": getattr(_safe_call(child.memory_info, None), "rss", None),
                    "status": _safe_call(child.status, "unknown"),
                    "num_fds": _safe_call(child.num_fds, None),
                    "create_time": _safe_call(child.create_time, None),
                }
            )
        return entries

    def _get_session_details(self, session_id: str) -> dict[str, Any]:
        details = dict(session_meta_impl(session_id))
        details.setdefault("id", session_id)
        diagnostics: dict[str, Any] = {}
        try:
            meta_path = _find_session_meta(None, session_id)
            details["log_paths"] = {"meta": str(meta_path)}
        except FileNotFoundError as exc:
            diagnostics["log_paths"] = self._diag("log_paths", session_id, "meta_missing", str(exc))
        except Exception as exc:  # noqa: BLE001
            diagnostics["log_paths"] = self._diag("log_paths", session_id, "path_resolution_error", str(exc))
        self._last_diag = None
        details["subagents"] = self._get_subagents_for_session(session_id)
        if self._last_diag is not None:
            diagnostics["subagents"] = self._last_diag
        if diagnostics:
            details["degraded"] = True
            details["diagnostics"] = diagnostics
        return details

    def render_sessions_list(self) -> Layout:
        rows = ps_impl()
        if isinstance(rows, dict):
            rows = rows.get("sessions", [])
        table = Table("ID", "Status", "Agent", "Diag")
        for row in rows:
            session_id = str(row.get("id", ""))
            details = self._get_session_details(session_id)
            diag = "ERR" if details.get("degraded") else ""
            table.add_row(session_id, str(row.get("status", "")), str(row.get("agent", "")), diag)
        layout = Layout()
        layout.split_column(Layout(Panel("Sessions"), name="header"), Layout(Panel(table), name="main"))
        return layout

    def render_session_view(self, session_id: str) -> Layout:
        details = self._get_session_details(session_id)
        badge = " DEGRADED" if details.get("degraded") else ""
        header = Panel(f"{session_id}{badge}")
        body = Panel(str(details.get("subagents", [])))
        layout = Layout()
        layout.split_column(Layout(header, name="header"), Layout(body, name="main"))
        return layout


def _safe_call(func: Any, default: Any) -> Any:
    try:
        return func()
    except Exception:
        return default


def _agent_name(command: str) -> str:
    lowered = command.lower()
    for name in ("codex", "claude", "agent"):
        if name in lowered:
            return name
    return "unknown"


def _is_pid_running(pid: int) -> bool:
    return pid > 0 and psutil.pid_exists(pid)


def _find_session_meta(_settings: Any, session_id: str) -> Path:
    raise FileNotFoundError(session_id)


__all__ = ["SessionTUI"]
