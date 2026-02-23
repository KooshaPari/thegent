"""Thegent observability impl facade - routes to specialized modules.

This module re-exports all observability implementation functions from:
- observability_main_impl: Main impls (observe_summary, sweep, review, compliance)
- observability_health_impl: Health payload and snapshot helpers
- observability_trends_impl: Observe summary trend analysis helpers

Direct imports from submodules preserve all public names for internal usage.
"""

from __future__ import annotations

# Re-export all main implementation functions
from thegent.cli.commands.observability_main_impl import (
    _REVIEW_ALLOWED_TOOLS as _REVIEW_ALLOWED_TOOLS,
    _REVIEW_SCHEMA_PREAMBLE as _REVIEW_SCHEMA_PREAMBLE,    _append_observe_summary_snapshot,
    _extract_agent_from_line,
    _extract_review_json_payload,
    _process_run_line,
    escalate_add_impl,
    escalate_approve_impl,
    escalate_list_impl,
    escalate_resolve_impl,
    get_compliance_report_impl,
    get_data_protection_status_impl,
    get_server_meta_impl,
    govern_approve_impl,
    govern_list_pending_impl,
    govern_reject_impl,
    govern_vet_impl,
    observe_summary_impl,
    review_impl,
    sitback_dashboard_impl,
    sweep_impl,
    update_calibration_impl,
)

# Re-export all health-related helpers
from thegent.cli.commands.observability_health_impl import (
    HEALTH_PAYLOAD_SCHEMA_VERSION,
    HEALTH_PAYLOAD_TYPES,
    HEALTH_POLICY_PROFILES,
    _append_health_snapshot,
    _coerce_issue_types,
    _compact_health_snapshot_log,
    _hash_health_payload,
    _health_scope_key,
    _health_snapshot_log_path,
    _health_snapshot_max_lines,
    _load_previous_health_snapshot,
    _resolve_health_policy,
)

# Re-export all trends-related helpers
from thegent.cli.commands.observability_trends_impl import (
    OBSERVE_SUMMARY_PAYLOAD_TYPES,
    OBSERVE_SUMMARY_SCHEMA_VERSION,
    _build_observe_summary_trend_scope,
    _classify_observe_summary_trend_health,
    _hash_observe_summary_payload,
    _hash_observe_summary_trend_scope,
    _load_observe_summary_snapshots,
    _observe_summary_freshness_bucket,
    _parse_observe_summary_env_float,
    _parse_observe_summary_env_int,
    _parse_observe_summary_timestamp,
)

__all__ = [
    "HEALTH_PAYLOAD_SCHEMA_VERSION",
    "HEALTH_PAYLOAD_TYPES",
    "HEALTH_POLICY_PROFILES",
    "OBSERVE_SUMMARY_PAYLOAD_TYPES",
    "OBSERVE_SUMMARY_SCHEMA_VERSION",
    "_REVIEW_ALLOWED_TOOLS",
    "_REVIEW_SCHEMA_PREAMBLE",
    "_append_health_snapshot",
    "_append_observe_summary_snapshot",
    "_build_observe_summary_trend_scope",
    "_classify_observe_summary_trend_health",
    "_coerce_issue_types",
    "_compact_health_snapshot_log",
    "_extract_agent_from_line",
    "_extract_review_json_payload",
    "_hash_health_payload",
    "_hash_observe_summary_payload",
    "_hash_observe_summary_trend_scope",
    "_health_scope_key",
    "_health_snapshot_log_path",
    "_health_snapshot_max_lines",
    "_load_observe_summary_snapshots",
    "_load_previous_health_snapshot",
    "_observe_summary_freshness_bucket",
    "_parse_observe_summary_env_float",
    "_parse_observe_summary_env_int",
    "_parse_observe_summary_timestamp",
    "_process_run_line",
    "_resolve_health_policy",
    "escalate_add_impl",
    "escalate_approve_impl",
    "escalate_list_impl",
    "escalate_resolve_impl",
    "get_compliance_report_impl",
    "get_data_protection_status_impl",
    "get_server_meta_impl",
    "govern_approve_impl",
    "govern_list_pending_impl",
    "govern_reject_impl",
    "govern_vet_impl",
    "observe_summary_impl",
    "review_impl",
    "sitback_dashboard_impl",
    "sweep_impl",
    "update_calibration_impl",
]
