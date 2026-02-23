"""Health payload constants — split from observability_impl (WL-124)."""

from __future__ import annotations

HEALTH_PAYLOAD_SCHEMA_VERSION = "health-schema-v1"
HEALTH_PAYLOAD_TYPES = (
    "session_contract_health_gate",
    "session_contract_health_report",
    "session_contract_health_trend",
)

__all__ = ["HEALTH_PAYLOAD_SCHEMA_VERSION", "HEALTH_PAYLOAD_TYPES"]
