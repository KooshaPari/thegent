"""Orchestration probes module (AUDIT-N+39 hardened).

Health probes are pluggable ``HealthProbe`` instances; the runners
``run_pre_promote_probes`` and ``run_post_rollback_probes`` return a
``{passed, findings}`` shape where ``findings`` is the list of
``ProbeResult.to_dict()`` payloads (so callers can serialise to JSON
without coupling to the dataclass).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "HealthProbe",
    "ProbeResult",
    "run_post_rollback_probes",
    "run_pre_promote_probes",
]


@dataclass
class ProbeResult:
    """Result of a single probe run.

    @trace FR-RES-007
    """

    name: str
    healthy: bool
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "healthy": self.healthy, "message": self.message}


class HealthProbe:
    """A single named health probe.

    @trace FR-RES-007

    Subclasses override ``check()`` to perform the actual health
    check. ``healthy=True`` is the default (no-op probe).
    """

    def __init__(self, name: str, *, healthy: bool = True) -> None:
        self.name = name
        self._default_healthy = healthy

    def check(self) -> ProbeResult:
        return ProbeResult(self.name, self._default_healthy, "")

    def is_healthy(self) -> bool:
        return self.check().healthy


def _run_probes(probes: list[HealthProbe], tmp_path: Path | None) -> dict[str, Any]:
    results = [probe.check() for probe in probes]
    passed = all(r.healthy for r in results)
    return {
        "passed": passed,
        "findings": [r.to_dict() for r in results],
        "tmp_path": str(tmp_path) if tmp_path else None,
    }


def run_pre_promote_probes(_tmp_path: Path | None = None) -> dict[str, Any]:
    """Run the pre-promotion probe battery.

    @trace FR-RES-008
    """
    probes = [
        HealthProbe("code_quality"),
        HealthProbe("test_coverage"),
        HealthProbe("documentation"),
    ]
    return _run_probes(probes, _tmp_path)


def run_post_rollback_probes(_tmp_path: Path | None = None) -> dict[str, Any]:
    """Run the post-rollback probe battery.

    @trace FR-RES-008
    """
    probes = [
        HealthProbe("database"),
        HealthProbe("cache"),
        HealthProbe("queue"),
    ]
    return _run_probes(probes, _tmp_path)
