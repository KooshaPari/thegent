"""Process utilities for doctor.

Extracted from doctor.py.
"""

import psutil
from typing import Any


class ProcessInfo:
    """Process information."""
    def __init__(self, pid: int, name: str, status: str):
        self.pid = pid
        self.name = name
        self.status = status


def is_process_working(pid: int, min_cpu: float = 0.1, min_io: int = 1024) -> tuple[bool, str]:
    """Check if process is actively working."""
    try:
        proc = psutil.Process(pid)
        cpu = proc.cpu_percent(interval=0.1)
        io = proc.io_counters().read_bytes if proc.io_counters() else 0

        if cpu > min_cpu or io > min_io:
            return True, f"cpu={cpu}%"
        return False, "idle"
    except Exception as e:
        return False, str(e)


def find_stuck_processes(patterns: list[str], max_age: int = 300) -> list[tuple[int, str, str]]:
    """Find stuck processes matching patterns."""
    stuck = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if any(p in proc.info['name'] for p in patterns):
                stuck.append((proc.info['pid'], proc.info['name'], "stuck"))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return stuck


def extract_process_info(proc: psutil.Process) -> ProcessInfo | None:
    """Extract process info."""
    try:
        return ProcessInfo(
            pid=proc.pid,
            name=proc.name(),
            status=proc.status()
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


__all__ = ["ProcessInfo", "extract_process_info", "find_stuck_processes", "is_process_working"]
