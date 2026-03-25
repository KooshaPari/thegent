"""DAG command handlers facade (WL-120).

Re-exports split modules:
- cli_dag_validate_list_add: validation, list, add, remove
- cli_dag_run_sync_recover: update, cancel, status, ready, run, sync, recover, checkpoints
"""

from thegent.cli.commands.cli_dag_validate_list_add import (
    dag_validate_cmd,
    dag_list_cmd,
    dag_add_cmd,
    dag_remove_cmd,
)
from thegent.cli.commands.run.cli_dag_run_sync_recover import (
    TERMINAL_STATUSES,
    dag_update_cmd,
    dag_cancel_cmd,
    dag_status_cmd,
    dag_ready_cmd,
    dag_reconcile_cmd,
    dag_run_cmd,
    dag_sync_cmd,
    dag_checkpoint_cmd,
    dag_rollback_cmd,
    dag_checkpoints_cmd,
    dag_recover_cmd,
    dag_probe_cmd,
)

__all__ = [
    "TERMINAL_STATUSES",
    "dag_validate_cmd",
    "dag_list_cmd",
    "dag_add_cmd",
    "dag_remove_cmd",
    "dag_update_cmd",
    "dag_cancel_cmd",
    "dag_status_cmd",
    "dag_ready_cmd",
    "dag_reconcile_cmd",
    "dag_run_cmd",
    "dag_sync_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_checkpoints_cmd",
    "dag_recover_cmd",
    "dag_probe_cmd",
]
