"""WP-4008: Discovery of external agents via sharecli and process tree."""

import contextlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class DiscoveredAgent(BaseModel):
    """Metadata for an agent discovered outside thegent's direct control."""

    pid: int
    ppid: int
    agent: str
    cwd: str
    discovered_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_seen_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    command: str | None = None
    args_preview: str | None = None
    tmux_pane: str | None = None


def register_discovered_agent(
    pid: int,
    ppid: int,
    agent: str,
    cwd: str,
    command: str | None = None,
    args_preview: str | None = None,
    session_dir: Path | None = None,
) -> Path:
    """Register or update a discovered agent in the session directory."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    base_dir = session_dir or settings.session_dir.expanduser().resolve()
    discovery_dir = base_dir / "discovered"
    discovery_dir.mkdir(parents=True, exist_ok=True)

    # We use PPID as the primary key for the "session" of the agent
    # since most agents launch subcommands from a stable parent process.
    file_path = discovery_dir / f"ppid_{ppid}.json"

    agent_data: dict[str, Any]
    if file_path.exists():
        try:
            agent_data = json.loads(file_path.read_text(encoding="utf-8"))
            agent_data["last_seen_at"] = datetime.now(UTC).isoformat()
            if command:
                agent_data["command"] = command
            if args_preview:
                agent_data["args_preview"] = args_preview
            if agent and agent != "?":
                agent_data["agent"] = agent
        except Exception as e:
            _log.warning(f"Failed to read discovered agent file {file_path}: {e}")
            agent_data = DiscoveredAgent(
                pid=pid, ppid=ppid, agent=agent, cwd=cwd, command=command, args_preview=args_preview
            ).model_dump()
    else:
        agent_data = DiscoveredAgent(
            pid=pid, ppid=ppid, agent=agent, cwd=cwd, command=command, args_preview=args_preview
        ).model_dump()

    # Try to find associated tmux pane
    from thegent.tools.terminal import list_tmux_panes

    panes = list_tmux_panes()
    for p in panes:
        # This is a heuristic: if the pane path matches the agent CWD
        # and the pane command matches the agent name or its PID is in the pane's process tree
        if p.path == cwd:
            agent_data["tmux_pane"] = p.pane_id
            break

    file_path.write_text(json.dumps(agent_data, indent=2), encoding="utf-8")
    return file_path


def list_discovered_agents(session_dir: Path | None = None) -> list[dict[str, Any]]:
    """List all currently active discovered agents."""
    from thegent.cli_impl import _is_pid_running
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    base_dir = session_dir or settings.session_dir.expanduser().resolve()
    discovery_dir = base_dir / "discovered"

    if not discovery_dir.exists():
        return []

    agents = []
    for f in discovery_dir.glob("ppid_*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ppid = data.get("ppid")
            if ppid and _is_pid_running(ppid):
                agents.append(data)
            else:
                # Cleanup stale discovery files
                with contextlib.suppress(Exception):
                    f.unlink()
        except Exception:
            continue

    return sorted(agents, key=lambda x: x.get("last_seen_at", ""), reverse=True)


def _is_triggered_by_agent_process() -> bool:
    """Check if the current process was triggered by an agent process.

    This checks the process tree (parent processes) to see if any ancestor
    is a known agent process (thegent, codex, copilot, claude, etc.).

    Returns:
        True if triggered by an agent process, False otherwise.
    """
    try:
        current = psutil.Process()

        # Check current process name
        current_name = current.name().lower()
        agent_names = {"thegent", "codex", "copilot", "claude", "cursor-agent", "opencode", "zen"}
        if any(agent in current_name for agent in agent_names):
            return True

        # Check parent process tree
        parent = current.parent()
        max_depth = 10  # Limit depth to avoid infinite loops
        depth = 0

        while parent and depth < max_depth:
            try:
                parent_name = parent.name().lower()
                if any(agent in parent_name for agent in agent_names):
                    return True

                # Check if parent is in discovered agents
                from thegent.config import ThegentSettings

                settings = ThegentSettings()
                discovery_dir = settings.session_dir.expanduser().resolve() / "discovered"
                if discovery_dir.exists():
                    ppid_file = discovery_dir / f"ppid_{parent.pid}.json"
                    if ppid_file.exists():
                        return True

                parent = parent.parent()
                depth += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        return False
    except Exception as e:
        _log.debug(f"Error checking if triggered by agent process: {e}")
        return False
