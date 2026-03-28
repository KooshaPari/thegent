"""
Health check endpoints for services.
Implements readiness and liveness probes per the Phenotype operations standard.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    component: str
    status: HealthStatus
    message: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duration_ms": self.duration_ms,
        }


@dataclass
class HealthReport:
    """Aggregate health report for a service."""
    service: str
    overall_status: HealthStatus
    checks: list[HealthCheckResult]
    timestamp: datetime
    version: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "status": self.overall_status.value,
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
        }


class HealthChecker:
    """Base class for health check implementations."""

    def __init__(self, service_name: str):
        self.service_name = service_name

    async def check_readiness(self) -> HealthCheckResult:
        """Check if service is ready to receive traffic."""
        raise NotImplementedError

    async def check_liveness(self) -> HealthCheckResult:
        """Check if service is alive."""
        raise NotImplementedError

    async def check_dependencies(self) -> list[HealthCheckResult]:
        """Check service dependencies (DB, cache, etc)."""
        return []


# Standard health check endpoint patterns:
#
# GET /health/live
#   Returns 200 if process is running
#   Used by Kubernetes liveness probe
#
# GET /health/ready
#   Returns 200 if service is ready to accept traffic
#   Checks dependencies (DB, cache, external services)
#   Used by Kubernetes readiness probe
#
# GET /health
#   Returns 200 with full health report
#   Includes all checks and dependency status
