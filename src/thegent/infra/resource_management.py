"""Phase 17: Resource Management implementation.
Includes memory limits, process limits, and FD budget monitoring.
"""

import logging
import os
import resource
from typing import Any

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
        """Monitor current resource usage of a process and record to SHM."""
        try:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            cpu_percent = proc.cpu_percent(interval=0.1)
            fd_count = proc.num_fds()
            children = proc.children(recursive=True)

            # Record to SHM for global observability
            try:
                from thegent_shm import record_resource_usage

                record_resource_usage(pid, cpu_percent, mem_info.rss // 1024)
            except (ImportError, RuntimeError):
                pass

            return {
                "pid": pid,
                "memory_rss": mem_info.rss,
                "cpu_percent": cpu_percent,
                "fd_count": fd_count,
                "child_count": len(children),
                "status": proc.status(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"error": "Process not accessible"}


class ResourcePredictionEngine:
    """Predicts future resource usage based on historical Harness Cards and trends."""

    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def predict_spawn_impact(self, harness_type: str, current_free_mb: int) -> bool:
        """Return True if spawning the agent is safe based on predicted impact."""
        # Simple heuristic: T3 isolation adds ~128MB overhead
        predicted_usage = 512  # Default
        if "claude" in harness_type.lower():
            predicted_usage = 1024
        elif "cursor" in harness_type.lower():
            predicted_usage = 768

        # Safety buffer
        if (current_free_mb - predicted_usage) < 256:
            logger.warning(f"Predictive throttle: Spawning {harness_type} may cause OOM.")
            return False
        return True

    def record_actual(self, harness_type: str, actual_mb: int):
        """Record actual usage for future predictions."""
        self.history.append({"harness": harness_type, "mb": actual_mb})
        # Keep last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]


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
