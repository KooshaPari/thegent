"""Thegent CLI infra/system commands - re-export facade (extracted from cli.py).

This module is a thin re-export facade for command groups extracted to focused modules:
- infra_resource_cmds: Concurrency, load, cost, usage
- infra_observe_cmds: Observe, cockpit, sitback dashboard
- infra_utils_cmds: Config, interruptions, purge, archive, history, scratchpad, explorer
- infra_perf_cmds: Modes, benchmark, release, forensics, monitor, operations
"""

# @trace WL-124
from __future__ import annotations

from thegent.cli.commands.infra_resource_cmds import (
    concurrency_set_cmd,
    concurrency_show_cmd,
    cost_status_cmd,
    load_status_cmd,
    usage_cmd,
)
from thegent.cli.commands.infra_observe_cmds import (
    cockpit_cmd,
    observe_summary_cmd,
    sitback_dashboard_cmd,
)
from thegent.cli.commands.infra_utils_cmds import (
    archive_cmd,
    config_check_cmd,
    context_history_cmd,
    explorer_cmd,
    interruption_list_cmd,
    interruption_snooze_cmd,
    purge_cmd,
    scratchpad_cmd,
)
from thegent.cli.commands.infra_perf_cmds import (
    benchmark_cmd,
    forensics_snapshot_cmd,
    modes_cmd,
    monitor_cmd,
    operations_cmd,
    recover_status_cmd,
    release_pack_cmd,
)

__all__ = [
    "archive_cmd",
    "benchmark_cmd",
    "cockpit_cmd",
    "concurrency_set_cmd",
    "concurrency_show_cmd",
    "config_check_cmd",
    "context_history_cmd",
    "cost_status_cmd",
    "explorer_cmd",
    "forensics_snapshot_cmd",
    "interruption_list_cmd",
    "interruption_snooze_cmd",
    "load_status_cmd",
    "modes_cmd",
    "monitor_cmd",
    "observe_summary_cmd",
    "operations_cmd",
    "purge_cmd",
    "recover_status_cmd",
    "release_pack_cmd",
    "scratchpad_cmd",
    "sitback_dashboard_cmd",
    "usage_cmd",
]
