import logging
import os
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TmuxPane:
    pane_id: str
    session_name: str
    window_index: str
    pane_index: str
    path: str
    command: str
    title: str
    tty: str


def list_tmux_panes() -> list[TmuxPane]:
    """List all tmux panes with detailed info."""
    # Construct likely tmux socket paths from tempdir and uid to avoid hardcoded /tmp paths
    sockets = [
        None,
        str(Path(tempfile.gettempdir()) / f"tmux-{os.getuid()}" / "default"),
        str(Path(tempfile.gettempdir()) / "../private" / f"tmux-{os.getuid()}" / "default"),
    ]

    for socket in sockets:
        cmd = ["tmux"]
        if socket:
            cmd.extend(["-S", socket])
        # Add #{pane_tty} to match with ps output
        cmd.extend(
            [
                "list-panes",
                "-a",
                "-F",
                "#{pane_id}|#{session_name}|#{window_index}|#{pane_index}|#{pane_current_path}|#{pane_current_command}|#{pane_title}|#{pane_tty}",
            ]
        )

        try:
            result = shim_run(cmd, capture_output=True, text=True, check=True)
            panes = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) == 8:
                    panes.append(
                        TmuxPane(
                            pane_id=parts[0],
                            session_name=parts[1],
                            window_index=parts[2],
                            pane_index=parts[3],
                            path=parts[4],
                            command=parts[5],
                            title=parts[6],
                            tty=parts[7],
                        )
                    )
            return panes
        except Exception:
            continue

    return []


def is_claude_code_pane(pane: TmuxPane) -> bool:
    """Detect if a pane is likely running Claude Code."""
    # Check command name or title or common session names
    cmd = pane.command.lower()
    if "claude" in cmd or "clode" in cmd:
        return True

    # Check process list in pane? (More expensive)
    return False


def capture_tmux_pane(pane_id: str, last_lines: int = 50) -> str:
    """Capture pane content."""
    cmd = ["tmux", "capture-pane", "-p", "-t", pane_id, "-S", f"-{last_lines}"]
    try:
        result = shim_run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def send_to_tmux_pane(pane_id: str, text: str, enter: bool = True) -> bool:
    """Send keys to pane."""
    cmd = ["tmux", "send-keys", "-t", pane_id, text]
    if enter:
        cmd.append("C-m")
    try:
        shim_run(cmd, check=True)
        return True
    except Exception:
        return False


def heliosShield_status() -> str:
    """Get status from thegent.mesh."""
    # Look for heliosShield in parent dir or path
    try:
        # Prefer direct execution if available
        result = shim_run(["../heliosShield/bin/harness", "status"], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception:
        try:
            result = shim_run(["harness", "status"], capture_output=True, text=True, check=True)
            return result.stdout
        except Exception:
            return "heliosShield harness not found"
