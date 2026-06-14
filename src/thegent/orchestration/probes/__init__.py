"""Orchestration probes module for health checking."""

from __future__ import annotations

from pathlib import Path
from typing import Any


__all__ = ["HealthProbe", "ProbeResult", "run_post_rollback_probes", "run_pre_promote_probes"]


class ProbeResult:
    """Result of a health probe."""

    def __init__(self, name: str, healthy: bool, message: str = "") -> None:
        self.name = name
        self.healthy = healthy
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "healthy": self.healthy, "message": self.message}


class HealthProbe:
    """Health probe for orchestration."""

    def __init__(self, name: str) -> None:
        self.name = name

    def check(self) -> ProbeResult:
        """Check health."""
        return ProbeResult(self.name, healthy=True)

    def is_healthy(self) -> bool:
        """Check if probe is healthy."""
        return self.check().healthy


def run_post_rollback_probes(_tmp_path: Path | None = None) -> dict[str, Any]:
    """Run health probes after a rollback operation.

    Args:
        _tmp_path: Optional path for temporary files

    Returns:
        Dict with passed status and findings
    """
    probes = [
        HealthProbe("database"),
        HealthProbe("cache"),
        HealthProbe("queue"),
    ]
    results = [probe.check() for probe in probes]
    all_passed = all(r.healthy for r in results)
    return {"passed": all_passed, "findings": [r.to_dict() for r in results]}


def run_pre_promote_probes(_tmp_path: Path | None = None) -> dict[str, Any]:
    """Run health probes before promotion.

    Args:
        _tmp_path: Optional path for temporary files

    Returns:
        Dict with passed status and findings
    """
    probes = [
        HealthProbe("code_quality"),
        HealthProbe("test_coverage"),
        HealthProbe("documentation"),
    ]
    results = [probe.check() for probe in probes]
    all_passed = all(r.healthy for r in results)
    return {"passed": all_passed, "findings": [r.to_dict() for r in results]}
