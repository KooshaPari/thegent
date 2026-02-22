"""Process enumeration and agent detection for heliosShield."""

import platform
import re
import subprocess
from pathlib import Path
from typing import Any


def get_processes() -> list[dict[str, Any]]:
    """Get list of running processes with PIDs and command lines.

    Uses /proc on Linux and ps on macOS.
    """
    processes = []
    system = platform.system().lower()

    if system == "linux":
        # Linux /proc scan
        for pid_path in Path("/proc").iterdir():
            pid_str = pid_path.name
            if not pid_path.is_dir() or not pid_str.isdigit():
                continue
            pid = int(pid_str)
            try:
                with open(f"/proc/{pid}/cmdline", "rb") as f:
                    cmdline = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
                if cmdline:
                    processes.append({"pid": pid, "cmd": cmdline})
            except OSError:
                continue
    elif system == "darwin":
        # macOS ps scan
        try:
            output = subprocess.check_output(["ps", "-ax", "-o", "pid,command"], stderr=subprocess.STDOUT).decode(
                "utf-8"
            )
            lines = output.splitlines()[1:]  # skip header
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                match = re.match(r"^(\d+)\s+(.+)$", line)
                if match:
                    processes.append({"pid": int(match.group(1)), "cmd": match.group(2)})
        except subprocess.CalledProcessError:
            pass

    return processes


def detect_agents(patterns: dict[str, str]) -> list[dict[str, Any]]:
    """Detect known agents from running processes using regex patterns.

    Args:
        patterns: Dict of agent name -> regex pattern
    """
    processes = get_processes()
    detected = []

    for proc in processes:
        for name, pattern in patterns.items():
            if re.search(pattern, proc["cmd"], re.IGNORECASE):
                detected.append({"agent": name, "pid": proc["pid"], "cmd": proc["cmd"]})
                break  # only detect one agent per PID

    return detected


if __name__ == "__main__":
    # Simple test

    # Example agent patterns
    agent_patterns = {
        "claude": r"claude-code|clode",
        "cursor": r"cursor-agent|cursor",
        "thegent": r"thegent",
        "codex": r"codex",
        "copilot": r"copilot",
    }

    found = detect_agents(agent_patterns)
    for _a in found:
        pass
