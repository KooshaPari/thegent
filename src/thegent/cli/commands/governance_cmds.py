"""Thegent CLI governance commands facade - routes to specialized modules (WL-124).

This module re-exports all governance commands from:
- governance_audit_compliance_cmds: Audit, compliance, data protection
- governance_escalation_hitl_cmds: Escalation and HITL approval handling
- governance_policy_health_cmds: Policies, contracts, health scoring, drift
- governance_agileplus_cmds: AgilePlus health cycling and watching
- governance_discovery_guardrails_cmds: Discovery and guardrails

Direct imports from submodules preserve all public names for CLI registration.
"""

# @trace WL-124
from __future__ import annotations

# Re-export all audit & compliance commands
from thegent.cli.commands.governance_audit_compliance_cmds import (
    audit_verify_cmd,
    compliance_plugin_check_cmd,
    compliance_redact_cmd,
    compliance_report_cmd,
    compliance_siem_test_cmd,
    data_protection_cmd,
    signatures_list_cmd,
    signatures_verify_cmd,
    trust_status_cmd,
)

# Re-export all escalation & HITL commands
from thegent.cli.commands.governance_escalation_hitl_cmds import (
    escalate_add_cmd,
    escalate_approve_cmd,
    escalate_list_cmd,
    escalate_resolve_cmd,
    govern_approve_cmd,
    govern_list_pending_cmd,
    govern_reject_cmd,
)

# Re-export all policy & health commands
from thegent.cli.commands.governance_policy_health_cmds import (
    HEALTH_POLICY_PROFILES,
    contracts_conformance_cmd,
    contracts_registry_cmd,
    drift_cmd,
    govern_configure_cmd,
    govern_cost_cmd,
    migration_cmd,
    policy_check_cmd,
    policy_purge_cmd,
    policy_show_cmd,
    sweep_cmd,
)

# Re-export all AgilePlus commands
from thegent.cli.commands.governance_agileplus_cmds import (
    govern_go_cycle_cmd,
    govern_go_health_cmd,
    govern_go_status_cmd,
    govern_go_watch_cmd,
)

# Re-export discovery & guardrails commands
from thegent.cli.commands.governance_discovery_guardrails_cmds import (
    discovery_parse_cmd,
    discovery_register_cmd,
    discovery_scan_cmd,
    guardrails_check_cmd,
    guardrails_show_cmd,
)

__all__ = [
    # Audit & compliance
    "audit_verify_cmd",
    "compliance_plugin_check_cmd",
    "compliance_redact_cmd",
    "compliance_report_cmd",
    "compliance_siem_test_cmd",
    "data_protection_cmd",
    "signatures_list_cmd",
    "signatures_verify_cmd",
    "trust_status_cmd",
    # Escalation & HITL
    "escalate_add_cmd",
    "escalate_approve_cmd",
    "escalate_list_cmd",
    "escalate_resolve_cmd",
    "govern_approve_cmd",
    "govern_list_pending_cmd",
    "govern_reject_cmd",
    # Policies & health
    "HEALTH_POLICY_PROFILES",
    "contracts_conformance_cmd",
    "contracts_registry_cmd",
    "drift_cmd",
    "govern_configure_cmd",
    "govern_cost_cmd",
    "migration_cmd",
    "policy_check_cmd",
    "policy_purge_cmd",
    "policy_show_cmd",
    "sweep_cmd",
    # AgilePlus
    "govern_go_cycle_cmd",
    "govern_go_health_cmd",
    "govern_go_status_cmd",
    "govern_go_watch_cmd",
    # Discovery & guardrails
    "discovery_parse_cmd",
    "discovery_register_cmd",
    "discovery_scan_cmd",
    "guardrails_check_cmd",
    "guardrails_show_cmd",
]
