"""Thegent CLI team/collaboration commands facade - re-exports from submodules.

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from __future__ import annotations

# Crew commands
from thegent.cli.commands.team.cli_crew import (
    crew_add_agent_cmd,
    crew_add_task_cmd,
    crew_create_cmd,
    crew_execute_cmd,
    crew_list_cmd,
    crew_show_cmd,
    crew_status_cmd,
)

# Teammates commands
from thegent.cli.commands.team.cli_teammates import (
    delegate_task,
    list_teammates,
)

# Team commands
from thegent.cli.commands.team.team_commands import (
    team_create_cmd,
    team_crew_cmd,
    team_hierarchy_cmd,
    team_list_cmd,
    team_task_add_cmd,
    team_task_list_cmd,
)

# Team handoff commands
from thegent.cli.commands.team.team_handoff_cmds import (
    handoff_cmd,
    handoff_confirm_cmd,
    handoff_list_cmd,
    handoff_show_cmd,
)

# Team dump commands
from thegent.cli.commands.team.team_dump_cmds import (
    dump_categories_cmd,
    dump_index_cmd,
    dump_latest_cmd,
)

# Team monitoring commands
from thegent.cli.commands.team.team_monitoring_cmds import (
    dlq_list_cmd,
    drift_monitor_cmd,
    roadmap_cmd,
    self_heal_tests_cmd,
    traffic_cmd,
    watchdog_cmd,
)

# Team snapshot commands
from thegent.cli.commands.team.team_snapshot_cmds import (
    snapshot_daily_export_cmd,
    snapshot_daily_index_cmd,
    snapshot_daily_totals_cmd,
    snapshot_export_cmd,
    snapshot_index_cmd,
    snapshot_list_cmd,
    snapshot_meta_cmd,
    snapshot_prune_cmd,
)

# Team summary commands
from thegent.cli.commands.team.team_summary_cmds import (
    summary_cmd,
    teammates_delegate_cmd,
    teammates_list_cmd,
    teammates_status_cmd,
)

# Team analysis commands
from thegent.cli.commands.team.team_analysis_cmds import (
    explain_cmd,
    fallbacks_cmd,
)

# Team legacy commands (from team_cmds.py which is a consolidation module)
from thegent.cli.commands.team.team_cmds import (
    project_list_cmd,
    project_register_cmd,
    queue_list_cmd,
    recover_status_cmd,
)

__all__ = [
    "crew_add_agent_cmd",
    "crew_add_task_cmd",
    "crew_create_cmd",
    "crew_execute_cmd",
    "crew_list_cmd",
    "crew_show_cmd",
    "crew_status_cmd",
    "list_teammates",
    "delegate_task",
    "team_create_cmd",
    "team_list_cmd",
    "team_crew_cmd",
    "team_hierarchy_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
    "handoff_cmd",
    "handoff_show_cmd",
    "handoff_list_cmd",
    "handoff_confirm_cmd",
    "dump_index_cmd",
    "dump_latest_cmd",
    "dump_categories_cmd",
    "watchdog_cmd",
    "dlq_list_cmd",
    "traffic_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "snapshot_list_cmd",
    "snapshot_index_cmd",
    "snapshot_export_cmd",
    "snapshot_prune_cmd",
    "snapshot_meta_cmd",
    "snapshot_daily_index_cmd",
    "snapshot_daily_totals_cmd",
    "snapshot_daily_export_cmd",
    "summary_cmd",
    "teammates_list_cmd",
    "teammates_delegate_cmd",
    "teammates_status_cmd",
    "explain_cmd",
    "fallbacks_cmd",
    "queue_list_cmd",
    "recover_status_cmd",
    "project_register_cmd",
    "project_list_cmd",
]
