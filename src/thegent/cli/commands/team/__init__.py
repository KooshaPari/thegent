"""Thegent CLI team/collaboration domain (extracted from god package).

This package encapsulates all team/collaboration-related commands and infrastructure:
- Teammate persona and agent management (WP-16001)
- Team and crew delegation, handoff, and workflow
- Swarm concurrency and fairness control
- Team snapshots, monitoring, and health checks
- Analysis and summary commands for team performance

@trace WL-125: CLI god package decomposition - TEAM domain
"""

from thegent.cli.commands.team.facade import (
    # CLI Crew commands
    crew_add_agent_cmd,
    crew_add_task_cmd,
    crew_create_cmd,
    crew_execute_cmd,
    crew_list_cmd,
    crew_show_cmd,
    crew_status_cmd,
    # CLI Teammates commands
    list_teammates,
    delegate_task,
    # Team Commands
    team_create_cmd,
    team_list_cmd,
    team_crew_cmd,
    team_hierarchy_cmd,
    team_task_add_cmd,
    team_task_list_cmd,
    # Team Handoff Commands
    handoff_cmd,
    handoff_show_cmd,
    handoff_list_cmd,
    handoff_confirm_cmd,
    # Team Dump Commands
    dump_index_cmd,
    dump_latest_cmd,
    dump_categories_cmd,
    # Team Monitoring Commands
    watchdog_cmd,
    dlq_list_cmd,
    traffic_cmd,
    drift_monitor_cmd,
    roadmap_cmd,
    self_heal_tests_cmd,
    # Team Snapshot Commands
    snapshot_list_cmd,
    snapshot_index_cmd,
    snapshot_export_cmd,
    snapshot_prune_cmd,
    snapshot_meta_cmd,
    snapshot_daily_index_cmd,
    snapshot_daily_totals_cmd,
    snapshot_daily_export_cmd,
    # Team Summary Commands
    summary_cmd,
    teammates_list_cmd,
    teammates_delegate_cmd,
    teammates_status_cmd,
    # Team Analysis Commands
    explain_cmd,
    fallbacks_cmd,
    # Team Legacy Commands
    queue_list_cmd,
    recover_status_cmd,
    project_register_cmd,
    project_list_cmd,
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
