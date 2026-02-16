"""Tmux terminal interaction tools for thegent."""

import logging
import subprocess
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TmuxPane:
    pane_id: str
    session_name: str
    window_index: int
    pane_index: int
    path: str
    command: str
    title: str


def list_tmux_panes() -> list[TmuxPane]:
    """List all tmux panes with their metadata."""
    format_str = "#{pane_id} #{session_name} #{window_index} #{pane_index} #{pane_current_path} #{pane_current_command} #{pane_title}"
    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", format_str], capture_output=True, text=True, check=True
        )
        panes = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(" ", 6)
            if len(parts) < 7:
                continue
            panes.append(
                TmuxPane(
                    pane_id=parts[0],
                    session_name=parts[1],
                    window_index=int(parts[2]),
                    pane_index=int(parts[3]),
                    path=parts[4],
                    command=parts[5],
                    title=parts[6],
                )
            )
        return panes
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list tmux panes: {e.stderr}")
        return []
    except Exception as e:
        logger.error(f"Error listing tmux panes: {e}")
        return []


def capture_tmux_pane(pane_id: str, last_lines: int = 50) -> str:
    """Capture the content of a tmux pane."""
    try:
        # Capture the pane
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", pane_id, "-p"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.split("\n")
        if last_lines > 0:
            return "\n".join(lines[-last_lines:])
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to capture tmux pane {pane_id}: {e.stderr}")
        return ""


def send_to_tmux_pane(pane_id: str, text: str, enter: bool = True) -> bool:
    """Send text/keys to a tmux pane."""
    try:
        cmd = ["tmux", "send-keys", "-t", pane_id, text]
        if enter:
            cmd.append("Enter")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to send keys to tmux pane {pane_id}: {e.stderr}")
        return False


def is_claude_code_pane(pane: TmuxPane) -> bool:
    """Heuristic to detect if a pane is running Claude Code."""
    # Check command and title
    if any(x in pane.command.lower() for x in ["node", "claude"]):
        # Often claude code has 'claude' in title or content
        # We can also check content
        content = capture_tmux_pane(pane.pane_id, last_lines=10)
        if "Claude" in content or "CC:" in pane.title:
            return True
    return False
