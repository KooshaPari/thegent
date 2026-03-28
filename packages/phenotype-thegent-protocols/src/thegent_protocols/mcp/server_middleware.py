"""Middleware setup for the MCP FastMCP server (WL-120 W3-C4)."""

from __future__ import annotations

from typing import Any


def setup_middleware(mcp: Any) -> None:
    """Register all middleware on the FastMCP instance (order: first added = outermost).

    Registers:
    - ErrorHandlingMiddleware
    - RateLimitingMiddleware (10 rps, burst 20)
    - TimingMiddleware
    - ResponseCachingMiddleware (30s TTL for read-only tools)
    - ResponseLimitingMiddleware (500k max response size)
    - LoggingMiddleware
    """
    from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
    from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
    from fastmcp.server.middleware.logging import LoggingMiddleware
    from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
    from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
    from fastmcp.server.middleware.timing import TimingMiddleware

    mcp.add_middleware(ErrorHandlingMiddleware())
    mcp.add_middleware(RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20))
    mcp.add_middleware(TimingMiddleware())
    mcp.add_middleware(
        ResponseCachingMiddleware(
            call_tool_settings=CallToolSettings(
                included_tools=[
                    "thegent_ps",
                    "thegent_plan_status",
                    "thegent_plan_get",
                    "thegent_protocol_list",
                    "thegent_protocol_get",
                    "thegent_validation_report",
                    "thegent_team_list",
                    "thegent_dag_ready",
                    "thegent_list_agents",
                    "thegent_list_droids",
                    "thegent_list_models",
                    "thegent_session_contract_health_trend",
                    "thegent_sitback_dashboard",
                    "thegent_inspect",
                    "thegent_inbox_list",
                    "thegent_resolve_model_route",
                    "thegent_list_operations",
                    "thegent_list_modes",
                ],
                ttl=30,
            ),
        ),
    )
    mcp.add_middleware(ResponseLimitingMiddleware(max_size=500_000))
    mcp.add_middleware(LoggingMiddleware())
