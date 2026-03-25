"""Thegent CLI observability commands facade - re-exports from submodules."""

# @trace WL-124
from __future__ import annotations

# Git operations
from thegent.cli.commands.observability.cli_git_log_ops import (
    cli_git_log_ops_cmd,
)

# Governance audit and compliance commands
from thegent.cli.commands.observability.governance_audit_compliance_cmds import (
    signatures_list_cmd,
    signatures_verify_cmd,
    compliance_siem_test_cmd,
    compliance_plugin_check_cmd,
    compliance_redact_cmd,
    govern_cost_cmd,
    guardrails_check_cmd,
    guardrails_show_cmd,
)

# Governance health commands
from thegent.cli.commands.observability.governance_health_core_cmds import (
    govern_configure_cmd,
    govern_go_health_cmd,
    govern_go_status_cmd,
    govern_go_cycle_cmd,
    govern_go_watch_cmd,
)

# Governance policy health commands
from thegent.cli.commands.observability.governance_policy_health_cmds import (
    policy_health_cmd,
)

# Infra observability commands
from thegent.cli.commands.observability.infra_observe_cmds import (
    observe_summary_cmd,
    cockpit_cmd,
    sitback_dashboard_cmd,
)

# Infra performance commands
from thegent.cli.commands.observability.infra_perf_cmds import (
    modes_cmd,
    benchmark_cmd,
    release_pack_cmd,
    forensics_snapshot_cmd,
    recover_status_cmd,
    monitor_cmd,
    operations_cmd,
)

# Session contract health commands
from thegent.cli.commands.observability.session_contract_health_cmds import (
    session_contract_health_gate_cmd,
    session_contract_health_report_cmd,
    session_contract_health_trend_cmd,
)

# Session status commands
from thegent.cli.commands.observability.session_status_cmds import (
    status_cmd,
    inspect_cmd,
    logs_cmd,
)

# Team monitoring commands
from thegent.cli.commands.observability.team_monitoring_cmds import (
    watchdog_cmd,
    dlq_list_cmd,
    traffic_cmd,
    drift_monitor_cmd,
    roadmap_cmd,
    self_heal_tests_cmd,
)

__all__ = [
    # Git operations
    "cli_git_log_ops_cmd",
    # Governance audit and compliance
    "signatures_list_cmd",
    "signatures_verify_cmd",
    "compliance_siem_test_cmd",
    "compliance_plugin_check_cmd",
    "compliance_redact_cmd",
    "govern_cost_cmd",
    "guardrails_check_cmd",
    "guardrails_show_cmd",
    # Governance health
    "govern_configure_cmd",
    "govern_go_health_cmd",
    "govern_go_status_cmd",
    "govern_go_cycle_cmd",
    "govern_go_watch_cmd",
    # Governance policy health
    "policy_health_cmd",
    # Infra observability
    "observe_summary_cmd",
    "cockpit_cmd",
    "sitback_dashboard_cmd",
    # Infra performance
    "modes_cmd",
    "benchmark_cmd",
    "release_pack_cmd",
    "forensics_snapshot_cmd",
    "recover_status_cmd",
    "monitor_cmd",
    "operations_cmd",
    # Session contract health
    "session_contract_health_gate_cmd",
    "session_contract_health_report_cmd",
    "session_contract_health_trend_cmd",
    # Session status
    "status_cmd",
    "inspect_cmd",
    "logs_cmd",
    # Team monitoring
    "watchdog_cmd",
    "dlq_list_cmd",
    "traffic_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
]
