"""Session management backend: thin re-export facade.

Extracted from impl.py as part of WL-120 LOC Reduction Program (Wave-3, W3-B2).
Split into sub-modules as part of WL-120 max-lines enforcement:
- session_meta_impl.py        — meta I/O, state contracts, output helpers, continuation
- session_health_impl.py      — contract listing, audit, health gate
- session_health_report_impl.py — health report, health trend
- session_ops_impl.py         — ps, list, status, inspect, logs
- session_control_impl.py     — wait, stop, send, history, metrics, prune, events,
                                meta, negotiate, purge, explain
"""

from __future__ import annotations

from thegent.cli.commands.session_control_impl import (
    events_impl,
    explain_run_impl,
    history_impl,
    metrics_impl,
    prune_sessions_impl,
    purge_impl,
    session_contract_negotiate_impl,
    session_meta_impl,
    session_send_impl,
    stop_impl,
    wait_impl,
)
from thegent.cli.commands.session_health_impl import (
    _extract_blocked_ratio,
    list_session_contracts_impl,
    session_contract_audit_impl,
    session_contract_health_gate_impl,
)
from thegent.cli.commands.session_health_report_impl import (
    session_contract_health_report_impl,
    session_contract_health_trend_impl,
)
from thegent.cli.commands.session_meta_impl import (
    _build_continuation_prompt,
    _find_session_meta,
    _is_non_empty_contract_string,
    _load_prior_session_output,
    _normalize_contract_string,
    _normalize_output_format,
    _parse_contract_timestamp,
    _read_session_meta,
    _resolve_latest_session_id,
    _resolve_session_status,
    _run_background_session_observer,
    _save_session_meta,
    _session_state_path,
    _write_session_state,
)
from thegent.cli.commands.session_ops_impl import (
    inspect_impl,
    logs_impl,
    ps_impl,
    session_list_impl,
    status_impl,
)

__all__ = [
    "_build_continuation_prompt",
    "_extract_blocked_ratio",
    "_find_session_meta",
    "_is_non_empty_contract_string",
    "_load_prior_session_output",
    "_normalize_contract_string",
    "_normalize_output_format",
    "_parse_contract_timestamp",
    "_read_session_meta",
    "_resolve_latest_session_id",
    "_resolve_session_status",
    "_run_background_session_observer",
    "_save_session_meta",
    "_session_state_path",
    "_write_session_state",
    "events_impl",
    "explain_run_impl",
    "history_impl",
    "inspect_impl",
    "list_session_contracts_impl",
    "logs_impl",
    "metrics_impl",
    "prune_sessions_impl",
    "ps_impl",
    "purge_impl",
    "session_contract_audit_impl",
    "session_contract_health_gate_impl",
    "session_contract_health_report_impl",
    "session_contract_health_trend_impl",
    "session_contract_negotiate_impl",
    "session_list_impl",
    "session_meta_impl",
    "session_send_impl",
    "status_impl",
    "stop_impl",
    "wait_impl",
]
