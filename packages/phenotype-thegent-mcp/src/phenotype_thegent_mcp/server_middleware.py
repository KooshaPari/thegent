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
                    "phenotype_thegent_ps",
                    "phenotype_thegent_plan_status",
                    "phenotype_thegent_plan_get",
                    "phenotype_thegent_protocol_list",
                    "phenotype_thegent_protocol_get",
                    "phenotype_thegent_validation_report",
                    "phenotype_thegent_team_list",
                    "phenotype_thegent_dag_ready",
                    "phenotype_thegent_list_agents",
                    "phenotype_thegent_list_droids",
                    "phenotype_thegent_list_models",
                    "phenotype_thegent_session_contract_health_trend",
                    "phenotype_thegent_sitback_dashboard",
                    "phenotype_thegent_inspect",
                    "phenotype_thegent_inbox_list",
                    "phenotype_thegent_resolve_model_route",
                    "phenotype_thegent_list_operations",
                    "phenotype_thegent_list_modes",
                ],
                ttl=30,
            ),
        ),
    )
    mcp.add_middleware(ResponseLimitingMiddleware(max_size=500_000))
    mcp.add_middleware(LoggingMiddleware())
