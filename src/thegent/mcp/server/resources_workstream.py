"""Workstream-related resource handlers for MCP server."""

from __future__ import annotations

import orjson as json


def resource_workstream_impl() -> str:
    from thegent.utils import get_resource_path
    from thegent.utils.helpers import read_file_optimized

    work_stream_path = get_resource_path("docs/reference/WORK_STREAM.md")
    if not work_stream_path.exists():
        return "WORK_STREAM.md not found. Run 'thegent plan incorporate' to seed it."
    return read_file_optimized(work_stream_path, max_size_mb=2) or "Error reading work stream."


def resource_events_session_complete_impl() -> str:
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        events = db.execute_query(
            """
            SELECT session_id, exit_code, completed_at, workstream_item_id
            FROM sessions
            WHERE status = 'exited' AND completed_at IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT 50
            """
        )
        return json.dumps({"events": events, "count": len(events).decode().decode()})
    except Exception as e:
        return json.dumps({"error": str(e).decode().decode(), "events": []})


def resource_workstream_db_impl() -> str:
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        stats = db.get_statistics()
        return json.dumps(
            {
                "database_path": str(db.db_path),
                "schema_version": db.SCHEMA_VERSION,
                "statistics": stats,
                "tables": [
                    "sessions",
                    "workstream_items",
                    "dependencies",
                    "launches",
                    "auto_launch_events",
                    "evidence_links",
                    "cost_tracking",
                    "deferred_tasks",
                    "team_tasks",
                    "kpi_metrics",
                    "backlog_items",
                    "teammate_delegations",
                    "policy_overrides",
                    "process_tracking",
                    "siem_events",
                    "rbac_audit",
                    "memory_cache",
                    "constitutional_violations",
                    "reputation_entries",
                    "agent_hierarchy",
                    "sync_tracking",
                    "config_cache",
                    "plan_tasks",
                    "alert_fatigue",
                ],
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e).decode().decode()})
