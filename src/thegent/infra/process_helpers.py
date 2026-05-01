"""Process utility helpers — shared infrastructure primitives.

This module contains low-level OS/process primitives with no thegent domain
dependencies. It lives in ``infra`` so it can be imported by any layer without
creating import cycles.
"""

from __future__ import annotations

import os


def is_pid_running(pid: int) -> bool:
    """Check whether a process with the given PID is still running.

    Uses ``os.kill(pid, 0)`` which sends no signal but checks whether
    the process exists and the caller has permission to send signals to it.

    Args:
        pid: Process ID to check.

    Returns:
        True if the process is running, False otherwise.
    """
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
