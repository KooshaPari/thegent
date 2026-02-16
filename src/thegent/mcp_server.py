"""FastMCP server for thegent."""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Literal, cast

from fastmcp import FastMCP
from fastmcp._vendor.docket_di import Depends
from fastmcp.server.context import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)

# Treat Context as Any for typing in this module to accommodate FastMCP runtime context shapes
Context = Any
from fastmcp.server.dependencies import CurrentContext
from fastmcp.server.event_store import EventStore
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.tasks.config import TaskConfig
from fastmcp.server.transforms import PromptsAsTools, ResourcesAsTools
from fastmcp.tools.tool import ToolResult
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from thegent.config import ThegentSettings


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """G-FM-01: Bearer token authentication for MCP HTTP endpoints."""

    async def dispatch(self, request: Request, call_next):
        settings = ThegentSettings()
        if settings.mcp_auth_mode == "bearer":
            # Allow health check without auth
            if request.url.path == "/health":
                return await call_next(request)

            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse({"error": "Missing or invalid Authorization"}, status_code=401)
            token = auth[7:]
            valid_tokens = [t.strip() for t in settings.mcp_bearer_tokens.split(",") if t.strip()]
            if token not in valid_tokens:
                return JSONResponse({"error": "Invalid token"}, status_code=401)
        return await call_next(request)


from thegent.cli_impl import (
    ELICIT_CWD_MSG,
    ELICIT_OWNER_MSG,
    _coerce_issue_types,
    _default_owner_tag,
    _resolve_cwd,
    bg_impl,
    dag_list_impl,
    get_server_meta_impl,
    inspect_impl,
    list_agents_impl,
    list_droids_impl,
    list_models_impl,
    logs_impl,
    observe_summary_impl,
    ps_impl,
    run_impl,
    session_contract_audit_impl,
    session_contract_health_gate_impl,
    session_contract_health_report_impl,
    session_contract_health_trend_impl,
    session_contract_negotiate_impl,
    status_impl,
    stop_impl,
    wait_impl,
)
from thegent.output_parser import OUTPUT_PARSER_SCHEMA_VERSION

# G-FM-04: Icon mapping for tools; wire when FastMCP supports icon parameter
TOOL_ICONS = {
    "thegent_run": "▶",
    "thegent_bg": "⏸",
    "thegent_stop": "⏹",
    "thegent_logs": "📄",
    "thegent_ps": "📋",
    "thegent_status": "ℹ",
    "thegent_wait": "⏳",
    "thegent_inspect": "🔍",
    "thegent_list_agents": "👤",
    "thegent_list_droids": "🤖",
    "thegent_list_models": "📦",
    "thegent_dag_list": "📊",
    "thegent_observe_summary": "📈",
    "thegent_sitback_dashboard": "🖥️",
    "thegent_terminal_list": "🖥️",
    "thegent_terminal_inspect": "👁️",
    "thegent_terminal_send": "⌨️",
    "thegent_terminal_attach": "🔗",
    "thegent_ddg_search": "🔍",
}

_log = logging.getLogger(__name__)


def get_default_cwd(ctx: Context = CurrentContext()) -> Path | None:
    """Inject cwd from request meta (meta.cwd). Client can send meta.cwd in request."""
    if ctx.request_context and ctx.request_context.meta:
        meta = ctx.request_context.meta
        cwd = getattr(meta, "cwd", None) if meta else None
        if cwd:
            return Path(str(cwd)).expanduser().resolve()
    return None


def get_default_owner(ctx: Context = CurrentContext()) -> str | None:
    """Inject owner from request meta (meta.owner). Client can send meta.owner in request."""
    if ctx.request_context and ctx.request_context.meta:
        meta = ctx.request_context.meta
        return getattr(meta, "owner", None) if meta else None
    return None


@lifespan
async def thegent_lifespan(_: FastMCP) -> AsyncIterator[dict[str, Any] | None]:
    """Startup and teardown for thegent MCP server. See gofastmcp.com/servers/lifespan."""
    _log.info("thegent MCP server starting")

    # ROB-013: Configuration validation on startup (fail-fast)
    from thegent.config import ThegentSettings

    try:
        settings = ThegentSettings()
        settings.validate_setup()
        _log.info("Configuration validated successfully")
    except Exception as e:
        _log.critical("Configuration validation failed: %s", e)
        # In mission-critical rigor, we might want to exit here,
        # but for now we'll just log loudly to avoid breaking all installs.

    proxy_proc = None
    if os.environ.get("THGENT_BUNDLE_PROXY", "").lower() in ("1", "true", "yes"):
        try:
            from thegent.agents.cliproxy_manager import start_proxy_managed
            from thegent.config import ThegentSettings

            settings = ThegentSettings()
            proxy_proc, base_url = start_proxy_managed(settings)
            if proxy_proc is not None:
                _log.info("started CLIProxyAPIPlus proxy at %s", base_url)
        except Exception as e:
            _log.warning("could not start bundled proxy: %s", e)
    try:
        yield {}
    finally:
        # G-OP-10: Optional drain wait for in-flight requests
        wait_s = settings.shutdown_wait_s
        if wait_s > 0:
            _log.info("shutdown wait %ds for in-flight requests", wait_s)
            await asyncio.sleep(wait_s)

        # G-OP-10: Optional active-run wait — poll ps_impl until no running sessions or timeout
        active_wait_s = settings.shutdown_wait_active_s
        if active_wait_s > 0:
            start = time.monotonic()
            poll_interval = 2.0
            while (time.monotonic() - start) < active_wait_s:
                try:
                    rows = await asyncio.to_thread(ps_impl, None, True, False)
                    running = [r for r in rows if (r.get("status") or "").lower() == "running"]
                    if not running:
                        _log.info("no active runs; shutdown proceeding")
                        break
                    _log.info("shutdown waiting for %d active run(s)", len(running))
                except Exception as e:
                    _log.warning("ps_impl during shutdown: %s", e)
                    break
                await asyncio.sleep(min(poll_interval, active_wait_s - (time.monotonic() - start)))
            else:
                _log.info("active-run wait timeout (%ds); proceeding with shutdown", active_wait_s)

        if proxy_proc is not None and proxy_proc.poll() is None:
            proxy_proc.terminate()
            try:
                proxy_proc.wait(timeout=5)
            except Exception:
                proxy_proc.kill()
            _log.info("stopped bundled proxy")
        _log.info("shutting down")


