"""Service Level Objective (SLO) regulation and monitoring (WP-5001).

Hardening (AUDIT-N+55 — SOTA pass-39)
--------------------------------------
Contract surface asserted by
``tests/test_unit_audit_n55_slo_hardening.py``
(``FR-GOV-SLO-001..015``).

# @trace AUDIT-N+55
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_WINDOW = 100


class SLORegulator:
    """Monitors and regulates actions to meet defined Service Level Objectives.

    ``FR-GOV-SLO-001`` .. ``FR-GOV-SLO-015``.
    """

    def __init__(
        self,
        latency_slo_ms: float = 500.0,
        error_slo_rate: float = 0.01,
    ) -> None:
        if latency_slo_ms <= 0:
            raise ValueError(f"latency_slo_ms must be > 0 (got {latency_slo_ms})")
        if not 0.0 <= error_slo_rate <= 1.0:
            raise ValueError(f"error_slo_rate must be in [0, 1] (got {error_slo_rate})")

        self.latency_slo_ms = latency_slo_ms
        self.error_slo_rate = error_slo_rate
        self._metrics: list[dict[str, Any]] = []

    def record_execution(self, latency_ms: float, success: bool) -> None:
        """Record an execution metric.

        ``FR-GOV-SLO-005`` / ``FR-GOV-SLO-006``.
        """
        if latency_ms < 0:
            raise ValueError(f"latency_ms must be >= 0 (got {latency_ms})")
        self._metrics.append({"latency": latency_ms, "success": bool(success)})

    def is_compliant(self) -> bool:
        """Check if currently compliant with SLOs.

        ``FR-GOV-SLO-007`` .. ``FR-GOV-SLO-010``: empty history is
        compliant; only the last ``_WINDOW`` samples are considered.
        """
        if not self._metrics:
            return True

        recent = self._metrics[-_WINDOW:]
        avg_latency = sum(m["latency"] for m in recent) / len(recent)
        error_rate = sum(1 for m in recent if not m["success"]) / len(recent)

        return avg_latency <= self.latency_slo_ms and error_rate <= self.error_slo_rate

    def reset(self) -> None:
        """Clear recorded metrics.

        ``FR-GOV-SLO-011``.
        """
        self._metrics.clear()

    @property
    def metrics(self) -> list[dict[str, Any]]:
        """Return a shallow copy of recorded metrics.

        ``FR-GOV-SLO-012``.
        """
        return list(self._metrics)

    @property
    def sample_count(self) -> int:
        """Number of recorded samples.

        ``FR-GOV-SLO-013``.
        """
        return len(self._metrics)


__all__ = [
    "SLORegulator",
]
