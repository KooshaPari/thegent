"""Thegent CLI run/execution commands facade - re-exports from submodules.

@trace WL-124: CLI god package decomposition - RUN domain
"""

from __future__ import annotations

# Core run commands
from thegent.cli.commands.run.run_cmds import (
    run_cmd,
    run_diff_cmd,
)

# Loop commands
from thegent.cli.commands.run.run_cmds_loop import (
    loop_cmd,
    loop_send_cmd,
    loop_stop_cmd,
)

# Advanced run commands
from thegent.cli.commands.run.run_cmds_advanced import (
    bg_cmd,
    replay_cmd,
    retry_cmd,
    deep_research_cmd,
    trace_replay_cmd,
    takeover_cmd,
    terminal_route_cmd,
)

# DAG run commands
from thegent.cli.commands.run.cli_dag_run_cmds import (
    dag_run_cmd,
    dag_status_cmd,
    dag_sync_cmd,
    dag_update_cmd,
    dag_cancel_cmd,
    dag_rollback_cmd,
    dag_ready_cmd,
    dag_recover_cmd,
    dag_reconcile_cmd,
    dag_checkpoint_cmd,
    dag_checkpoints_cmd,
    dag_probe_cmd,
)


__all__ = [
    # Core run
    "run_cmd",
    "run_diff_cmd",
    # Loop commands
    "loop_cmd",
    "loop_send_cmd",
    "loop_stop_cmd",
    # Advanced commands
    "bg_cmd",
    "replay_cmd",
    "retry_cmd",
    "deep_research_cmd",
    "trace_replay_cmd",
    "takeover_cmd",
    "terminal_route_cmd",
    # DAG run commands
    "dag_run_cmd",
    "dag_status_cmd",
    "dag_sync_cmd",
    "dag_update_cmd",
    "dag_cancel_cmd",
    "dag_rollback_cmd",
    "dag_ready_cmd",
    "dag_recover_cmd",
    "dag_reconcile_cmd",
    "dag_checkpoint_cmd",
    "dag_checkpoints_cmd",
    "dag_probe_cmd",
]