mcp = FastMCP("thegent", lifespan=thegent_lifespan)

# --- Middleware (order: first added = outermost) ---
mcp.add_middleware(ErrorHandlingMiddleware())
mcp.add_middleware(RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20))
mcp.add_middleware(TimingMiddleware())
mcp.add_middleware(
    ResponseCachingMiddleware(
        call_tool_settings=CallToolSettings(
            included_tools=[
                "thegent_ps",
                "thegent_list_agents",
                "thegent_list_droids",
                "thegent_list_models",
                "thegent_session_contract_health_trend",
                "thegent_sitback_dashboard",
            ],
            ttl=30,
        ),
    ),
)
mcp.add_middleware(ResponseLimitingMiddleware(max_size=500_000))
mcp.add_middleware(LoggingMiddleware())


def _stable_json(payload: Any) -> str:
    """Serialize dict/list payloads with stable key order for deterministic MCP transport."""
    return json.dumps(payload, sort_keys=True)


# --- MCP Resources ---


@mcp.resource(
    "thegent://sessions{?include_contract}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_sessions(include_contract: bool = False) -> str:
    """List all background sessions. Returns JSON array of session metadata."""
    return json.dumps(ps_impl(owner=None, all=True, include_contract=include_contract))


@mcp.resource(
    "thegent://session/{id}/meta{?include_contract}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_meta(id: str, include_contract: bool = False) -> str:
    """Get session metadata (status, pid, owner) by ID."""
    return json.dumps(status_impl(session_id=id, include_contract=include_contract))


@mcp.resource(
    "thegent://session/{id}/logs{?stderr,tail}",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_logs(id: str, stderr: bool = False, tail: int | None = None) -> str:
    """Get logs from a background session. Use ?stderr=true for stderr, ?tail=N for last N lines."""
    return logs_impl(session_id=id, tail=tail, stderr=stderr)


@mcp.resource(
    "thegent://dag",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_dag() -> str:
    """Get DAG from .factory/dag-session.md as {frontmatter, tasks} JSON."""
    return json.dumps(dag_list_impl(cd=None))


@mcp.resource(
    "thegent://agents",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_agents() -> str:
    """List available agents. Returns JSON array of {name, backend}."""
    return json.dumps(list_agents_impl())


@mcp.resource(
    "thegent://models{?provider,include_contract}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_models(
    provider: str | None = None,
    include_contract: bool = False,
) -> str:
    """List models, optionally filtered by provider."""
    return json.dumps(list_models_impl(provider=provider, include_contract=include_contract))


@mcp.resource(
    "thegent://models/contract",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_models_contract() -> str:
    """Return model routing contract schema metadata."""
    from thegent.models import route_contract

    return json.dumps(route_contract())


@mcp.resource(
    "thegent://sessions/contracts{?owner,all,missing_only,summary_only,strict}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_contracts(
    owner: str | None = None,
    all: bool = False,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> str:
    """Contract audit for sessions including completeness summary."""
    return json.dumps(
        session_contract_audit_impl(
            owner=owner,
            all=all,
            missing_only=missing_only,
            summary_only=summary_only,
            strict=strict,
        )
    )


@mcp.resource(
    "thegent://sessions/contracts/health{?owner,all,strict,min_healthy_ratio,policy_profile,no_worse_than_baseline,regression_tolerance}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_contract_health_gate(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> str:
    """
    Contract health gate for CI/automation and policy enforcement.
    Returns schema-aware payload with `schema_version` and `payload_type`.
    """
    return _stable_json(
        session_contract_health_gate_impl(
            owner=owner,
            all=all,
            strict=strict,
            min_healthy_ratio=min_healthy_ratio,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
        )
    )


@mcp.resource(
    "thegent://sessions/contracts/report{?owner,all,strict,top_blocked,policy_profile,no_worse_than_baseline,regression_tolerance}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_contract_health_report(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> str:
    """
    Contract health report for issue/owner triage and observability.
    Returns schema-aware payload with `schema_version` and `payload_type`.
    """
    return _stable_json(
        session_contract_health_report_impl(
            owner=owner,
            all=all,
            strict=strict,
            top_blocked=top_blocked,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
        )
    )


@mcp.resource(
    "thegent://sessions/contracts/trend{?payload_type,owner,all,strict,policy_profile,min_healthy_ratio,top_blocked,limit}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_contract_health_trend(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
) -> str:
    """Contract health trend snapshots for a scoped report/gate policy context."""
    return _stable_json(
        session_contract_health_trend_impl(
            payload_type=payload_type,
            owner=owner,
            all=all,
            strict=strict,
            policy_profile=policy_profile,
            min_healthy_ratio=min_healthy_ratio,
            top_blocked=top_blocked,
            limit=limit,
        )
    )


@mcp.resource(
    "thegent://observe/summary{?limit,drift_window,structural_budget_pct,semantic_budget_pct,provider,trend_samples,top_escalations}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_observe_summary(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    trend_samples: int = 0,
    top_escalations: int = 10,
) -> str:
    """Observe summary payload for contract KPIs, drift status, and escalation backlog."""
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    return _stable_json(payload)


@mcp.resource(
    "thegent://meta",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_meta() -> str:
    """Server metadata: version, capabilities, health payload schema."""
    return json.dumps(get_server_meta_impl())


@mcp.resource(
    "thegent://operations{?operation}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_operations(operation: str | None = None) -> str:
    """Universal operation taxonomy: orchestrate, govern, recover, observe, plan."""
    from thegent.operations import Operation, get_operations_by_type, list_operations

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            return json.dumps({"error": f"Unknown operation: {operation}"})
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()
    return json.dumps(data)


@mcp.resource(
    "thegent://modes{?mode}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_modes(mode: str | None = None) -> str:
    """Multi-agent orchestration modes: sequential_delegation, parallel_consensus, review_loop."""
    from thegent.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            return json.dumps({"error": f"Unknown mode: {mode}"})
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()
    return json.dumps(data)


# --- MCP Prompts ---


@mcp.prompt
def thegent_run_agent(agent: str, prompt: str, cd: str | None = None, mode: str = "write") -> str:
    """
    Generate a prompt to run an agent synchronously.
    Use thegent_run tool to execute.
    """
    cd_hint = f" in directory {cd}" if cd else ""
    return f"Run agent '{agent}'{cd_hint} with mode '{mode}'. Task: {prompt}"


@mcp.prompt
def thegent_create_wbs(feature: str, scope: str | None = None) -> str:
    """
    Generate a prompt to create a Work Breakdown Structure (WBS) for a feature.
    Use thegent_run with a planning agent (e.g. cursor, claude) to execute.
    """
    scope_hint = f" Scope: {scope}." if scope else ""
    return f"Create a phased WBS (Work Breakdown Structure) for: {feature}.{scope_hint} Use phases (Discovery, Design, Build, Test, Deploy) and DAG-style dependencies."


@mcp.prompt
def thegent_bg_task(agent: str, prompt: str, owner: str | None = None) -> str:
    """
    Generate a prompt to start an agent task in the background.
    Use thegent_bg tool to execute.
    """
    owner_hint = f" (owner: {owner})" if owner else ""
    return f"Start background task: agent '{agent}'{owner_hint}. Task: {prompt}"


# --- MCP Tools ---


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_negotiate_contract(
    contract_id: str,
    supported_versions: list[str],
) -> str:
    """
    Negotiate a contract version between client and server (WP-7001).

    Args:
        contract_id: The ID of the contract (e.g. 'csm', 'task-tool')
        supported_versions: List of versions supported by the client, in order of preference.

    Returns: JSON string with 'version', 'status', 'reason'.
    """
    res = session_contract_negotiate_impl(contract_id, supported_versions)
    return json.dumps(res, indent=2)


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False},
    task=TaskConfig(mode="optional"),
)
async def thegent_run(
    prompt: str,
    agent: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    cd: str | None = None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
    include_contract: bool = False,
    confidence: float | None = None,
    arbitration: str | None = None,
    ctx: Any = CurrentContext(),
    default_cwd: Any = Depends(get_default_cwd),
) -> ToolResult | str:
    """
    Run an agent synchronously with a prompt.

    Args:
        prompt: The task prompt (required)
        agent: Agent/provider name (optional when model given for model-first routing)
        model: Model ID (e.g. gemini-3-flash, claude-sonnet-4). When set, agent can be omitted for auto-route.
        provider: Provider hint for model-first (use this provider if it serves the model)
        cd: Optional working directory
    mode: 'write' or 'full' (default: 'write')
    timeout: Timeout in seconds (default: 90)
    full: Return full output instead of condensed (default: False)
    include_contract: Include resolved route contract metadata for model-based routing
    confidence: Required confidence threshold (0.0-1.0)
    arbitration: Arbitration role (e.g. planner, operator, reviewer)

    Returns: JSON string with keys: stdout, stderr, exit_code, timed_out and optional routing metadata.
    """
    # Model-first: resolve model -> (agent, model_alias)
    request_payload: dict[str, Any] = {
        "model": model,
        "provider_hint": provider,
        "policy": None,
        "route_contract": None,
    }
    if model and not agent:
        from thegent.config import ThegentSettings
        from thegent.models import resolve_route, resolve_route_contract

        settings = ThegentSettings()
        policy = (settings.default_routing or "prefer_direct").lower()
        if policy not in ("prefer_direct", "prefer_proxy"):
            policy = "prefer_direct"
        request_payload["policy"] = policy
        resolved = resolve_route(
            model,
            provider_hint=provider,
            policy=cast("Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']", policy),
        )
        if resolved is None:
            return ToolResult(
                content=json.dumps(
                    {"error": f"No route for model '{model}'. Try thegent list-models.", "exit_code": 1}
                ),
                meta={},
            )
        agent, model = resolved[0], resolved[1]
        if include_contract:
            route = resolve_route_contract(
                model,
                provider_hint=provider,
                policy=cast("Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']", policy),
            )
            if route is not None:
                request_payload["route_contract"] = {
                    "provider": route.provider,
                    "model_alias": route.model_alias,
                    "backend_type": route.backend_type,
                    "priority": route.priority,
                    "schema_version": route.schema_version,
                }
    elif model and agent:
        from thegent.config import ThegentSettings
        from thegent.models import ModelCatalog, resolve_route, resolve_route_contract

        settings = ThegentSettings()
        policy = (settings.default_routing or "prefer_direct").lower()
        if policy not in ("prefer_direct", "prefer_proxy"):
            policy = "prefer_direct"
        request_payload["policy"] = policy
        resolved = resolve_route(
            model,
            provider_hint=agent,
            policy=cast("Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']", policy),
        )
        if resolved is None:
            routes = ModelCatalog.routes_for(model)
            available = ", ".join(sorted({r.provider for r in routes})) if routes else ""
            suffix = f" Available: {available}." if available else ""
            return ToolResult(
                content=json.dumps(
                    {"error": f"Model '{model}' not available via provider '{agent}'.{suffix}", "exit_code": 1}
                ),
                meta={},
            )
        agent, model = resolved[0], resolved[1]
        if include_contract:
            route = resolve_route_contract(
                model,
                provider_hint=agent,
                policy=cast("Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']", policy),
            )
            if route is not None:
                request_payload["route_contract"] = {
                    "provider": route.provider,
                    "model_alias": route.model_alias,
                    "backend_type": route.backend_type,
                    "priority": route.priority,
                    "schema_version": route.schema_version,
                }
    elif not agent:
        return ToolResult(
            content=json.dumps({"error": "Provide agent or model for routing.", "exit_code": 1}),
            meta={},
        )

    await cast("Any", ctx).info(f"thegent_run agent={agent} cd={cd} timeout={timeout}")
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cast("Path | None", cd_path))
    if cwd is None:
        elicitation = await cast("Any", ctx).elicit(ELICIT_CWD_MSG, response_type=str)
        if isinstance(elicitation, AcceptedElicitation):
            cwd = Path(cast("str", elicitation.data)).expanduser().resolve()
        elif isinstance(elicitation, DeclinedElicitation):
            return ToolResult(
                content=json.dumps({"error": "User declined to provide working directory.", "exit_code": 1}),
                meta={},
            )
        elif isinstance(elicitation, CancelledElicitation):
            return ToolResult(
                content=json.dumps({"error": "Elicitation cancelled.", "exit_code": 1}),
                meta={},
            )
        else:
            return ToolResult(
                content=json.dumps({"error": "Ambiguous cwd. Provide --cd /path explicitly.", "exit_code": 1}),
                meta={},
            )
    cd_path = cwd

    # Run in thread; poll and report progress every 10s until done
    start_time = time.perf_counter()
    task = asyncio.create_task(
        asyncio.to_thread(
            run_impl,
            agent=agent,
            prompt=prompt,
            cd=cd_path,
            mode=mode,
            timeout=timeout,
            full=full,
            model=model,
            provider=None,
            run_id=None,
            owner=None,
            include_contract=False,
            route_contract=None,
            route_request=None,
            lane="standard",
            confidence=confidence,
            override_reason=arbitration,
        )
    )
    last_reported = 0
    last_close_at = 0
    while not task.done():
        elapsed = int(time.perf_counter() - start_time)
        if elapsed - last_reported >= 10:
            await cast("Any", ctx).report_progress(progress=elapsed, total=timeout)
            last_reported = elapsed
        # Close SSE stream every 30s during long runs to avoid LB timeouts (SSE polling)
        if elapsed - last_close_at >= 30 and elapsed > 0:
            await cast("Any", ctx).close_sse_stream()
            last_close_at = elapsed
        await asyncio.sleep(1)
    result = await task
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if include_contract:
        payload = dict(result)
        payload["routing"] = request_payload
        payload["routing"]["resolved_agent"] = agent
        payload["routing"]["requested_model"] = request_payload.get("model")
        payload["routing"]["requested_provider_hint"] = request_payload.get("provider_hint")
        payload["routing"]["resolved_model_alias"] = model
        if not full:
            payload["extraction_schema_version"] = OUTPUT_PARSER_SCHEMA_VERSION
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed_ms},
        )
    return ToolResult(
        content=json.dumps(result),
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_bg(
    agent: str,
    prompt: str,
    cd: str | None = None,
    mode: str = "write",
    timeout: int = 90,
    owner: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    include_contract: bool = False,
    routing: str | None = None,
    failover: bool = False,
    confidence: float | None = None,
    arbitration: str | None = None,
    ctx: Any = CurrentContext(),
    default_cwd: Any = Depends(get_default_cwd),
    default_owner: Any = Depends(get_default_owner),
) -> ToolResult:
    """
    Start an agent run in the background.

    Args:
        agent: Agent name
        prompt: The task prompt
        cd: Optional working directory
        mode: 'write' or 'full' (default: 'write')
        timeout: Timeout in seconds (default: 90)
        owner: Optional owner tag for session grouping
        model: Optional model override
        provider: Optional provider hint when model is supplied.
        routing: Routing policy: prefer_direct | prefer_proxy | failover
        failover: Try next route on failures (model-first/failover mode)
        include_contract: Return resolved routing contract metadata.
        confidence: Required confidence threshold (0.0-1.0)
        arbitration: Arbitration role (e.g. planner, operator, reviewer)

    Returns: ToolResult with session_id, log_path, owner
    """
    await cast("Any", ctx).info(f"thegent_bg agent={agent} cd={cd} owner={owner}")
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cast("Path | None", cd_path))
    elicited_cwd = False
    if cwd is None:
        elicitation = await cast("Any", ctx).elicit(ELICIT_CWD_MSG, response_type=str)
        if isinstance(elicitation, AcceptedElicitation):
            cwd = Path(cast("str", elicitation.data)).expanduser().resolve()
            elicited_cwd = True
        elif isinstance(elicitation, DeclinedElicitation):
            err = {"error": "User declined to provide working directory.", "exit_code": 1}
            return ToolResult(content=json.dumps(err), structured_content=err, meta={"execution_time_ms": 0})
        elif isinstance(elicitation, CancelledElicitation):
            err = {"error": "Elicitation cancelled.", "exit_code": 1}
            return ToolResult(content=json.dumps(err), structured_content=err, meta={"execution_time_ms": 0})
        else:
            err = {"error": "Ambiguous cwd. Provide --cd /path explicitly.", "exit_code": 1}
            return ToolResult(content=json.dumps(err), structured_content=err, meta={"execution_time_ms": 0})
    cd_path = cwd
    route_contract: dict[str, Any] | None = None
    route_lookup_policy = "prefer_direct"
    routing_for_child = None
    requested_policy: str | None = None
    requested_model = model
    requested_provider = provider or agent
    requested_policy = routing or ThegentSettings().default_routing or "prefer_direct"
    from thegent.models import normalize_route_policy

    try:
        requested_policy = normalize_route_policy(requested_policy)
    except ValueError:
        requested_policy = "prefer_direct"
    route_lookup_policy = requested_policy
    if routing is not None:
        routing_for_child = requested_policy
    if route_lookup_policy == "failover":
        failover = True
        route_lookup_policy = "prefer_direct"

    owner_tag = owner or default_owner
    if owner_tag is None and elicited_cwd:
        elicitation = await cast("Any", ctx).elicit(ELICIT_OWNER_MSG, response_type=str)
        if isinstance(elicitation, AcceptedElicitation):
            owner_tag = cast("str", elicitation.data)
        elif isinstance(elicitation, DeclinedElicitation):
            owner_tag = _default_owner_tag(cwd)
        elif isinstance(elicitation, CancelledElicitation):
            return ToolResult(
                content=json.dumps({"error": "Elicitation cancelled.", "exit_code": 1}),
                meta={},
            )
        else:
            owner_tag = _default_owner_tag(cwd)
    elif owner_tag is None:
        owner_tag = _default_owner_tag(cwd)

    if include_contract and model:
        try:
            from thegent.models import resolve_route_contract
            from thegent.models import route_contract as catalog_route_contract

            contract = resolve_route_contract(
                model,
                provider_hint=requested_provider or None,
                policy=cast(
                    "Literal['prefer_direct','prefer_proxy','failover','round_robin','cheapest']", route_lookup_policy
                ),
            )
            if contract is not None:
                route_contract = {
                    "provider": contract.provider,
                    "model_alias": contract.model_alias,
                    "backend_type": contract.backend_type,
                    "priority": contract.priority,
                    "schema_version": contract.schema_version,
                    "schema": catalog_route_contract(),
                }
            else:
                route_contract = {
                    "provider": requested_provider or "",
                    "model_alias": model or "",
                    "route_lookup_failed": True,
                    "schema": catalog_route_contract(),
                }
        except Exception:
            route_contract = {
                "provider": requested_provider,
                "model_alias": model,
                "route_lookup_failed": True,
            }

    start_time = time.perf_counter()
    result = await asyncio.to_thread(
        bg_impl,
        agent=agent,
        prompt=prompt,
        cd=cd_path,
        mode=mode,
        timeout=timeout,
        full=True,
        owner=owner_tag,
        model=model,
        include_contract=include_contract,
        route_contract=route_contract,
        routing=routing_for_child,
        failover=failover,
        route_request={
            "requested_model": requested_model or "",
            "requested_provider_hint": requested_provider or "",
            "policy": requested_policy or "",
            "resolved_model_alias": model or "",
            "resolved_agent": agent or "",
        }
        if include_contract
        else None,
        lane="standard",
        confidence=confidence,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if include_contract:
        payload = dict(result)
        payload["routing"] = {
            "requested_model": requested_model,
            "requested_provider_hint": requested_provider,
            "policy": requested_policy,
            "resolved_model_alias": model,
            "resolved_agent": agent,
            "route_contract": route_contract,
        }
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed_ms},
        )
    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_ps(owner: str | None = None, all: bool = False, include_contract: bool = False) -> ToolResult:
    """
    List background sessions.

    Args:
        owner: Filter by owner tag (optional)
        all: Include completed/stopped sessions (default: False)
        include_contract: Include resolved route contract/request metadata (optional)

    Returns: JSON string with list of sessions
    """
    start_time = time.perf_counter()
    result = ps_impl(owner=owner, all=all, include_contract=include_contract)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_status(session_id: str, include_contract: bool = False) -> ToolResult:
    """
    Get status of a background session.

    Args:
        session_id: Session ID to query

    Returns: ToolResult with session status and metadata
    """
    _log.info("thegent_status session_id=%s", session_id)
    start_time = time.perf_counter()
    result = status_impl(session_id=session_id, include_contract=include_contract)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_logs(session_id: str, tail: int | None = None, stderr: bool = False) -> ToolResult:
    """
    Get logs from a background session.

    Args:
        session_id: Session ID to query
        tail: Number of lines to return from end (optional, default: all)
        stderr: Include stderr instead of stdout (default: False)

    Returns: Log text
    """
    _log.info("thegent_logs session_id=%s tail=%s", session_id, tail)
    start_time = time.perf_counter()
    result = logs_impl(session_id=session_id, tail=tail, stderr=stderr)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_inspect(
    session_ids: list[str] | None = None,
    owner: str | None = None,
    tail: int = 50,
    stderr: bool = False,
    include_contract: bool = False,
) -> ToolResult:
    """
    Get status and logs for one or more sessions. No shell loop needed.

    Args:
        session_ids: Session ID(s) to inspect. Omit when using owner.
        owner: Inspect all sessions for this owner (alternative to session_ids)
        tail: Log lines per session (default: 50)
        stderr: Show stderr instead of stdout (default: False)

    Returns: ToolResult with list of {session_id, status, logs}
    """
    start_time = time.perf_counter()
    result = inspect_impl(
        session_ids=session_ids or [],
        owner=owner,
        tail=tail,
        stderr=stderr,
        include_contract=include_contract,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_session_contracts(
    owner: str | None = None,
    all: bool = False,
    missing_only: bool = False,
    summary_only: bool = False,
    strict: bool = False,
) -> ToolResult:
    """
    List session routing contract metadata and report completeness.
    """
    start_time = time.perf_counter()
    payload = session_contract_audit_impl(
        owner=owner,
        all=all,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(payload), structured_content=payload, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_session_contract_health_gate(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> ToolResult:
    """
    Evaluate session contract health against a minimum ratio gate.

    Returns a unified health payload with `schema_version`, `payload_type`,
    `pass`, `status`, `total_sessions`, `healthy_sessions`, `unhealthy_sessions`,
    `blocked_sessions_count`, `blocked_ratio`, and `blocked_sessions`.
    """
    start_time = time.perf_counter()
    payload = session_contract_health_gate_impl(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=_stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "payload_signature": payload.get("payload_signature"),
            "status": payload.get("status", ""),
            "policy_profile": payload.get("policy_profile", "custom"),
            "decision_reasons": payload.get("decision_reasons", []),
            "total": payload.get("total", 0),
            "healthy_count": payload.get("healthy_count", 0),
            "unhealthy_count": payload.get("unhealthy_count", 0),
            "blocked_count": payload.get("blocked_count", 0),
            "top_blocked_count": payload.get("top_blocked_count", 0),
            "blocked_sessions_cap": payload.get("blocked_sessions_cap", 0),
        },
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_session_contract_health_report(
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    top_blocked: int = 25,
    policy_profile: str | None = None,
    no_worse_than_baseline: bool = False,
    regression_tolerance: float = 0.0,
) -> ToolResult:
    """
    Get contract health report with issue taxonomy and owner-level breakdown.

    Returns a unified health payload with `schema_version`, `payload_type`,
    `status`, `total_sessions`, `healthy_sessions`, `unhealthy_sessions`,
    `blocked_sessions_count`, `blocked_ratio`, `issue_breakdown`, and `owner_breakdown`.
    """
    start_time = time.perf_counter()
    payload = session_contract_health_report_impl(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=_stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "payload_signature": payload.get("payload_signature"),
            "status": payload.get("status", ""),
            "policy_profile": payload.get("policy_profile", "custom"),
            "decision_reasons": payload.get("decision_reasons", []),
            "total": payload.get("total", 0),
            "healthy_count": payload.get("healthy_count", 0),
            "unhealthy_count": payload.get("unhealthy_count", 0),
            "blocked_count": payload.get("blocked_count", 0),
            "top_blocked_count": payload.get("top_blocked_count", 0),
        },
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_session_contract_health_trend(
    payload_type: str = "session_contract_health_report",
    owner: str | None = None,
    all: bool = False,
    strict: bool = False,
    policy_profile: str | None = None,
    min_healthy_ratio: float = 1.0,
    top_blocked: int = 25,
    limit: int = 20,
) -> ToolResult:
    """
    Get trend snapshots and deltas for session contract health scopes.
    """
    start_time = time.perf_counter()
    payload = session_contract_health_trend_impl(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    result = ToolResult(
        content=_stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "schema_version": payload.get("schema_version", ""),
            "schema_compat_mode": payload.get("schema_compat_mode", "compat"),
            "payload_type": payload.get("payload_type", ""),
            "trend_payload_type": payload.get("trend_payload_type", ""),
            "generated_at_utc": payload.get("generated_at_utc", ""),
            "scope_key": payload.get("scope_key", {}),
            "scope_key_json": payload.get(
                "scope_key_json",
                _stable_json(payload.get("scope_key", {})),
            ),
            "scope_payload_type": payload.get(
                "scope_payload_type",
                (payload.get("scope_key") or {}).get("payload_type", ""),
            ),
            "scope_owner": payload.get("scope_owner", (payload.get("scope_key") or {}).get("owner", "")),
            "scope_all": payload.get("scope_all", (payload.get("scope_key") or {}).get("all", False)),
            "scope_strict": payload.get("scope_strict", (payload.get("scope_key") or {}).get("strict", False)),
            "scope_policy_profile": payload.get(
                "scope_policy_profile",
                (payload.get("scope_key") or {}).get("policy_profile", "custom"),
            ),
            "scope_min_healthy_ratio": payload.get(
                "scope_min_healthy_ratio",
                (payload.get("scope_key") or {}).get("min_healthy_ratio", None),
            ),
            "scope_top_blocked": payload.get(
                "scope_top_blocked",
                (payload.get("scope_key") or {}).get("top_blocked", None),
            ),
            "snapshot_count": payload.get("snapshot_count", 0),
            "snapshot_ids_csv": payload.get(
                "snapshot_ids_csv",
                ", ".join(
                    [
                        str((s or {}).get("captured_at_utc", ""))
                        for s in (payload.get("snapshots", []) or [])
                        if (s or {}).get("captured_at_utc", "")
                    ]
                ),
            ),
            "snapshot_ids_hash": payload.get(
                "snapshot_ids_hash",
                hashlib.sha256(
                    payload.get(
                        "snapshot_ids_csv",
                        ", ".join(
                            [
                                str((s or {}).get("captured_at_utc", ""))
                                for s in (payload.get("snapshots", []) or [])
                                if (s or {}).get("captured_at_utc", "")
                            ]
                        ),
                    ).encode("utf-8")
                ).hexdigest(),
            ),
            "snapshot_window_seconds": payload.get("snapshot_window_seconds", None),
            "snapshot_window_hash": payload.get(
                "snapshot_window_hash",
                hashlib.sha256(str(payload.get("snapshot_window_seconds", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_interval_seconds_avg": payload.get("snapshot_interval_seconds_avg", None),
            "snapshot_interval_hash": payload.get(
                "snapshot_interval_hash",
                hashlib.sha256(str(payload.get("snapshot_interval_seconds_avg", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_density_per_hour": payload.get("snapshot_density_per_hour", None),
            "snapshot_density_hash": payload.get(
                "snapshot_density_hash",
                hashlib.sha256(str(payload.get("snapshot_density_per_hour", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_issue_churn_count": payload.get("snapshot_issue_churn_count", None),
            "snapshot_issue_churn_hash": payload.get(
                "snapshot_issue_churn_hash",
                hashlib.sha256(str(payload.get("snapshot_issue_churn_count", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_health_volatility": payload.get("snapshot_health_volatility", None),
            "snapshot_health_volatility_hash": payload.get(
                "snapshot_health_volatility_hash",
                hashlib.sha256(str(payload.get("snapshot_health_volatility", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_freshness_seconds": payload.get("snapshot_freshness_seconds", None),
            "snapshot_freshness_hash": payload.get(
                "snapshot_freshness_hash",
                hashlib.sha256(str(payload.get("snapshot_freshness_seconds", None)).encode("utf-8")).hexdigest(),
            ),
            "snapshot_retention_max_lines": payload.get("snapshot_retention_max_lines", 0),
            "delta_summary_json": payload.get(
                "delta_summary_json",
                _stable_json(payload.get("delta_summary", {})),
            ),
            "blocked_ratio_delta": payload.get(
                "blocked_ratio_delta",
                payload.get("delta_summary", {}).get("blocked_ratio_delta", None),
            ),
            "blocked_count_delta": payload.get(
                "blocked_count_delta",
                payload.get("delta_summary", {}).get("blocked_count_delta", None),
            ),
            "latest_status": payload.get("latest_status", (payload.get("latest") or {}).get("status", "")),
            "latest_pass": payload.get("latest_pass", (payload.get("latest") or {}).get("pass", None)),
            "latest_captured_at_utc": payload.get(
                "latest_captured_at_utc",
                (payload.get("latest") or {}).get("captured_at_utc", ""),
            ),
            "latest_blocked_ratio": payload.get(
                "latest_blocked_ratio",
                (payload.get("latest") or {}).get("blocked_ratio", None),
            ),
            "latest_blocked_count": payload.get(
                "latest_blocked_count",
                (payload.get("latest") or {}).get("blocked_count", None),
            ),
            "latest_issue_types_count": payload.get(
                "latest_issue_types_count",
                len(_coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_csv": payload.get(
                "latest_issue_types_csv",
                ", ".join(_coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_json": payload.get(
                "latest_issue_types_json",
                _stable_json(_coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
            ),
            "latest_issue_types_hash": payload.get(
                "latest_issue_types_hash",
                hashlib.sha256(
                    payload.get(
                        "latest_issue_types_json",
                        _stable_json(_coerce_issue_types((payload.get("latest") or {}).get("issue_types", []))),
                    ).encode("utf-8")
                ).hexdigest(),
            ),
            "compat_mode": (payload.get("compat") or {}).get("mode", "compat"),
            "compat_aliases": (payload.get("compat") or {}).get("aliases", {}),
            "compat_aliases_count": payload.get(
                "compat_aliases_count",
                len((payload.get("compat") or {}).get("aliases", {}) or {}),
            ),
        },
    )
    return result


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_observe_summary(
    limit: int = 500,
    drift_window: int = 50,
    structural_budget_pct: float = 5.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    trend_samples: int = 0,
    top_escalations: int = 10,
) -> ToolResult:
    """
    Get unified observability summary for KPIs, drift budget, and escalations.
    """
    start_time = time.perf_counter()
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    kpis = payload.get("kpis", {})
    drift = payload.get("drift", {})
    escalation = payload.get("escalation", {})
    return ToolResult(
        content=_stable_json(payload),
        structured_content=payload,
        meta={
            "execution_time_ms": elapsed_ms,
            "payload_type": payload.get("payload_type", "observe_summary"),
            "payload_schema_version": payload.get("payload_schema_version", "observe-summary-schema-v1"),
            "status": payload.get("status", ""),
            "alerts_count": len(payload.get("alerts", [])),
            "kpi_total_events": kpis.get("total_events", 0),
            "fallback_rate": kpis.get("fallback_rate", 0.0),
            "structural_drift_pct": kpis.get("structural_drift_pct", 0.0),
            "semantic_drift_pct": kpis.get("semantic_drift_pct", 0.0),
            "drift_within_budget": drift.get("within_budget", True),
            "drift_structural_rate_pct": drift.get("structural_rate_pct", 0.0),
            "drift_semantic_rate_pct": drift.get("semantic_rate_pct", 0.0),
            "drift_structural_budget_pct": drift.get("structural_budget_pct", structural_budget_pct),
            "drift_semantic_budget_pct": drift.get("semantic_budget_pct", semantic_budget_pct),
            "backlog_count": escalation.get("backlog_count", 0),
            "backlog_past_sla_count": escalation.get("past_sla_count", 0),
            "trend_enabled": payload.get("trend_summary", {}).get("enabled", False),
            "trend_samples_requested": payload.get("generated_query", {}).get("trend_samples", 0),
            "top_escalations_count": escalation.get("top_escalations_count", 0),
            "provider": escalation.get("provider", provider),
            "top_escalations_requested": top_escalations,
        },
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_wait(session_id: str, timeout: int | None = None) -> ToolResult:
    """
    Wait for a background session to complete.

    Args:
        session_id: Session ID to wait for
        timeout: Timeout in seconds (optional)

    Returns: ToolResult with final status and exit code
    """
    _log.info("thegent_wait session_id=%s timeout=%s", session_id, timeout)
    start_time = time.perf_counter()
    result = wait_impl(session_id=session_id, timeout=timeout)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False})
def thegent_stop(session_id: str, force: bool = False) -> ToolResult:
    """
    Stop a background session.

    Args:
        session_id: Session ID to stop
        force: Use SIGKILL instead of SIGTERM (default: False)

    Returns: ToolResult with status
    """
    _log.info("thegent_stop session_id=%s force=%s", session_id, force)
    start_time = time.perf_counter()
    result = stop_impl(session_id=session_id, force=force)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_operations(operation: str | None = None) -> ToolResult:
    """
    List universal operation taxonomy: orchestrate, govern, recover, observe, plan.

    Args:
        operation: Optional filter (orchestrate | govern | recover | observe | plan)

    Returns: JSON with operations and their commands/mcp_tools.
    """
    from thegent.operations import Operation, get_operations_by_type, list_operations

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            return ToolResult(content=json.dumps({"error": f"Unknown operation: {operation}"}))
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()
    return ToolResult(content=_stable_json(data))


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_modes(mode: str | None = None) -> ToolResult:
    """
    List multi-agent orchestration modes (G-KD-04).

    Args:
        mode: Optional filter (sequential_delegation | parallel_consensus | review_loop)

    Returns: JSON with modes, phases, use_case, risk_profile, selection_hint.
    """
    from thegent.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            return ToolResult(content=json.dumps({"error": f"Unknown mode: {mode}"}))
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()
    return ToolResult(content=_stable_json(data))


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_agents() -> ToolResult:
    """
    List available agents.

    Returns: JSON string with list of {name, backend}
    """
    start_time = time.perf_counter()
    result = list_agents_impl()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_droids(
    cd: str | None = None,
    default_cwd: Any = Depends(get_default_cwd),
) -> ToolResult:
    """
    List available droids.

    Args:
        cd: Optional working directory (or use meta.cwd in request)
        Returns: JSON string with list of droid names
    """
    cd_path = Path(cd) if cd else default_cwd
    start_time = time.perf_counter()
    result = list_droids_impl(cd=cast("Path | None", cd_path))
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content={"droids": result},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_models(
    provider: str | None = None,
    include_contract: bool = False,
    by_model: bool = False,
) -> ToolResult:
    """
    List available models (optionally filtered by provider).

    Args:
        provider: Optional provider filter (minimax, glm, cursor, gemini, copilot, claude, codex)
        include_contract: If true, return route metadata payload instead of provider/model map.
        by_model: If true, return {model_id: [provider, ...]} for routing (R5).

    Returns: JSON string with {provider: [model_names]}, {model_id: [providers]}, or contract payload.
    """
    start_time = time.perf_counter()
    result = list_models_impl(provider=provider, include_contract=include_contract, by_model=by_model)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_resolve_model_route(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
) -> ToolResult:
    """
    Resolve a model to a concrete routing target.

    Args:
        model: Model identifier (alias or canonical)
        provider: Optional provider hint
        policy: Routing policy: prefer_direct, prefer_proxy, failover

    Returns: JSON contract payload with resolved route if available.
    """
    from thegent.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        return ToolResult(
            content=json.dumps(
                {
                    "error": "Invalid policy",
                    "policy": policy,
                    "valid_policies": ["prefer_direct", "prefer_proxy", "failover"],
                }
            ),
            meta={"execution_time_ms": 0},
        )

    start_time = time.perf_counter()
    normalized = normalize_model_id(model)
    route = resolve_route_contract(model, provider_hint=provider, policy=policy_value)
    available_routes = [
        {
            "provider": r.provider,
            "backend_type": r.backend_type,
            "model_alias": r.model_alias,
            "priority": r.priority,
        }
        for r in sorted(ModelCatalog.routes_for(model), key=lambda r: (r.provider, r.priority, r.model_alias))
    ]
    payload = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is not None:
        payload["resolved_route"] = {
            "provider": route.provider,
            "model_alias": route.model_alias,
            "backend_type": route.backend_type,
            "priority": route.priority,
            "schema_version": route.schema_version,
        }
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(payload),
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_dag_list(
    cd: str | None = None,
    ctx: Any = CurrentContext(),
    default_cwd: Any = Depends(get_default_cwd),
) -> ToolResult:
    """
    List DAG tasks from .factory/dag-session.md.

    Args:
        cd: Optional working directory (or use meta.cwd in request)

    Returns: JSON string with {frontmatter, tasks}
    """
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cast("Path | None", cd_path))
    if cwd is None:
        elicitation = await cast("Any", ctx).elicit(ELICIT_CWD_MSG, response_type=str)
        if isinstance(elicitation, AcceptedElicitation):
            cwd = Path(cast("str", elicitation.data)).expanduser().resolve()
        elif isinstance(elicitation, DeclinedElicitation):
            return ToolResult(
                content=json.dumps(
                    {"error": "User declined to provide working directory.", "frontmatter": {}, "tasks": []}
                ),
                meta={},
            )
        elif isinstance(elicitation, CancelledElicitation):
            return ToolResult(
                content=json.dumps({"error": "Elicitation cancelled.", "frontmatter": {}, "tasks": []}),
                meta={},
            )
        else:
            return ToolResult(
                content=json.dumps(
                    {
                        "error": "Ambiguous cwd. Provide --cd /path or run from project root.",
                        "frontmatter": {},
                        "tasks": [],
                    }
                ),
                meta={},
            )
    start_time = time.perf_counter()
    result = dag_list_impl(cd=cwd)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_terminal_list(all: bool = False) -> ToolResult:
    """
    List active terminal panes (tmux).

    Args:
        all: Show all panes, not just Claude Code (default: False)
    """
    from thegent.tools.terminal import is_claude_code_pane, list_tmux_panes

    panes = list_tmux_panes()
    result = []
    for p in panes:
        is_cc = is_claude_code_pane(p)
        if not all and not is_cc:
            continue
        result.append(
            {
                "pane_id": p.pane_id,
                "session": p.session_name,
                "window": p.window_index,
                "pane": p.pane_index,
                "path": p.path,
                "command": p.command,
                "title": p.title,
                "is_claude_code": is_cc,
            }
        )
    return ToolResult(content=json.dumps(result), structured_content=result)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_terminal_inspect(pane_id: str, last_lines: int = 50) -> ToolResult:
    """
    Capture the content of a terminal pane.
    """
    from thegent.tools.terminal import capture_tmux_pane

    content = capture_tmux_pane(pane_id, last_lines=last_lines)
    return ToolResult(content=content)


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_send(pane_id: str, text: str, enter: bool = True) -> ToolResult:
    """
    Send text/keys to a terminal pane.
    """
    from thegent.tools.terminal import send_to_tmux_pane

    success = send_to_tmux_pane(pane_id, text, enter=enter)
    return ToolResult(content=json.dumps({"success": success}), structured_content={"success": success})


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_attach(pane_id: str) -> ToolResult:
    """
    Get instructions to attach to a terminal session.
    """
    from thegent.tools.terminal import list_tmux_panes

    panes = list_tmux_panes()
    p = next((p for p in panes if p.pane_id == pane_id), None)
    if not p:
        return ToolResult(
            content=json.dumps({"error": "Pane not found"}), structured_content={"error": "Pane not found"}
        )

    msg = f"To attach to this session, run: tmux attach-session -t {p.session_name}"
    return ToolResult(
        content=msg,
        structured_content={"session": p.session_name, "command": f"tmux attach-session -t {p.session_name}"},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_sharecli_status() -> ToolResult:
    """
    Get status from sharecli harness.
    """
    from thegent.tools.terminal import sharecli_status

    status = sharecli_status()
    return ToolResult(content=status)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_ddg_search(query: str, num_results: int = 5) -> ToolResult:
    """
    Search DuckDuckGo for heavy web research.
    """
    from thegent.tools.research import ddg_search

    results = ddg_search(query, max_results=num_results)
    return ToolResult(content=json.dumps(results), structured_content=results)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_suggest_prompt(
    raw_prompt: str,
    ctx: Any = CurrentContext(),
) -> ToolResult:
    """
    Refine a raw prompt using LLM sampling. Returns a suggested, clearer prompt.
    When client lacks sampling support, returns raw_prompt with a note.
    """
    start_time = time.perf_counter()
    try:
        result = await cast("Any", ctx).sample(
            f"Refine this task prompt to be clearer and more actionable for an AI agent. Keep it concise. Return only the refined prompt, no explanation.\n\nRaw prompt:\n{raw_prompt}",
            temperature=0.3,
            max_tokens=500,
        )
        suggested = (result.text or raw_prompt).strip()
    except Exception as e:
        _log.debug("thegent_suggest_prompt sampling unavailable: %s", e)
        suggested = raw_prompt
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"suggested_prompt": suggested, "sampling_used": suggested != raw_prompt}),
        structured_content={"suggested_prompt": suggested, "sampling_used": suggested != raw_prompt},
        meta={"execution_time_ms": elapsed_ms},
    )


# Sitback: dashboard resource, tool, prompts (FastMCP-first projection)
from thegent.mcp_sitback import register_sitback

register_sitback(mcp)

# Add transforms to expose resources and prompts as tools for tool-only clients
mcp.add_transform(ResourcesAsTools(cast("Any", mcp)))
mcp.add_transform(PromptsAsTools(cast("Any", mcp)))


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> Response:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "ok", "server": "thegent"})


def _get_event_store() -> EventStore:
    """EventStore: MemoryStore default, Redis when FASTMCP_EVENT_STORE_URL set."""
    url = os.environ.get("FASTMCP_EVENT_STORE_URL")
    if url:
        from key_value.aio.stores.redis import RedisStore

        return EventStore(storage=RedisStore(url=url))
    return EventStore()


def http_app(stateless_http: bool = True):
    """Return ASGI app with EventStore (mountable in FastAPI/Starlette).
    stateless_http=True allows per-request JSON-RPC without SSE session (for simple clients, CI, verification)."""
    app = mcp.http_app(
        event_store=_get_event_store(),
        retry_interval=2000,
        transport="http",
        stateless_http=stateless_http,
    )
    # Some app objects used in testing may not implement add_middleware; guard to avoid attribute errors
    if hasattr(app, "add_middleware"):
        cast("Any", app).add_middleware(BearerAuthMiddleware)
    return app


def run(host: str | None = None, port: int | None = None) -> None:
    """Start the FastMCP server with EventStore and optional Docket."""
    import uvicorn

    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    os.environ.get("FASTMCP_DOCKET_URL")
    app = http_app(stateless_http=True)
    uvicorn.run(
        app,
        host=host or settings.mcp_host,
        port=port or settings.mcp_port,
        lifespan="on",
    )


if __name__ == "__main__":
    run()
