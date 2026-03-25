"""Infra domain facade and public API.

Re-exports all infra command groups and helpers for use in thegent CLI.
Provides a single import point for infrastructure, concurrency, and tooling functionality.

Usage:
    from thegent.cli.commands.infra.facade import *
    # All infra commands now available
"""

from __future__ import annotations

# Concurrency and tooling infrastructure
from thegent.cli.commands.infra.cli_concurrency import (
    set_concurrency as set_concurrency,
    show_concurrency as show_concurrency,
)
from thegent.cli.commands.infra.cli_tooling import (
    debug_cmd as debug_cmd,
    logs_cmd as logs_cmd,
)

# Resource management commands
from thegent.cli.commands.infra.infra_resource_cmds import (
    concurrency_set_cmd as concurrency_set_cmd,
    concurrency_show_cmd as concurrency_show_cmd,
    cost_status_cmd as cost_status_cmd,
    load_status_cmd as load_status_cmd,
    usage_cmd as usage_cmd,
)

# Observability commands
from thegent.cli.commands.infra.infra_observe_cmds import (
    cockpit_cmd as cockpit_cmd,
    observe_summary_cmd as observe_summary_cmd,
    sitback_dashboard_cmd as sitback_dashboard_cmd,
)

# Performance and operations commands
from thegent.cli.commands.infra.infra_perf_cmds import (
    benchmark_cmd as benchmark_cmd,
    forensics_snapshot_cmd as forensics_snapshot_cmd,
    modes_cmd as modes_cmd,
    monitor_cmd as monitor_cmd,
    operations_cmd as operations_cmd,
    recover_status_cmd as recover_status_cmd,
    release_pack_cmd as release_pack_cmd,
)

# Utilities commands
from thegent.cli.commands.infra.infra_utils_cmds import (
    archive_cmd as archive_cmd,
    config_check_cmd as config_check_cmd,
    context_history_cmd as context_history_cmd,
    explorer_cmd as explorer_cmd,
    interruption_list_cmd as interruption_list_cmd,
    interruption_snooze_cmd as interruption_snooze_cmd,
    purge_cmd as purge_cmd,
    scratchpad_cmd as scratchpad_cmd,
)

__all__ = [
    # Concurrency and tooling
    "debug_cmd",
    "logs_cmd",
    "set_concurrency",
    "show_concurrency",
    # Resource management
    "concurrency_set_cmd",
    "concurrency_show_cmd",
    "cost_status_cmd",
    "load_status_cmd",
    "usage_cmd",
    # Observability
    "cockpit_cmd",
    "observe_summary_cmd",
    "sitback_dashboard_cmd",
    # Performance and operations
    "benchmark_cmd",
    "forensics_snapshot_cmd",
    "modes_cmd",
    "monitor_cmd",
    "operations_cmd",
    "recover_status_cmd",
    "release_pack_cmd",
    # Utilities
    "archive_cmd",
    "config_check_cmd",
    "context_history_cmd",
    "explorer_cmd",
    "interruption_list_cmd",
    "interruption_snooze_cmd",
    "purge_cmd",
    "scratchpad_cmd",
]
