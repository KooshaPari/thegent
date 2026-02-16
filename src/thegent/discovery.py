"""WP-4008: Discovery of external agents via sharecli and process tree."""

import contextlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
