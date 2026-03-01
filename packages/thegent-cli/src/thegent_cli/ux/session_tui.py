"""Rich TUI for session management with subagent monitoring and control."""

import logging
import os
import signal
from typing import Any

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from thegent.cli.commands.impl import (
    _find_session_meta,
    _is_pid_running,
    _read_session_meta,
    ps_impl,
    session_meta_impl,
)
from thegent.config import ThegentSettings

_LOG = logging.getLogger(__name__)


class SessionTUI:
    """Rich-based TUI for session management with subagent monitoring."""

    def __init__(self, session_id: str | None = None) -> None:
        self.session_id = session_id
        self.console = Console()
        self.settings = ThegentSettings()
        self._last_diag: dict[str, Any] | None = None

    def _get_subagents_for_session(self, session_id: str) -> list[dict[str, Any]]:
        """Get subagents (child processes) for a session."""
        self._last_diag = None

        def _record_subagent_failure(extra: dict[str, Any]) -> None:
            self._last_diag = {
                "component": "subagents",
                "session_id": session_id,
                **extra,
            }
            _LOG.warning("session_tui_subagent_probe_failed", extra=self._last_diag)

        def _normalize_cmd_line(cmdline: list[str]) -> str:
            return " ".join(cmdline[:3]) if len(cmdline) > 0 else ""

        try:
            meta = session_meta_impl(session_id)
        except (RuntimeError, ValueError, OSError, TypeError) as exc:
            _record_subagent_failure(
                {
                    "failure_type": "metadata_lookup_failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            return []

        if "error" in meta:
            _record_subagent_failure(
                {
                    "failure_type": "metadata_error",
                    "error_message": str(meta.get("error")),
                }
            )
            return []

        try:
            pid = meta.get("pid", 0)
            if not pid or not _is_pid_running(pid):
                return []
        except (RuntimeError, TypeError, ValueError) as exc:
            _record_subagent_failure(
                {
                    "failure_type": "pid_probe_failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            return []

        # QOL: Enhanced human-only monitoring
        is_agent = self.settings.agent_id != "default-agent"

        # Find child processes
        subagents = []
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                try:
                    cmd_str = _normalize_cmd_line(child.cmdline())

                    # Check if it's an agent process
                    cmd_lower = cmd_str.lower()
                    agent_name = "unknown"
                    if any(
                        agent in cmd_lower
                        for agent in ["thegent", "codex", "copilot", "claude", "cursor", "uv", "bun", "cargo"]
                    ):
                        if "thegent" in cmd_lower:
                            agent_name = "thegent"
                        elif "codex" in cmd_lower:
                            agent_name = "codex"
                        elif "copilot" in cmd_lower:
                            agent_name = "copilot"
                        elif "claude" in cmd_lower:
                            agent_name = "claude"
                        elif "cursor" in cmd_lower:
                            agent_name = "cursor"
                        elif "uv" in cmd_lower:
                            agent_name = "uv"
                        elif "bun" in cmd_lower:
                            agent_name = "bun"
                        elif "cargo" in cmd_lower:
                            agent_name = "cargo"

                    # DX: Richer info for humans
                    cpu_percent = child.cpu_percent(interval=0.1)
                    memory_info = child.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024

                    subagents.append(
                        {
                            "pid": child.pid,
                            "ppid": child.ppid(),
                            "agent": agent_name,
                            "cmd": cmd_str[:60] + ("..." if len(cmd_str) > 60 else ""),
                            "memory_mb": memory_mb,
                            "cpu_percent": cpu_percent,
                            "status": child.status(),
                            "num_fds": child.num_fds() if not is_agent and hasattr(child, "num_fds") else "N/A",
                            "create_time": child.create_time(),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):  # noqa: PERF203 - intentional per-item error handling
                    continue
        except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
            _record_subagent_failure(
                {
                    "failure_type": "child_enumeration_failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
        except (RuntimeError, ValueError, OSError) as exc:
            _record_subagent_failure(
                {
                    "failure_type": "enumeration_failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

        return subagents

    def _get_session_details(self, session_id: str) -> dict[str, Any]:
        """Get detailed session information."""
        meta = session_meta_impl(session_id)
        if "error" in meta:
            return meta

        # Add subagents
        meta["subagents"] = self._get_subagents_for_session(session_id)
        if self._last_diag:
            meta["degraded"] = True
            meta.setdefault("diagnostics", {})["subagents"] = self._last_diag

        # Add log paths
        try:
            meta_path = _find_session_meta(self.settings, session_id)
            session_dir = meta_path.parent
            meta["log_paths"] = {
                "stdout": str(session_dir / f"{session_id}.stdout.log"),
                "stderr": str(session_dir / f"{session_id}.stderr.log"),
            }
        except FileNotFoundError as exc:
            diag = {
                "component": "log_paths",
                "session_id": session_id,
                "failure_type": "meta_missing",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _LOG.warning("session_tui_log_path_resolution_failed", extra=diag)
            meta["degraded"] = True
            meta.setdefault("diagnostics", {})["log_paths"] = diag
        except (RuntimeError, ValueError, TypeError, OSError) as exc:
            diag = {
                "component": "log_paths",
                "session_id": session_id,
                "failure_type": "path_resolution_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            _LOG.warning("session_tui_log_path_resolution_failed", extra=diag)
            meta["degraded"] = True
            meta.setdefault("diagnostics", {})["log_paths"] = diag
        return meta

    def render_session_view(self, session_id: str) -> Layout:
        """Render detailed view for a specific session."""
        details = self._get_session_details(session_id)

        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=3))

        # Header
        status = details.get("status", "unknown")
        status_color = "green" if status == "running" else "yellow" if "exited" in status else "red"
        degraded_badge = " | [bold yellow]DEGRADED[/bold yellow]" if details.get("degraded") else ""
        layout["header"].update(
            Panel(
                f"[bold cyan]Session:[/bold cyan] {session_id[:20]}... | "
                f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}] | "
                f"[bold]Agent:[/bold] {details.get('agent', '?')} | "
                f"[bold]PID:[/bold] {details.get('pid', 'N/A')}{degraded_badge}",
                border_style="cyan",
            )
        )

        # Main content - split into Session Info, Subagents, and Logs preview
        layout["main"].split_row(
            Layout(name="info"),
            Layout(name="subagents"),
        )
        layout["info"].split_column(
            Layout(name="session_info"),
            Layout(name="logs_preview"),
        )

        # Session Info Panel
        info_table = Table(title="Session Details", show_header=True, header_style="bold magenta", box=None)
        info_table.add_column("Field", style="cyan", width=20)
        info_table.add_column("Value", style="green")

        for key in ["owner", "model", "mode", "started_at_utc", "prompt"]:
            value = details.get(key, "N/A")
            if key == "prompt" and isinstance(value, str) and len(value) > 80:
                value = value[:80] + "..."
            info_table.add_row(key.replace("_", " ").title(), str(value))

        layout["session_info"].update(Panel(info_table, border_style="magenta", title="Session Info"))

        # Subagents Table
        subagents = details.get("subagents", [])
        subagents_table = Table(title=f"Subagents ({len(subagents)})", show_header=True, header_style="bold yellow")
        subagents_table.add_column("PID", style="cyan", width=8)
        subagents_table.add_column("Agent", style="magenta", width=12)
        subagents_table.add_column("Memory", style="green", width=10)
        subagents_table.add_column("CPU %", style="yellow", width=8)
        subagents_table.add_column("Status", style="cyan", width=10)
        subagents_table.add_column("Command", style="dim", no_wrap=False)

        if subagents:
            for sa in subagents:
                subagents_table.add_row(
                    str(sa.get("pid", "N/A")),
                    sa.get("agent", "unknown"),
                    f"{sa.get('memory_mb', 0):.1f}MB",
                    f"{sa.get('cpu_percent', 0):.1f}%",
                    sa.get("status", "unknown"),
                    sa.get("cmd", "")[:50],
                )
        else:
            subagents_table.add_row("—", "—", "—", "—", "—", "No subagents found")

        layout["subagents"].update(Panel(subagents_table, border_style="yellow", title="Subagents"))

        # Logs Preview
        logs_text = Text("Logs preview (use 'thegent logs <session_id>' for full logs)", style="dim")
        log_paths = details.get("log_paths", {})
        if log_paths:
            stdout_path = log_paths.get("stdout", "")
            if stdout_path:
                from thegent.utils.helpers import read_file_tail

                lines = read_file_tail(stdout_path, num_lines=10)
                if lines:
                    logs_text = Text("\n".join(lines), style="dim")

        layout["logs_preview"].update(Panel(logs_text, border_style="blue", title="Recent Logs"))

        # Footer with actions
        footer_text = Text(
            "[dim]Actions:[/dim] [bold]s[/bold]=stop [bold]p[/bold]=pause [bold]r[/bold]=resume "
            "[bold]l[/bold]=logs [bold]q[/bold]=quit",
            style="dim",
        )
        layout["footer"].update(Panel(footer_text, border_style="dim"))

        return layout

    def render_sessions_list(self) -> Layout:
        """Render list of all sessions."""
        sessions = ps_impl(all=True)
        running = [s for s in sessions if s.get("status") == "running"]

        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=2))

        # Header
        layout["header"].update(
            Panel(
                f"[bold cyan]thegent Session Manager[/bold cyan] | "
                f"Total: {len(sessions)} | Running: {len(running)} | Exited: {len(sessions) - len(running)}",
                border_style="cyan",
            )
        )

        # Main - Sessions table
        sessions_table = Table(title="Sessions", show_header=True, header_style="bold magenta", expand=True)
        sessions_table.add_column("ID", style="cyan", width=20)
        sessions_table.add_column("Agent", style="magenta", width=12)
        sessions_table.add_column("Status", style="yellow", width=12)
        sessions_table.add_column("PID", style="green", width=8)
        sessions_table.add_column("Memory", style="blue", width=12)
        sessions_table.add_column("Subagents", style="cyan", width=10)
        sessions_table.add_column("Prompt", style="dim", no_wrap=False)

        for s in sessions[:50]:  # Limit to 50 for performance
            session_id = s.get("id", "N/A")
            status = s.get("status", "unknown")
            status_color = "green" if status == "running" else "yellow"

            # Get subagent count
            subagent_count = "0"
            if status == "running":
                subagents = self._get_subagents_for_session(session_id)
                if self._last_diag and self._last_diag.get("component") == "subagents":
                    subagent_count = "ERR"
                else:
                    subagent_count = str(len(subagents))

            prompt_preview = s.get("prompt_preview", "")[:40] + ("..." if len(s.get("prompt_preview", "")) > 40 else "")

            # Get memory info
            pid = s.get("pid", 0)
            memory_str = "—"
            if pid and status == "running":
                try:
                    import psutil

                    proc = psutil.Process(pid)
                    mem = proc.memory_info()
                    memory_str = f"{mem.rss / 1024 / 1024:.1f}MB"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    memory_str = "—"

            session_id_str = str(session_id) if session_id else "N/A"
            sessions_table.add_row(
                session_id_str[:20] + ("..." if len(session_id_str) > 20 else ""),
                s.get("agent", "?"),
                f"[{status_color}]{status}[/{status_color}]",
                str(pid) if pid else "N/A",
                memory_str,
                str(subagent_count),
                prompt_preview,
            )

        layout["main"].update(Panel(sessions_table, border_style="magenta"))

        # Footer
        footer_text = Text(
            "[dim]Select session ID to view details | [bold]q[/bold]=quit [bold]r[/bold]=refresh", style="dim"
        )
        layout["footer"].update(Panel(footer_text, border_style="dim"))

        return layout

    def show(self, session_id: str | None = None) -> None:
        """Show session view (single session or list)."""
        if session_id:
            self.console.print(self.render_session_view(session_id))
        else:
            self.console.print(self.render_sessions_list())

    def watch(self, session_id: str | None = None, interval: float = 2.0) -> None:
        """Watch sessions live with auto-refresh."""
        if session_id:
            with Live(self.render_session_view(session_id), refresh_per_second=1 / interval, screen=False) as live:
                try:
                    import time

                    while True:
                        live.update(self.render_session_view(session_id))
                        time.sleep(interval)
                except KeyboardInterrupt:
                    pass
        else:
            with Live(self.render_sessions_list(), refresh_per_second=1 / interval, screen=False) as live:
                try:
                    import time

                    while True:
                        live.update(self.render_sessions_list())
                        time.sleep(interval)
                except KeyboardInterrupt:
                    pass

    def manage_session(self, session_id: str, action: str) -> dict[str, Any]:
        """Manage a session (stop, pause, resume, logs)."""
        try:
            meta = session_meta_impl(session_id)
            if "error" in meta:
                return {"error": meta["error"]}

            pid = meta.get("pid", 0)
            if not pid:
                return {"error": "No PID found for session"}

            if action == "stop":
                if _is_pid_running(pid):
                    os.kill(pid, signal.SIGTERM)
                    return {"success": True, "message": f"Sent SIGTERM to session {session_id}"}
                return {"error": "Process not running"}

            if action == "kill":
                if _is_pid_running(pid):
                    os.kill(pid, signal.SIGKILL)
                    return {"success": True, "message": f"Sent SIGKILL to session {session_id}"}
                return {"error": "Process not running"}

            if action == "pause":
                # Mark as paused in registry
                from thegent.execution import RunRegistry

                registry = RunRegistry(self.settings.session_dir)
                meta_path = _find_session_meta(self.settings, session_id)
                m = _read_session_meta(meta_path)
                run_id = m.get("run_id")
                if run_id:
                    registry.register_pause(run_id, reason="user_pause")
                return {"success": True, "message": f"Session {session_id} marked as paused"}

            if action == "resume":
                # Mark as running in registry
                from thegent.execution import RunRegistry

                registry = RunRegistry(self.settings.session_dir)
                meta_path = _find_session_meta(self.settings, session_id)
                m = _read_session_meta(meta_path)
                run_id = m.get("run_id")
                if run_id:
                    registry.register_resume(run_id)
                return {"success": True, "message": f"Session {session_id} marked as resumed"}

            if action == "logs":
                log_paths = self._get_session_details(session_id).get("log_paths", {})
                return {"success": True, "log_paths": log_paths}

            return {"error": f"Unknown action: {action}"}

        except Exception as e:
            return {"error": str(e)}
