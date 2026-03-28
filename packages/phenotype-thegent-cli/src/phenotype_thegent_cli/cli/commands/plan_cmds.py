"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124).

This is a thin facade that re-exports commands from split submodules for backward compatibility.
"""

# @trace WL-124
from __future__ import annotations

from phenotype_thegent_cli.cli.commands.plan_dag_cmds import (
    dag_add_cmd,
    dag_cancel_cmd,
    dag_checkpoint_cmd,
    dag_checkpoints_cmd,
    dag_list_cmd,
    dag_probe_cmd,
    dag_ready_cmd,
    dag_recover_cmd,
    dag_reconcile_cmd,
    dag_remove_cmd,
    dag_rollback_cmd,
    dag_run_cmd,
    dag_status_cmd,
    dag_sync_cmd,
    dag_update_cmd,
    dag_validate_cmd,
)

from phenotype_thegent_cli.cli.commands.team_snapshot_cmds import (
    snapshot_daily_totals_cmd,
)

from phenotype_thegent_cli.cli.commands.team_dump_cmds import (
    dump_categories_cmd,
)

from phenotype_thegent_cli.cli.commands.plan_workstream_cmds import (
    closure_pack_cmd,
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
    "snapshot_daily_totals_cmd",
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
    "workstream_query_cmd",
]
