"""Workstream/governance status tool registrations for MCP server."""

from __future__ import annotations

import orjson as json
import time
from typing import Any, Callable

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_workstream_governance_tools(
    *,
    mcp: FastMCP,
    server_tools_governance: Any,
    govern_approve_impl: Callable[..., dict[str, Any]],
    govern_reject_impl: Callable[..., dict[str, Any]],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_workstream_query(query: str) -> ToolResult:
        """
        Execute SQL query on workstream database.

        Returns query results as JSON. Use for exploring session/workstream data.
        Example: "SELECT * FROM sessions WHERE status='running' LIMIT 10"
        """
        from thegent_core.config import ThegentSettings
        from thegent_planning.planning.workstream_db import WorkstreamDB

        start_time = time.perf_counter()
        try:
            db = WorkstreamDB(settings=ThegentSettings())
            results = db.execute_query(query)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                content=json.dumps(results, indent=2).decode().decode(),
                structured_content={"results": results, "count": len(results)},
                meta={"execution_time_ms": elapsed_ms, "row_count": len(results)},
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                content=f"Error executing query: {e}",
                structured_content={"error": str(e)},
                meta={"execution_time_ms": elapsed_ms},
            )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_workstream_stats() -> ToolResult:
        """
        Get workstream statistics.

        Returns statistics including running/completed counts, success rate,
        average duration, deferred tasks, and lane breakdown.
        """
        from thegent_core.config import ThegentSettings
        from thegent_planning.planning.workstream_db import WorkstreamDB

        start_time = time.perf_counter()
        try:
            db = WorkstreamDB(settings=ThegentSettings())
            stats = db.get_statistics()
            lane_counts = db.get_running_count_by_lane()
            recent_costs = db.get_recent_costs(limit=5)

            result = {
                "statistics": stats,
                "lane_breakdown": lane_counts,
                "recent_costs": recent_costs,
            }

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                content=json.dumps(result, indent=2).decode().decode(),
                structured_content=result,
                meta={"execution_time_ms": elapsed_ms},
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                content=f"Error getting stats: {e}",
                structured_content={"error": str(e)},
                meta={"execution_time_ms": elapsed_ms},
            )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=json.dumps(result).decode().decode(),
            structured_content=result,
            meta={"execution_time_ms": elapsed_ms},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_heliosShield_status() -> ToolResult:
        """
        Get status from thegent.mesh harness.
        """
        from thegent_skills.skills.terminal import heliosShield_status

        start_time = time.perf_counter()
        status = heliosShield_status()
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=status,
            structured_content={"status": status},
            meta={"execution_time_ms": elapsed_ms},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_govern_approve(run_id: str, reason: str | None = None) -> ToolResult:
        """
        Approve a HITL-blocked run (G-GP-05 / WL-019).

        Reads pending approvals from governance_events.jsonl, updates status to
        'approved', and triggers continuation of the blocked run.
        Equivalent to: thegent govern approve <run_id> [--reason <r>]
        """
        return server_tools_governance.thegent_govern_approve_impl(
            run_id=run_id,
            reason=reason,
            govern_approve_impl=govern_approve_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_govern_reject(run_id: str, reason: str | None = None) -> ToolResult:
        """
        Reject a HITL-blocked run (G-GP-05 / WL-019).

        Reads pending approvals from governance_events.jsonl, updates status to
        'rejected', and cancels the blocked run.
        Equivalent to: thegent govern reject <run_id> [--reason <r>]
        """
        return server_tools_governance.thegent_govern_reject_impl(
            run_id=run_id,
            reason=reason,
            govern_reject_impl=govern_reject_impl,
        )

    return (
        thegent_workstream_query,
        thegent_workstream_stats,
        thegent_heliosShield_status,
        thegent_govern_approve,
        thegent_govern_reject,
    )
