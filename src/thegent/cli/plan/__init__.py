"""Thegent CLI plan/DAG domain subpackage.

Phase 3 extraction from cli.py god package (WL-124/WL-125).
Organizes all plan-related command handlers and utilities.

Modules:
  plan_cmds.py                    — Main command re-exports facade
  plan_dag_cmds.py                — DAG manipulation commands
  plan_dag_orchestrate_cmds.py    — DAG orchestration commands
  plan_dag_ready_run_cmds.py      — DAG ready/run commands
  plan_dag_sync_recover_cmds.py   — DAG sync/recovery commands
  plan_dag_validate_cmds.py       — DAG validation commands
  plan_entity_cmds.py             — Plan entity commands
  plan_output_helpers.py          — Output formatting utilities
  plan_workstream_analysis_cmds.py — Workstream analysis commands
  plan_workstream_cmds.py         — Main workstream commands
  plan_workstream_exec_cmds.py    — Workstream execution commands
  plan_workstream_flow_cmds.py    — Workstream flow commands
  plan_workstream_state_cmds.py   — Workstream state commands
  impl_work_stream.py             — Workstream implementation utilities
"""

# @trace WL-125 Phase-3 PLAN domain extraction

from __future__ import annotations

# Re-export main facade for backward compatibility
from thegent.cli.plan.plan_cmds import (
    closure_pack_cmd,
    dag_add_cmd,
    dag_cancel_cmd,
    dag_checkpoint_cmd,
    dag_checkpoints_cmd,
    dag_list_cmd,
    dag_probe_cmd,
    dag_ready_cmd,
    dag_reconcile_cmd,
    dag_recover_cmd,
    dag_remove_cmd,
    dag_rollback_cmd,
    dag_run_cmd,
    dag_status_cmd,
    dag_sync_cmd,
    dag_update_cmd,
    dag_validate_cmd,
    dump_categories_cmd,
    plan_analyze_cmd,
    plan_claim_cmd,
    plan_complete_cmd,
    plan_do_next_cmd,
    plan_get_next_cmd,
    plan_incorporate_cmd,
    plan_lint_workstream_cmd,
    plan_loop_cmd,
    plan_normalize_workstream_cmd,
    plan_progress_cmd,
    plan_verify_workstream_cmd,
    plan_wait_next_cmd,
    snapshot_daily_totals_cmd,
    workstream_query_cmd,
)

__all__ = [
    "closure_pack_cmd",
    "dag_add_cmd",
    "dag_cancel_cmd",
    "dag_checkpoint_cmd",
    "dag_checkpoints_cmd",
    "dag_list_cmd",
    "dag_probe_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "dag_recover_cmd",
    "dag_remove_cmd",
    "dag_rollback_cmd",
    "dag_run_cmd",
    "dag_status_cmd",
    "dag_sync_cmd",
    "dag_update_cmd",
    "dag_validate_cmd",
    "dump_categories_cmd",
    "plan_analyze_cmd",
    "plan_claim_cmd",
    "plan_complete_cmd",
    "plan_do_next_cmd",
    "plan_get_next_cmd",
    "plan_incorporate_cmd",
    "plan_lint_workstream_cmd",
    "plan_loop_cmd",
    "plan_normalize_workstream_cmd",
    "plan_progress_cmd",
    "plan_verify_workstream_cmd",
    "plan_wait_next_cmd",
    "snapshot_daily_totals_cmd",
    "workstream_query_cmd",
]
