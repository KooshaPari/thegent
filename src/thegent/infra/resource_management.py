"""Phase 17: Resource Management implementation.
Includes memory limits, process limits, and FD budget monitoring.
"""

import logging
import os
import resource
from typing import Any, Dict, List

import psutil

logger = logging.getLogger(__name__)


class ResourceManager:
    """Manages resource limits for agent processes."""

    def __init__(self) -> None:
        pass

    def apply_limits(self, memory_mb: int = 512, proc_limit: int = 100):
        """Apply soft/hard limits using resource module."""
        try:
            # Memory limit (RLIMIT_AS - Address Space)
            mem_bytes = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            # Process count limit
            resource.setrlimit(resource.RLIMIT_NPROC, (proc_limit, proc_limit))

            # File descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))

            logger.info(f"Applied resource limits: Mem={memory_mb}MB, Procs={proc_limit}")
        except Exception as e:
            logger.error(f"Failed to apply resource limits: {e}")

    def monitor_usage(self, pid: int) -> dict[str, Any]:
        """Monitor current resource usage of a process."""
        try:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            fd_count = proc.num_fds()
            children = proc.children(recursive=True)

            return {
                "pid": pid,
                "memory_rss": mem_info.rss,
                "memory_vms": mem_info.vms,
                "fd_count": fd_count,
                "child_count": len(children),
                "status": proc.status(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"error": "Process not accessible"}


class FDBudget:
    """Monitors and alerts on File Descriptor budget."""

    def __init__(self, threshold: float = 0.8) -> None:
        self.threshold = threshold

    def check(self, current: int, limit: int) -> bool:
        usage = current / limit
        if usage > self.threshold:
            logger.warning(f"FD usage critical: {current}/{limit} ({usage:.1%})")
            return False
        return True
