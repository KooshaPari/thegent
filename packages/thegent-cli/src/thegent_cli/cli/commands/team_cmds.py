"""Thegent CLI team/handoff commands - re-export facade (extracted from cli.py).

This module is a thin re-export facade for command groups extracted to focused modules:
- team_snapshot_cmds: Session snapshot management
- team_dump_cmds: Conversation dump management
- team_analysis_cmds: Run explanation and fallback analysis
- team_handoff_cmds: Shift handoff and continuity
- team_monitoring_cmds: Watchdog, DLQ, traffic, roadmap, self-heal
- team_summary_cmds: Summary and teammates commands
"""

# @trace WL-124
from __future__ import annotations

from thegent.cli.commands._cli_shared import console
from thegent.cli.commands.team_snapshot_cmds import (
    snapshot_daily_export_cmd,
    snapshot_daily_index_cmd,
    snapshot_daily_totals_cmd,
    snapshot_export_cmd,
    snapshot_index_cmd,
    snapshot_list_cmd,
    snapshot_meta_cmd,
    snapshot_prune_cmd,
)
from thegent.cli.commands.team_dump_cmds import (
    dump_categories_cmd,
    dump_index_cmd,
    dump_latest_cmd,
)
from thegent.cli.commands.team_analysis_cmds import (
    explain_cmd,
    fallbacks_cmd,
)
from thegent.cli.commands.team_handoff_cmds import (
    handoff_cmd,
    handoff_confirm_cmd,
    handoff_list_cmd,
    handoff_show_cmd,
)
from thegent.cli.commands.team_monitoring_cmds import (
    dlq_list_cmd,
    drift_monitor_cmd,
    roadmap_cmd,
    self_heal_tests_cmd,
    traffic_cmd,
    watchdog_cmd,
)
from thegent.cli.commands.team_summary_cmds import (
    summary_cmd,
    teammates_delegate_cmd,
    teammates_list_cmd,
    teammates_status_cmd,
)


def queue_list_cmd(watch: bool = False) -> None:
    """WP-7002: List pending prompts in the queue."""
    from thegent.cli.commands.queue_commands import queue_list_cmd as _queue_list_cmd_impl

    _queue_list_cmd_impl(watch=watch)


def team_create_cmd(name: str, leader: str | None = None, teammates: str | None = None) -> None:
    """Backward-compatible wrapper for extracted team command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.team_commands import team_create_cmd as _team_create_cmd_impl

    _team_create_cmd_impl(name=name, leader=leader, teammates=teammates, console=console)


def team_task_add_cmd(team_id: str, title: str, description: str) -> None:
    """Backward-compatible wrapper for extracted team command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.team_commands import team_task_add_cmd as _team_task_add_cmd_impl

    _team_task_add_cmd_impl(team_id=team_id, title=title, description=description, console=console)


def team_task_list_cmd(team_id: str) -> None:
    """Backward-compatible wrapper for extracted team command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.team_commands import team_task_list_cmd as _team_task_list_cmd_impl

    _team_task_list_cmd_impl(team_id=team_id, console=console)


def recover_status_cmd() -> None:
    """Backward-compatible wrapper for extracted recovery command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.recovery_commands import recover_status_cmd as _recover_status_cmd_impl

    _recover_status_cmd_impl(console=console)


def project_register_cmd(path, name: str | None = None) -> None:  # noqa: ANN001
    """Backward-compatible wrapper for extracted project command group."""
    from pathlib import Path

    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.project_commands import project_register_cmd as _project_register_cmd_impl

    _project_register_cmd_impl(path=path if isinstance(path, Path) else Path(path), name=name, console=console)


def project_list_cmd(
    format: str | None = None,
) -> None:
    """Backward-compatible wrapper for extracted project command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.project_commands import project_list_cmd as _project_list_cmd_impl

    _project_list_cmd_impl(format=format, console=console)


__all__ = [
    "dlq_list_cmd",
    "drift_monitor_cmd",
    "dump_categories_cmd",
    "dump_index_cmd",
    "dump_latest_cmd",
    "explain_cmd",
    "fallbacks_cmd",
    "handoff_cmd",
    "handoff_confirm_cmd",
    "handoff_list_cmd",
    "handoff_show_cmd",
    "project_list_cmd",
    "project_register_cmd",
    "queue_list_cmd",
    "recover_status_cmd",
    "roadmap_cmd",
    "self_heal_tests_cmd",
    "snapshot_daily_export_cmd",
    "snapshot_daily_index_cmd",
    "snapshot_daily_totals_cmd",
    "snapshot_export_cmd",
    "snapshot_index_cmd",
    "snapshot_list_cmd",
    "snapshot_meta_cmd",
    "snapshot_prune_cmd",
    "summary_cmd",
    "team_create_cmd",
    "team_task_add_cmd",
    "team_task_list_cmd",
    "teammates_delegate_cmd",
    "teammates_list_cmd",
    "teammates_status_cmd",
    "traffic_cmd",
    "watchdog_cmd",
]
