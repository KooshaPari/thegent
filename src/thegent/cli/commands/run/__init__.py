"""Thegent CLI run/execution domain (extracted from god package).

This package encapsulates all execution and run-related commands and infrastructure:
- Run and agent execution
- Loop execution (continuous task loops)
- Background execution (bg)
- DAG execution and orchestration
- Advanced run features (replay, retry, research)
- Execution helpers and output formatting

@trace WL-124: CLI god package decomposition - RUN domain
"""

from thegent.cli.commands.run.facade import (
    # Core run
    run_cmd,
    run_diff_cmd,
    # Loop commands
    loop_cmd,
    loop_send_cmd,
    loop_stop_cmd,
    # Advanced commands
    bg_cmd,
    replay_cmd,
    retry_cmd,
    deep_research_cmd,
    trace_replay_cmd,
    takeover_cmd,
    terminal_route_cmd,
    # DAG run commands
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
