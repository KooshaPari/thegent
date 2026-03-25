"""
Health Checker

System health monitoring and reporting.
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum
import time


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str
    timestamp: float
    duration: float
    details: Optional[dict] = None


class HealthChecker:
    """Manages health checks."""

    def __init__(self):
        self._checks: dict[str, Callable] = {}
        self._results: dict[str, HealthCheckResult] = {}

    def register(self, name: str, check_fn: Callable[[], tuple[bool, str, dict]]) -> None:
        """Register a health check."""
        self._checks[name] = check_fn

    def check(self, name: str) -> HealthCheckResult:
        """Run a specific health check."""
        check_fn = self._checks.get(name)
        if not check_fn:
            return HealthCheckResult(
                name=name, status=HealthStatus.UNHEALTHY, message="Check not found", timestamp=time.time(), duration=0
            )

        start = time.time()
        try:
            healthy, message, details = check_fn()
            status = HealthStatus.HEALTHY if healthy else HealthStatus.DEGRADED
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = str(e)
            details = {"error": str(e)}

        duration = time.time() - start
        result = HealthCheckResult(
            name=name, status=status, message=message, timestamp=time.time(), duration=duration, details=details
        )

        self._results[name] = result
        return result

    def check_all(self) -> dict[str, HealthCheckResult]:
        """Run all health checks."""
        for name in self._checks:
            self.check(name)
        return self._results

    @property
    def status(self) -> HealthStatus:
        """Get overall system status."""
        if not self._results:
            return HealthStatus.HEALTHY

        statuses = [r.status for r in self._results.values()]

        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def summary(self) -> dict:
        """Get health summary."""
        return {
            "status": self.status.value,
            "checks": {
                name: {"status": result.status.value, "message": result.message, "duration": result.duration}
                for name, result in self._results.items()
            },
        }

    # Built-in checks
    def check_memory(self) -> tuple[bool, str, dict]:
        """Check memory usage."""
        try:
            import psutil

            mem = psutil.virtual_memory()
            healthy = mem.percent < 90
            return healthy, f"Memory at {mem.percent}%", {"percent": mem.percent}
        except ImportError:
            return True, "psutil not available", {}

    def check_disk(self, path: str = "/") -> tuple[bool, str, dict]:
        """Check disk usage."""
        try:
            import psutil

            disk = psutil.disk_usage(path)
            healthy = disk.percent < 90
            return healthy, f"Disk at {disk.percent}%", {"percent": disk.percent}
        except ImportError:
            return True, "psutil not available", {}

    def check_cpu(self) -> tuple[bool, str, dict]:
        """Check CPU usage."""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.1)
            healthy = cpu < 90
            return healthy, f"CPU at {cpu}%", {"percent": cpu}
        except ImportError:
            return True, "psutil not available", {}

    def register_defaults(self) -> None:
        """Register default health checks."""
        self.register("memory", self.check_memory)
        self.register("cpu", self.check_cpu)
        self.register("disk", self.check_disk)
