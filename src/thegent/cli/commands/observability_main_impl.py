"""Observability implementation facade (WL-120).

Re-exports split modules:
- observability_escalation_impl: escalation, sweep
- observability_governance_impl: governance, review, compliance
- observability_trends_impl: summary (lazy import)
"""

from thegent.cli.commands.observability_escalation_impl import (
    _extract_agent_from_line,
    _process_run_line,
    escalate_add_impl,
    escalate_approve_impl,
    escalate_list_impl,
    escalate_resolve_impl,
    update_calibration_impl,
    sweep_impl,
)
from thegent.cli.commands.observability_governance_impl import (
    _extract_review_json_payload,
    get_server_meta_impl,
    govern_approve_impl,
    govern_reject_impl,
    govern_list_pending_impl,
    govern_vet_impl,
    review_impl,
    get_data_protection_status_impl,
    sitback_dashboard_impl,
    get_compliance_report_impl,
)

def observe_summary_impl(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 10,
    trend_samples: int = 0,
) -> dict:
    """FR-X08: Unified observability summary (lazy import from trends impl)."""
    from thegent.cli.commands.observability_trends_impl import observe_summary_impl as _impl  # pyright: ignore[reportMissingImports]
    return _impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        top_escalations=top_escalations,
        trend_samples=trend_samples,
    )

__all__ = [
    "_extract_agent_from_line",
    "_process_run_line",
    "_extract_review_json_payload",
    "_REVIEW_ALLOWED_TOOLS",
    "_REVIEW_SCHEMA_PREAMBLE",
    "escalate_add_impl",
    "escalate_approve_impl",
    "escalate_list_impl",
    "escalate_resolve_impl",
    "update_calibration_impl",
    "sweep_impl",
    "observe_summary_impl",
    "get_server_meta_impl",
    "govern_approve_impl",
    "govern_reject_impl",
    "govern_list_pending_impl",
    "govern_vet_impl",
    "review_impl",
    "get_data_protection_status_impl",
    "sitback_dashboard_impl",
    "get_compliance_report_impl",
]

# Re-export constants
from thegent.cli.commands.observability_governance_impl import (
    _REVIEW_ALLOWED_TOOLS,
    _REVIEW_SCHEMA_PREAMBLE,
)
