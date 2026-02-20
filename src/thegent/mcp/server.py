"""FastMCP server for thegent."""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
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

# Auto-initialize IDE integrations on startup
from thegent.ide.auto_init import auto_init_on_startup


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


from thegent.cli.commands.impl import (
    ELICIT_CWD_MSG,
    ELICIT_OWNER_MSG,
    _coerce_issue_types,
    _default_owner_tag,
    _resolve_cwd,
    bg_impl,
    continuity_snapshot_impl,
    dag_list_impl,
    dag_status_impl,
    do_next_impl,  # Now exists
    escalate_add_impl,
    escalate_approve_impl,
    escalate_list_impl,
    escalate_resolve_impl,
    get_server_meta_impl,
    history_impl,
    inbox_list_impl,
    incorporate_impl,
    inspect_impl,
    list_agents_impl,
    list_droids_impl,
    list_models_impl,
    logs_impl,
    # loop_impl,  # TODO: Not implemented
    observe_summary_impl,
    # pause_impl,  # TODO: Not implemented
    plan_analyze_impl,
    ps_impl,
    # resume_impl,  # TODO: Not implemented
    retry_impl,
    run_impl,
    session_contract_audit_impl,
    session_contract_health_gate_impl,
    session_contract_health_report_impl,
    session_contract_health_trend_impl,
    session_contract_negotiate_impl,
    status_impl,
    stop_impl,
    wait_impl,
    wait_next_impl,
    work_stream_claim_impl,
    work_stream_complete_impl,
)
from thegent.output_parser import OUTPUT_PARSER_SCHEMA_VERSION

# G-FM-04: Icon mapping for tools; wire when FastMCP supports icon parameter
# Uses Unicode symbols (not emoji) for consistent terminal rendering
TOOL_ICONS = {
    "thegent_run": "▶",
    "thegent_plan_status": "≡",
    "thegent_plan_get": "▤",
    "thegent_plan_save": "⌃",
    "thegent_plan_approve": "✓",
    "thegent_protocol_list": "≡",
    "thegent_protocol_get": "≡",
    "thegent_discussion_finalize": "◉",
    "thegent_research_finalize": "⊕",
    "thegent_validation_report": "✓",
    "thegent_plan_create": "✎",
    "thegent_team_create": "⊕",
    "thegent_team_list": "≡",
    "thegent_team_delegate": "→",
    "thegent_discussion_start": "◉",
    "thegent_discussion_add_question": "?",
    "thegent_bg": "⏸",
    "thegent_stop": "⏹",
    "thegent_pause": "⏸",
    "thegent_resume": "▶",
    "thegent_continuity_snapshot": "≡",
    "thegent_suggest_mode": "◎",
    "thegent_logs": "▤",
    "thegent_ps": "≡",
    "thegent_status": "ℹ",
    "thegent_wait": "⏳",
    "thegent_inbox_list": "↓",
    "thegent_inbox_wait": "⊞",
    "thegent_inspect": "⌕",
    "thegent_list_agents": "⊕",
    "thegent_list_droids": "◉",
    "thegent_list_models": "⊞",
    "thegent_dag_list": "▣",
    "thegent_dag_ready": "▣",
    "thegent_dag_recover": "↺",
    "thegent_dag_run": "▶",
    "thegent_dag_sync": "↻",
    "thegent_observe_summary": "↑",
    "thegent_config_resolve": "◎",
    "thegent_sitback_dashboard": "⊞",
    "thegent_terminal_list": "⊞",
    "thegent_terminal_inspect": "◉",
    "thegent_terminal_send": "⌨",
    "thegent_terminal_attach": "⎘",
    "thegent_ddg_search": "⌕",
    "thegent_do_next": "→",
    "thegent_plan_get_next": "▤",
    "thegent_plan_progress": "≡",
    "thegent_plan_analyze": "⊕",
    "thegent_plan_wait_next": "⏳",
    "thegent_history": "≡",
    "thegent_retry": "↺",
    "thegent_plan_incorporate": "⌃",
    "thegent_dag_status": "▣",
    "thegent_escalate_list": "↑",
    "thegent_escalate_add": "↑",
    "thegent_escalate_approve": "✓",
    "thegent_escalate_resolve": "✓",
    "thegent_handoff": "↔",
    "thegent_handoff_list": "≡",
    "thegent_handoff_show": "◉",
    "thegent_handoff_confirm": "✓",
    "thegent_queue_list": "≡",
    "thegent_queue_claim": "→",
    "thegent_queue_done": "✓",
    "thegent_queue_add": "⊕",
    "thegent_queue_edit": "✎",
    "thegent_queue_release": "↺",
    "thegent_queue_extend_lease": "⏳",
    "thegent_terminal_route": "⌨",
    "thegent_free": "▶",
    "thegent_flash": "⚡",
    "thegent_elicit_confirmation": "?",
    "thegent_elicit_choice": "◎",
    "thegent_elicit_text": "✎",
    "thegent_storage_get": "▤",
    "thegent_storage_set": "⌃",
    "thegent_events_emit": "↑",
    "thegent_events_replay": "≡",
    "thegent_macos_run_script": "⌘",
}

_log = logging.getLogger(__name__)

# ROB-016: Elicitation timeout (seconds). Fail-safe if client doesn't respond.
ELICIT_TIMEOUT_S = 30

# OPT-018: ElicitationResponse caching with SHA256 of prompt+response
# Cache to avoid re-eliciting identical contexts
from cachetools import TTLCache

_ELICITATION_CACHE: TTLCache[str, Any] = TTLCache(maxsize=100, ttl=300)  # 5 min TTL


def _cache_elicitation_key(prompt: str, response_type: type) -> str:
    """Generate cache key for elicitation request."""
    key_data = f"{prompt}:{response_type.__name__}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def _get_cached_elicitation(prompt: str, response_type: type) -> Any | None:
    """OPT-018: Get cached elicitation response if available."""
    cache_key = _cache_elicitation_key(prompt, response_type)
    return _ELICITATION_CACHE.get(cache_key)


def _cache_elicitation_response(prompt: str, response_type: type, response: Any) -> None:
    """OPT-018: Cache elicitation response."""
    cache_key = _cache_elicitation_key(prompt, response_type)
    _ELICITATION_CACHE[cache_key] = response


# OPT-018: ElicitationResponse caching with SHA256 of prompt+response
# Cache to avoid re-eliciting identical contexts
import hashlib

from cachetools import TTLCache

_ELICITATION_CACHE: TTLCache[str, Any] = TTLCache(maxsize=100, ttl=300)  # 5 min TTL


def _cache_elicitation_key(prompt: str, response_type: type) -> str:
    """Generate cache key for elicitation request."""
    key_data = f"{prompt}:{response_type.__name__}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def _get_cached_elicitation(prompt: str, response_type: type) -> Any | None:
    """OPT-018: Get cached elicitation response if available."""
    cache_key = _cache_elicitation_key(prompt, response_type)
    return _ELICITATION_CACHE.get(cache_key)


def _cache_elicitation_response(prompt: str, response_type: type, response: Any) -> None:
    """OPT-018: Cache elicitation response."""
    cache_key = _cache_elicitation_key(prompt, response_type)
    _ELICITATION_CACHE[cache_key] = response


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
async def thegent_lifespan(mcp_app: FastMCP) -> AsyncIterator[dict[str, Any] | None]:
    """Startup and teardown for thegent MCP server. See gofastmcp.com/servers/lifespan."""
    _log.info("thegent MCP server starting")

    # Initialize runtime infrastructure (resource limits and monitoring)
    try:
        from thegent.infra import initialize_runtime_infrastructure

        initialize_runtime_infrastructure()
        _log.info("Runtime infrastructure initialized")
    except Exception as e:
        _log.warning("Failed to initialize runtime infrastructure: %s", e)

    # ROB-013: Configuration validation on startup (fail-fast)
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    try:
        settings.validate_setup()
        _log.info("Configuration validated successfully")
    except Exception as e:
        _log.critical("Configuration validation failed: %s", e)
        # In mission-critical rigor, we might want to exit here,
        # but for now we'll just log loudly to avoid breaking all installs.

    # Auto-initialize IDE integrations (JetBrains, Serena, Ghostty)
    try:
        auto_init_on_startup()
        _log.info("IDE integrations auto-initialized")
    except Exception as e:
        _log.debug("IDE auto-init failed (non-critical): %s", e)

    # MCP bundle: required mounts (playwright for browser; serena, octocode); flyto-core optional alternative for browser
    mounts_enabled = (
        settings.mcp_mount_flyto
        or settings.mcp_mount_playwright
        or settings.mcp_mount_serena
        or settings.mcp_mount_octocode
        or settings.mcp_mount_sequential_thinking
        or settings.mcp_mount_next_devtools
    )
    if mounts_enabled:
        try:
            from fastmcp.server import create_proxy

            def _js_executor_config(package: str) -> dict[str, Any]:
                """Utility to generate consistent JS executor proxy config.
                Prefers 'bun x' (Bun) for speed, falls back to 'npx' (Node).
                Uses --no-install if possible to reduce process sprawl."""
                import shutil

                bun = shutil.which("bun")
                if bun:
                    return {
                        "mcpServers": {"default": {"command": "bun", "args": ["x", package], "env": {**os.environ}}}
                    }
                return {
                    "mcpServers": {
                        "default": {
                            "command": "npx",
                            "args": ["-y", "--no-install", package],
                            "env": {**os.environ, "npm_config_update_notifier": "false"},
                        }
                    }
                }

            if settings.mcp_mount_flyto:
                # flyto-core HTTP at 8333 (run: flyto serve) or THGENT_FLYTO_URL
                flyto_url = settings.flyto_url
                proxy = create_proxy(flyto_url, name="flyto")
                mcp_app.mount(proxy, namespace="browser")
                _log.info("mounted flyto-core at namespace browser (url=%s)", flyto_url)
            elif settings.mcp_mount_playwright:
                playwright_config = _js_executor_config("@playwright/mcp@latest")
                proxy = create_proxy(playwright_config, name="playwright")
                mcp_app.mount(proxy, namespace="browser")
                _log.info("mounted @playwright/mcp at namespace browser")

            if settings.mcp_mount_serena:
                # Use Serena integration to detect backend (LSP or JetBrains plugin)
                from thegent.lsp.serena_integration import detect_serena_backend, get_serena_mcp_config

                backend = detect_serena_backend()
                serena_config = get_serena_mcp_config()

                if backend == "jetbrains":
                    # JetBrains plugin: may need different proxy setup
                    # For now, use same proxy pattern (may need HTTP client instead)
                    _log.info(f"Using Serena JetBrains plugin backend (port {settings.serena_jetbrains_port})")
                    # Note: JetBrains plugin may expose HTTP MCP server, not stdio
                    # This is a placeholder - actual implementation depends on plugin API
                    serena_config = {
                        "command": "uvx",
                        "args": [
                            "--from",
                            "git+https://github.com/oraios/serena",
                            "serena",
                            "start-mcp-server",
                            "--transport",
                            "sse",
                            "--port",
                            "3848",
                            "--context",
                            "ide",
                            "--project-from-cwd",
                            "--open-web-dashboard",
                            "false",
                        ],
                        "env": {},
                    }
                else:
                    # LSP backend: existing configuration
                    _log.info("Using Serena LSP backend")
                    serena_config = {
                        "command": "uvx",
                        "args": [
                            "--from",
                            "git+https://github.com/oraios/serena",
                            "serena",
                            "start-mcp-server",
                            "--transport",
                            "sse",
                            "--port",
                            "3848",
                            "--context",
                            "ide",
                            "--project-from-cwd",
                            "--open-web-dashboard",
                            "false",
                        ],
                        "env": {},
                    }

                proxy = create_proxy(serena_config, name="serena")
                mcp_app.mount(proxy, namespace="serena")
                _log.info(f"mounted Serena at namespace serena (backend: {backend})")

            if settings.mcp_mount_octocode:
                proxy = create_proxy(_js_executor_config("octocode-mcp@latest"), name="octocode")
                mcp_app.mount(proxy, namespace="octocode")
                _log.info("mounted Octocode at namespace octocode")

            if settings.mcp_mount_sequential_thinking:
                proxy = create_proxy(
                    _js_executor_config("@modelcontextprotocol/server-sequential-thinking"), name="thinking"
                )
                mcp_app.mount(proxy, namespace="thinking")
                _log.info("mounted Sequential Thinking at namespace thinking")

            if settings.mcp_mount_next_devtools:
                proxy = create_proxy(_js_executor_config("@next/devtools-mcp"), name="next")
                mcp_app.mount(proxy, namespace="next")
                _log.info("mounted Next DevTools at namespace next")
        except Exception as e:
            _log.warning("failed to mount provider: %s", e)

    # OPT-021: Parallel Dependency Resolution (warming catalog/routes)
    # Disabled: prewarm_catalog/prewarm_git_index functions don't exist yet (GH-4172)
    try:
        # from thegent.models.catalog import prewarm_catalog
        # from thegent.tools.terminal import prewarm_git_index
        # # Run in thread to avoid blocking lifespan event loop
        # task1 = asyncio.create_task(asyncio.to_thread(prewarm_catalog))
        # task2 = asyncio.create_task(asyncio.to_thread(prewarm_git_index))
        # # Keep references to avoid task cancellation
        # _background_tasks = (task1, task2)
        pass
    except Exception as e:
        _log.warning("failed to pre-warm dependencies: %s", e)

    proxy_proc = None
    if settings.bundle_proxy:
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
                    rows = await asyncio.to_thread(ps_impl, None, True, None)
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


def _stable_json(payload: Any) -> str:
    """Serialize dict/list payloads with stable key order for deterministic MCP transport."""
    return json.dumps(payload, sort_keys=True)


def _error_result(
    error: str,
    remediation: str,
    exit_code: int = 1,
    extra: dict[str, Any] | None = None,
) -> ToolResult:
    """Return ToolResult with error, remediation, and structured_content (MCP-OPT §5)."""
    payload: dict[str, Any] = {"error": error, "remediation": remediation, "exit_code": exit_code}
    if extra:
        payload.update(extra)
    return ToolResult(
        content=json.dumps(payload),
        structured_content=payload,
        meta={"execution_time_ms": 0},
    )


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
    return logs_impl(session_id=id, tail=tail, stderr=stderr) or ""


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
    "thegent://workstream",
    mime_type="text/markdown",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workstream() -> str:
    """Get the canonical WORK_STREAM.md content."""
    from thegent.utils import get_resource_path
    from thegent.utils.helpers import read_file_optimized

    work_stream_path = get_resource_path("docs/reference/WORK_STREAM.md")
    if not work_stream_path.exists():
        return "WORK_STREAM.md not found. Run 'thegent plan incorporate' to seed it."
    # Work stream can be large; optimize read
    return read_file_optimized(work_stream_path, max_size_mb=2) or "Error reading work stream."


@mcp.resource(
    "thegent://events/session-complete",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_events_session_complete() -> str:
    """Event stream for session completion events (for auto-launch system)."""
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    try:
        db = WorkstreamDB(settings=ThegentSettings())
        # Get recent completion events
        events = db.execute_query(
            """
            SELECT session_id, exit_code, completed_at, workstream_item_id
            FROM sessions
            WHERE status = 'exited' AND completed_at IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT 50
            """
        )
        return json.dumps({"events": events, "count": len(events)})
    except Exception as e:
        return json.dumps({"error": str(e), "events": []})


@mcp.resource(
    "thegent://workstream/db",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workstream_db() -> str:
    """Workstream database metadata and schema info."""
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
        return json.dumps({"error": str(e)})


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


@mcp.resource(
    "thegent://workflow/triggers",
    mime_type="text/markdown",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workflow_triggers() -> str:
    """Workflow instructions: idea→research→spec, quality green, next item. Injected on UserPromptSubmit."""
    return """# Workflow Triggers

## Idea/Task Prompts
When user gives idea/task prompts (research, explore, build, implement, design, create, feature, investigate):
1. Dump research to docs/research/ (or docs/guides/)
2. Create or update specs in docs/docset/
3. Add work items to unified work stream (docs/reference/, contracts/, docs/plans/)
4. Enables: spam ideas → open new chat → ask "find the next thing to do"

## Quality Green
When user says "get task quality green", "quality green", "make quality pass", "fix quality":
- Run: task quality-a-r (full pipeline; on fail pipes to agent until green)
- Or: task quality:dag (DAG only)

## Next Item
When user says "find the next thing to do", "what next", "pick next", "next task":
1. Read from docs/reference/, docs/docset/, contracts/, docs/plans/
2. Check PLAN_STATUS.md, FR_TRACKER.md, or project tracker
3. Pick highest-priority in-progress or pending item
4. Execute that item

## Gardening (Converge to Empty Backlog + Green)
When user says "garden", "converge", "empty backlog", "complete green", "check gov traceability":
1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: thegent_run/thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""


@mcp.prompt
def thegent_workflow_idea(idea: str) -> str:
    """
    Instructions for idea/task prompts: dump research, create specs, add work items.
    Use when user gives research/explore/build/implement/design/create/feature prompts.
    """
    return f"""Idea/task: {idea}

Workflow:
1. Dump research to docs/research/ (or docs/guides/)
2. Create or update specs in docs/docset/
3. Add work items to unified work stream (docs/reference/, contracts/, docs/plans/)
4. This enables: spam ideas here → open new chat → ask "find the next thing to do"
"""


@mcp.prompt
def thegent_workflow_quality_green() -> str:
    """
    Instructions to run full quality pipeline until green.
    Use when user says "get task quality green", "quality green", "make quality pass".
    """
    return """Run: task quality-a-r
(Full quality pipeline; on fail pipes to agent and reloads until green)
Or: task quality:dag (DAG only, no agent loop)
"""


@mcp.prompt
def thegent_workflow_next_item() -> str:
    """
    Instructions to find and execute the next work item from the unified stream.
    Use when user says "find the next thing to do", "what next", "pick next".
    """
    return """1. Read from unified work stream: docs/reference/, docs/docset/, contracts/, docs/plans/
2. Check docs/reference/PLAN_STATUS.md, docs/reference/FR_TRACKER.md, or project tracker
3. Pick the highest-priority in-progress or pending item
4. Execute that item
"""


@mcp.resource(
    "thegent://workflow/gardening",
    mime_type="text/markdown",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workflow_gardening() -> str:
    """Gardening workflow: converge to empty backlog and complete green."""
    return """# Gardening Workflow (Converge to Empty Backlog + Green)

1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: thegent_run/thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""


@mcp.prompt
def thegent_workflow_gardening() -> str:
    """
    Instructions for gardening: check gov traceability, tests, plan items; dispatch; converge to empty backlog and complete green.
    Use when user says "garden", "converge", "empty backlog", "complete green".
    """
    return """Gardening workflow — converge to empty backlog + complete green:

1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: thegent_run/thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""


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
async def thegent_session_list(
    all: bool = False,
    owner: str | None = None,
    agent: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> str:
    """
    List agent sessions from the registry (WP-9006).

    Args:
        all: Show sessions for all owners (admin)
        owner: Filter by owner tag
        agent: Filter by agent name
        status: Filter by status (running, completed, failed)
        limit: Max sessions to return
    """
    from thegent.cli.commands.impl import ps_impl

    sessions = ps_impl(all=all, owner=owner, agent=agent, status=status, limit=limit)
    return json.dumps(sessions, indent=2)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_session_show(
    session_id: str,
) -> str:
    """
    Get detailed metadata for a session (WP-9006).

    Args:
        session_id: The ID of the session
    """
    from thegent.cli.commands.impl import ps_impl

    sessions = ps_impl(all=True)
    session = next(
        (s for s in sessions if s.get("run_id") == session_id or s.get("correlation_id") == session_id), None
    )
    if not session:
        return json.dumps({"error": f"Session {session_id} not found"}, indent=2)

    return json.dumps(session, indent=2)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_session_logs(
    session_id: str,
    stderr: bool = False,
    tail: int = 100,
) -> str:
    """
    Read session logs (stdout/stderr) (WP-9006).

    Args:
        session_id: The ID of the session
        stderr: Read stderr instead of stdout
        tail: Number of lines to return from the end
    """
    from thegent.cli.commands.impl import logs_impl

    res = logs_impl(session_id=session_id, stderr=stderr, follow=False, tail=tail)
    if res is None:
        return ""
    return res


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_session_send(
    session_id: str,
    message: str,
    msg_type: str = "reprompt",
) -> str:
    """
    Send a message/reprompt to a running session (WP-9004).

    Args:
        session_id: The ID of the session
        message: The message text to send
        msg_type: reprompt, command, system
    """
    from thegent.cli.commands.impl import session_send_impl

    ok, msg = session_send_impl(session_id, message, msg_type=msg_type)
    return json.dumps({"success": ok, "message": msg}, indent=2)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_session_attach_hint(
    session_id: str,
) -> str:
    """
    Return the command to attach to a session (WP-9007).

    Args:
        session_id: The ID of the session
    """
    from thegent.cli.commands.impl import ps_impl

    sessions = ps_impl(all=True)
    session = next(
        (s for s in sessions if s.get("run_id") == session_id or s.get("correlation_id") == session_id), None
    )
    if not session:
        return json.dumps({"error": f"Session {session_id} not found"}, indent=2)

    interactivity = session.get("interactivity")
    attach_target = session.get("attach_target") or {}

    if interactivity == "tmux" or attach_target.get("tmux_pane"):
        pane = attach_target.get("tmux_pane") or session_id
        return json.dumps(
            {
                "mode": "tmux",
                "command": f"thegent session attach {session_id}",
                "raw_command": f"tmux attach-session -t {pane}",
                "hint": "Attach via tmux",
            },
            indent=2,
        )

    if interactivity == "headless-holdpty":
        return json.dumps(
            {
                "mode": "holdpty",
                "command": f"thegent session attach {session_id}",
                "hint": "Attach via holdpty wrapper",
            },
            indent=2,
        )

    return json.dumps(
        {
            "mode": "none",
            "hint": "Session does not support interactive attachment. Use 'thegent session logs --follow' instead.",
        },
        indent=2,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_config_resolve(
    tenant_id: str | None = None,
    session_id: str | None = None,
    overrides: dict[str, Any] | None = None,
    keys: list[str] | None = None,
) -> str:
    """
    Resolve configuration for a given tenant or session (WP-10001).
    Returns a JSON string of the resolved configuration values.

    Args:
        tenant_id: Optional ID of the tenant.
        session_id: Optional ID of the session.
        overrides: Optional key-value pairs to override the resolved config.
        keys: Optional list of keys to include in the output (returns all if omitted).
    """
    from thegent.config_provider import get_config_provider

    provider = get_config_provider()
    config = provider.resolve(tenant_id=tenant_id, session_id=session_id, request_overrides=overrides, keys=keys)

    # Sanitize for JSON (Path -> str)
    def _sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize(i) for i in obj]
        if hasattr(obj, "__str__") and not isinstance(obj, (int, float, bool, str, type(None))):
            return str(obj)
        return obj

    return json.dumps(_sanitize(config), indent=2)


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
    task=TaskConfig(mode="required", poll_interval=timedelta(seconds=5)),
)
async def thegent_run(
    prompt: str | None = None,
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
    async_task: bool = False,
    ctx: Any = CurrentContext(),
    default_cwd: Any = Depends(get_default_cwd),
) -> ToolResult | str:
    """
    Execute a task using a specified agent or model.
    This tool is synchronous (blocks until completion) by default.
    Use for critical path operations that require immediate feedback.

    Args:
        prompt: Detailed instruction for the agent. (Semantic hint: include 'task context')
        agent: Canonical agent name (e.g. 'free', 'zen'). Omit if using model-first routing.
        model: Specific model ID (e.g. 'gemini-3-flash'). Triggers auto-routing if agent is omitted.
        provider: Provider hint for model-first routing (e.g. 'codex', 'openai').
        cd: Working directory. (Semantic hint: absolute path preferred).
        mode: Operation mode: 'read-only' (safe), 'write' (normal), 'full' (destructive/sudo).
        timeout: Execution timeout in seconds (min: 5, max: 3600).
        full: Return verbose output including logs and trace metadata.
        include_contract: Include resolved routing metadata for verification.
        confidence: Minimum required model confidence score (0.0-1.0).
        arbitration: Peer-review role: 'planner', 'operator', 'reviewer', 'consenter'.
        async_task: Return task_id immediately and execute in background. Use thegent_status to track.

    Returns:
        JSON result containing 'stdout', 'stderr', and 'exit_code'.
        Zero exit_code implies success. Non-zero implies actionable failure.
    """
    # UX-AX: Elicit missing prompt instead of failing
    if not prompt:
        try:
            elicitation = await asyncio.wait_for(
                ctx.elicit("What task should I perform?", response_type=str),
                timeout=ELICIT_TIMEOUT_S,
            )
            if isinstance(elicitation, AcceptedElicitation):
                prompt = cast("str", elicitation.data)
            else:
                return _error_result("Prompt is required to run a task.", "Provide 'prompt' in tool call.")
        except TimeoutError:
            return _error_result("Elicitation timed out (no prompt provided).", "Provide 'prompt' in tool call.")

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
            return _error_result(
                f"No route for model '{model}'.",
                "Run: thegent list-models",
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
            return _error_result(
                f"Model '{model}' not available via provider '{agent}'.{suffix}",
                "Run: thegent list-models" if not available else f"Available: {available}. Or: thegent list-models",
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
        return _error_result("Provide agent or model for routing.", "Run: thegent list-agents")

    await ctx.info(f"thegent_run agent={agent} cd={cd} timeout={timeout}")
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cd_path)
    if cwd is None:
        # OPT-018: Check cache first to avoid re-eliciting identical contexts
        cached_response = _get_cached_elicitation(ELICIT_CWD_MSG, str)
        if cached_response is not None:
            if isinstance(cached_response, AcceptedElicitation):
                cwd = Path(cached_response.data).expanduser().resolve()
            elif isinstance(cached_response, DeclinedElicitation):
                return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
            elif isinstance(cached_response, CancelledElicitation):
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
        else:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit(ELICIT_CWD_MSG, response_type=str),
                    timeout=ELICIT_TIMEOUT_S,
                )
                # OPT-018: Cache the response
                _cache_elicitation_response(ELICIT_CWD_MSG, str, elicitation)
                if isinstance(elicitation, AcceptedElicitation):
                    cwd = Path(elicitation.data).expanduser().resolve()
                elif isinstance(elicitation, DeclinedElicitation):
                    return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                elif isinstance(elicitation, CancelledElicitation):
                    return _error_result("Elicitation cancelled.", "Retry with explicit params")
                else:
                    return _error_result("Ambiguous cwd.", "Provide cd=/path explicitly")
            except TimeoutError:
                return _error_result(
                    "Elicitation timed out (no response from client).",
                    "Provide cd=/path in tool call",
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
    # async_task=True: register in task registry and return task_id immediately
    if async_task:
        from thegent.mcp.task_registry import get_task_registry as _gtr

        tid = _gtr().create(task)
        payload = {"task_id": tid, "status": "running"}
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": 0},
        )
    last_reported = 0
    last_close_at = 0
    while not task.done():
        elapsed = int(time.perf_counter() - start_time)
        if elapsed - last_reported >= 10:
            await ctx.report_progress(progress=elapsed, total=timeout)
            last_reported = elapsed
        # Close SSE stream every 30s during long runs to avoid LB timeouts (SSE polling)
        if elapsed - last_close_at >= 30 and elapsed > 0:
            await ctx.close_sse_stream()
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
async def thegent_loop(
    prompt: str,
    todo_spec: str,
    agent: str | None = None,
    checker: str = "antigravity",
    mode: str = "soft",
    cd: str | None = None,
    ctx: Any = CurrentContext(),
    default_cwd: Any = Depends(get_default_cwd),
) -> ToolResult:
    """
    Run a Lifecycle loop with Checker oversight.
    """
    await ctx.info(f"thegent_loop agent={agent} mode={mode}")
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cd_path)
    if cwd is None:
        return _error_result("CWD not found.", "Provide cd=/path or run from project root")

    start_time = time.perf_counter()

    # loop_impl is not yet implemented in cli_impl; use bg_impl to launch the loop agent
    async def _run():
        return await asyncio.to_thread(
            bg_impl,
            agent=agent or "cursor",
            prompt=f"[LOOP mode={mode} checker={checker}] {prompt}\n\nTODO: {todo_spec}",
            cd=cwd,
            mode="write",
            timeout=0,
        )

    task = asyncio.create_task(_run())
    while not task.done():
        await asyncio.sleep(1)
        await ctx.report_progress(progress=0, total=100)  # Progress unknown

    result = await task
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_loop_takeover(
    session_id: str,
    prompt: str,
) -> str:
    """
    Inject human input into a running loop for takeover.
    """
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    session_dir = settings.session_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    takeover_file = session_dir / "takeover.json"
    takeover_file.write_text(json.dumps({"prompt": prompt}))
    return f"Takeover input injected for session {session_id}"


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_loop_stop(
    session_id: str,
) -> str:
    """
    Send a STOP signal to a running loop.
    """
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    session_dir = settings.session_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    stop_file = session_dir / "STOP"
    stop_file.write_text("STOP")
    return f"Stop signal sent to session {session_id}"


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_bg(
    prompt: str | None = None,
    agent: str | None = None,
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
    Fire-and-forget background task execution (asynchronous).
    Returns a session_id immediately. Use this for non-blocking long-running jobs.

    Args:
        prompt: Task instruction. (Semantic hint: 'process in background')
        agent: Canonical agent name.
        cd: Working directory.
        mode: Operation mode: 'read-only', 'write', 'full'.
        timeout: Execution timeout in seconds.
        owner: Optional owner tag for grouping/discovery.
        model: Specific model ID (auto-route if agent is omitted).
        provider: Provider hint for model-first routing.
        routing: Routing policy: 'prefer_direct', 'prefer_proxy', 'failover'.
        failover: Enable automatic failover on routing failure.
        include_contract: Include routing contract in the result.
        confidence: Minimum confidence threshold.
        arbitration: Peer-review role.

    Returns:
        JSON result with 'session_id', 'status', and 'log_path'.
        Success is implied if session_id is returned.
    """
    # UX-AX: Elicit missing prompt
    if not prompt:
        try:
            elicitation = await asyncio.wait_for(
                ctx.elicit("What background task should I perform?", response_type=str),
                timeout=ELICIT_TIMEOUT_S,
            )
            if isinstance(elicitation, AcceptedElicitation):
                prompt = cast("str", elicitation.data)
            else:
                return _error_result("Prompt is required for background task.", "Provide 'prompt' in tool call.")
        except TimeoutError:
            return _error_result("Elicitation timed out (no prompt provided).", "Provide 'prompt' in tool call.")

    await ctx.info(f"thegent_bg agent={agent} cd={cd} owner={owner}")
    cd_path = Path(cd) if cd else default_cwd
    cwd = _resolve_cwd(cast("Path | None", cd_path))
    elicited_cwd = False
    if cwd is None:
        # OPT-018: Check cache first to avoid re-eliciting identical contexts
        cached_response = _get_cached_elicitation(ELICIT_CWD_MSG, str)
        if cached_response is not None:
            if isinstance(cached_response, AcceptedElicitation):
                cwd = Path(cast("str", cached_response.data)).expanduser().resolve()
                elicited_cwd = True
            elif isinstance(cached_response, DeclinedElicitation):
                return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
            elif isinstance(cached_response, CancelledElicitation):
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
        else:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit(ELICIT_CWD_MSG, response_type=str),
                    timeout=ELICIT_TIMEOUT_S,
                )
                # OPT-018: Cache the response
                _cache_elicitation_response(ELICIT_CWD_MSG, str, elicitation)
                if isinstance(elicitation, AcceptedElicitation):
                    cwd = Path(cast("str", elicitation.data)).expanduser().resolve()
                    elicited_cwd = True
                elif isinstance(elicitation, DeclinedElicitation):
                    return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                elif isinstance(elicitation, CancelledElicitation):
                    return _error_result("Elicitation cancelled.", "Retry with explicit params")
                else:
                    return _error_result("Ambiguous cwd.", "Provide cd=/path explicitly")
            except TimeoutError:
                return _error_result(
                    "Elicitation timed out (no response from client).",
                    "Provide cd=/path in tool call",
                )
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
        try:
            elicitation = await asyncio.wait_for(
                ctx.elicit(ELICIT_OWNER_MSG, response_type=str),
                timeout=ELICIT_TIMEOUT_S,
            )
        except TimeoutError:
            owner_tag = _default_owner_tag(cwd)
        else:
            if isinstance(elicitation, AcceptedElicitation):
                owner_tag = cast("str", elicitation.data)
            elif isinstance(elicitation, DeclinedElicitation):
                owner_tag = _default_owner_tag(cwd)
            elif isinstance(elicitation, CancelledElicitation):
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
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
    List active and historical background sessions for monitoring and discovery.
    Use this to find session_ids for thegent_logs, thegent_status, etc.

    Args:
        owner: Filter by owner tag (e.g. 'kooshapari').
        all: If true, include completed and stopped sessions (default: only running).
        include_contract: Include detailed routing contract and request metadata.

    Returns:
        JSON result containing a 'sessions' list.
    """
    start_time = time.perf_counter()
    result = ps_impl(owner=owner, all=all, include_contract=include_contract)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content={"sessions": result},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_status(session_id: str, include_contract: bool = False) -> ToolResult:
    """
    Get session status for quick health check.

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
    Read session log output with optional tail limit.

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
        structured_content={"logs": result, "session_id": session_id, "tail": tail, "stderr": stderr},
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
    Multi-session status + logs.

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
    # structured_content must be dict or None; inspect_impl returns list
    structured = {"sessions": result} if isinstance(result, list) else result
    return ToolResult(
        content=json.dumps(result),
        structured_content=structured,
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
    Block until session completes or timeout.

    Auto-times out every 2 minutes to prevent Cursor timeout (4min guard).
    Returns instruction to retry without terminating chat.

    Args:
        session_id: Session ID to wait for
        timeout: Timeout in seconds (optional)

    Returns: ToolResult with final status and exit code, or retry instruction if auto-timeout
    """
    _log.info("thegent_wait session_id=%s timeout=%s", session_id, timeout)
    start_time = time.perf_counter()
    result = wait_impl(session_id=session_id, timeout=timeout)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    # Handle auto-timeout case - return retry instruction with emphasis
    if result.get("auto_timeout"):
        message = (
            f"⏱️ **Auto-timeout after {int(result.get('elapsed_seconds', 0))}s** to prevent Cursor timeout.\n\n"
            f"Session '{session_id}' is **still running**.\n\n"
            f"**⚠️ CRITICAL: DO NOT TERMINATE THIS CHAT**\n\n"
            f"**Action Required**: Call `thegent_wait(session_id='{session_id}', timeout={timeout})` again "
            f"to continue waiting. The session continues running in the background.\n\n"
            f"This is a safety mechanism to prevent the 4-minute Cursor guard timeout. "
            f"Simply retry the wait command - do not start a new chat or terminate this conversation."
        )
        return ToolResult(
            content=message,
            structured_content={
                "session_id": session_id,
                "auto_timeout": True,
                "elapsed_seconds": result.get("elapsed_seconds", 0),
                "retry_instruction": result.get("retry_instruction", ""),
                "action": "retry",
                "message": message,
                "note": "DO NOT TERMINATE CHAT - Session continues running, just retry the wait command",
            },
            meta={"execution_time_ms": elapsed_ms, "auto_timeout": True, "action": "retry"},
        )

    return ToolResult(content=json.dumps(result), structured_content=result, meta={"execution_time_ms": elapsed_ms})


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_inbox_list(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    limit: int = 50,
) -> ToolResult:
    """
    List unified inbox events (run registry + escalation) with optional filters.

    Args:
        owner: Filter by owner
        agent: Filter by agent
        event_type: start|finish|feedback|pause|resume|escalation
        status: running|completed|failed
        sources: Comma-separated: registry,escalation (default: registry,escalation)
        limit: Max events to return (default: 50)

    Returns: List of inbox events
    """
    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    start_time = time.perf_counter()
    events = inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=src_tuple,
        limit=limit,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    payload = {"events": events}
    return ToolResult(
        content=json.dumps(payload),
        structured_content=payload,
        meta={"count": len(events), "execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
def thegent_inbox_wait(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: str | None = None,
    poll_interval: float = 2.0,
    timeout: float = 60.0,
) -> ToolResult:
    """
    Wait for next inbox event matching filters. Blocks until new event or timeout.

    Auto-times out every 2 minutes to prevent Cursor timeout (4min guard).
    Returns instruction to retry without terminating chat.

    Args:
        owner: Filter by owner
        agent: Filter by agent
        event_type: start|finish|feedback|pause|resume|escalation
        status: running|completed|failed
        sources: Comma-separated: registry,escalation (default: registry,escalation)
        poll_interval: Poll interval in seconds (default: 2.0)
        timeout: Max wait seconds (default: 60, 0=unbounded)

    Returns: New events that arrived, or empty list on timeout, or retry instruction if auto-timeout
    """
    _log.info(
        "thegent_inbox_wait owner=%s agent=%s event_type=%s poll=%.1f timeout=%.1f",
        owner,
        agent,
        event_type,
        poll_interval,
        timeout,
    )
    src_tuple = tuple(s.strip() for s in (sources or "registry,escalation").split(",") if s.strip())
    start_time = time.perf_counter()
    # inbox_wait_impl only supports timeout; implement filtered polling inline
    auto_timeout_secs = 110.0  # Just under 2min to avoid Cursor 4min guard
    effective_timeout = min(timeout, auto_timeout_secs) if timeout > 0 else auto_timeout_secs
    seen_ids: set[str] = set()
    result: dict | list = []
    # Seed seen_ids with current events so we only return NEW events
    initial = inbox_list_impl(owner=owner, agent=agent, event_type=event_type, status=status, sources=src_tuple)
    for ev in initial:
        seen_ids.add(ev.get("run_id", "") + str(ev.get("timestamp", "")))
    while True:
        elapsed = time.perf_counter() - start_time
        if effective_timeout > 0 and elapsed >= effective_timeout:
            auto_timed_out = timeout <= 0 or elapsed < timeout
            result = {"auto_timeout": auto_timed_out, "elapsed_seconds": int(elapsed), "retry_instruction": "retry"}
            break
        current = inbox_list_impl(owner=owner, agent=agent, event_type=event_type, status=status, sources=src_tuple)
        new_events = [ev for ev in current if ev.get("run_id", "") + str(ev.get("timestamp", "")) not in seen_ids]
        if new_events:
            result = new_events
            break
        time.sleep(poll_interval)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    # Handle auto-timeout case
    if isinstance(result, dict) and result.get("auto_timeout"):
        message = (
            f"⏱️ **Auto-timeout after {int(result.get('elapsed_seconds', 0))}s** to prevent Cursor timeout.\n\n"
            f"Still waiting for inbox events matching filters.\n\n"
            f"**⚠️ CRITICAL: DO NOT TERMINATE THIS CHAT**\n\n"
            f"**Action Required**: Call `thegent_inbox_wait(owner={owner}, agent={agent}, event_type={event_type}, "
            f"status={status}, sources={sources}, poll_interval={poll_interval}, timeout={timeout})` again "
            f"to continue waiting.\n\n"
            f"This is a safety mechanism to prevent the 4-minute Cursor guard timeout. "
            f"Simply retry the wait command - do not start a new chat or terminate this conversation."
        )
        return ToolResult(
            content=message,
            structured_content={
                "events": [],
                "auto_timeout": True,
                "elapsed_seconds": result.get("elapsed_seconds", 0),
                "retry_instruction": result.get("retry_instruction", ""),
                "action": "retry",
                "message": message,
                "note": "DO NOT TERMINATE CHAT - Continue waiting, just retry the wait command",
            },
            meta={"count": 0, "execution_time_ms": elapsed_ms, "auto_timeout": True, "action": "retry"},
        )

    # Normal result (list of events)
    events = result if isinstance(result, list) else []
    payload = {"events": events}
    return ToolResult(
        content=json.dumps(payload),
        structured_content=payload,
        meta={"count": len(events), "execution_time_ms": elapsed_ms},
    )


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
def thegent_config_resolve(
    tenant_id: str | None = None,
    session_id: str | None = None,
    request_overrides: dict[str, Any] | None = None,
    keys: list[str] | None = None,
) -> ToolResult:
    """
    WP-1010: Resolve configuration for a given tenant/session context from the control plane.
    Falls back to environment settings if control plane is unavailable.

    Args:
        tenant_id: Optional tenant ID for context-aware config
        session_id: Optional session ID
        request_overrides: Optional dict of keys to override
        keys: Optional list of specific keys to resolve (resolves all if missing)

    Returns: JSON dict of resolved configuration
    """
    from thegent.config_provider import get_config_provider

    start_time = time.perf_counter()
    p = get_config_provider()
    resolved = p.resolve(
        tenant_id=tenant_id,
        session_id=session_id,
        request_overrides=request_overrides,
        keys=keys,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(resolved, indent=2),
        structured_content=resolved,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_pause(session_id: str, reason: str = "Manual pause") -> ToolResult:
    """
    WP-1009: Pause a background session (register pause event in registry).

    Args:
        session_id: Session ID to pause
        reason: Reason for pause (default: Manual pause)

    Returns: ToolResult with status
    """
    _log.info("thegent_pause session_id=%s", session_id)
    from thegent.execution import RunRegistry

    start_time = time.perf_counter()
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    registry.register_pause(run_id=session_id, reason=reason)
    result = {"success": True, "session_id": session_id, "status": "paused", "reason": reason}
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_resume(session_id: str) -> ToolResult:
    """
    WP-1009: Resume a paused session (register resume event in registry).

    Args:
        session_id: Session ID to resume

    Returns: ToolResult with status
    """
    _log.info("thegent_resume session_id=%s", session_id)
    from thegent.execution import RunRegistry

    start_time = time.perf_counter()
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    registry.register_resume(run_id=session_id)
    result = {"success": True, "session_id": session_id, "status": "running"}
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_continuity_snapshot(
    owner: str,
    run_ids: list[str],
    state_summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
) -> ToolResult:
    """
    WP-1009: Create a continuity snapshot for shift handoff.

    Args:
        owner: Current owner
        run_ids: Run IDs to include in snapshot
        state_summary: Optional state summary dict
        next_steps: Optional list of next steps

    Returns: ToolResult with snapshot_id
    """
    start_time = time.perf_counter()
    result = continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_operations(operation: str | None = None) -> ToolResult:
    """
    List universal operation taxonomy: orchestrate, govern, recover, observe, plan.

    Args:
        operation: Optional filter (orchestrate | govern | recover | observe | plan)

    Returns: JSON with operations and their commands/mcp_tools.
    """
    from thegent.operations import Operation, get_operations_by_type, list_operations

    start_time = time.perf_counter()
    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            return _error_result(
                f"Unknown operation: {operation}",
                "Valid: orchestrate, govern, recover, observe, plan",
                extra={"operation": operation},
            )
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=_stable_json(data),
        structured_content=data,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_modes(mode: str | None = None) -> ToolResult:
    """
    List multi-agent orchestration modes (G-KD-04).

    Args:
        mode: Optional filter (sequential_delegation | parallel_consensus | review_loop)

    Returns: JSON with modes, phases, use_case, risk_profile, selection_hint.
    """
    from thegent.orchestration_modes import get_mode, list_modes

    start_time = time.perf_counter()
    if mode:
        entry = get_mode(mode)
        if not entry:
            return _error_result(
                f"Unknown mode: {mode}",
                "Valid: sequential_delegation, parallel_consensus, review_loop",
                extra={"mode": mode},
            )
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
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=_stable_json(data),
        structured_content=data if isinstance(data, dict) else {"modes": data},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_suggest_mode(
    risk: str = "medium",
    urgency: str = "normal",
    confidence: float = 0.8,
) -> ToolResult:
    """
    WP-Y1: Suggest multi-agent mode based on risk, urgency, confidence (FR-032).

    Args:
        risk: risk_profile (low | medium | high)
        urgency: urgency tier (normal | high | critical)
        confidence: confidence score 0.0-1.0

    Returns: JSON with mode, reason, phases, and selection inputs.
    """
    from thegent.orchestration_modes import get_mode, suggest_mode

    start_time = time.perf_counter()
    mode_value = suggest_mode(risk=risk, urgency=urgency, confidence=confidence)
    entry = get_mode(str(mode_value))
    result: dict[str, Any] = {
        "mode": str(mode_value),
        "inputs": {"risk": risk, "urgency": urgency, "confidence": confidence},
    }
    if entry:
        result["description"] = entry.description
        result["phases"] = entry.phases
        result["use_case"] = entry.use_case
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_agents() -> ToolResult:
    """
    List available canonical agents for task execution.
    Use this to find agent names for the 'agent' parameter in thegent_run or thegent_bg.
    (Semantic hint: agents are specialized workers like 'free', 'zen', 'summarizer').

    Returns:
        JSON result with an 'agents' list containing agent names and backends.
    """
    start_time = time.perf_counter()
    result = list_agents_impl()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content={"agents": result},
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
    List available AI models and their provider mappings.
    Use for model-first routing where you specify a 'model' instead of an 'agent'.

    Args:
        provider: Optional filter (e.g. 'openai', 'anthropic', 'codex').
        include_contract: Include low-level routing contract metadata.
        by_model: If true, group results by model ID (e.g. 'gemini-3-flash') for easier routing.

    Returns:
        JSON result with model IDs and associated providers.
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
        return _error_result(
            f"Invalid policy: {policy}",
            "Valid: prefer_direct, prefer_proxy, failover",
            extra={"policy": policy, "valid_policies": ["prefer_direct", "prefer_proxy", "failover"]},
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
        payload["resolved_route"] = cast(
            "Any",
            {
                "provider": route.provider,
                "model_alias": route.model_alias,
                "backend_type": route.backend_type,
                "priority": route.priority,
                "schema_version": route.schema_version,
            },
        )
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
        try:
            elicitation = await asyncio.wait_for(
                ctx.elicit(ELICIT_CWD_MSG, response_type=str),
                timeout=ELICIT_TIMEOUT_S,
            )
        except TimeoutError:
            return _error_result(
                "Elicitation timed out (no response from client).",
                "Provide cd=/path in tool call",
                extra={"frontmatter": {}, "tasks": []},
            )
        if isinstance(elicitation, AcceptedElicitation):
            cwd = Path(cast("str", elicitation.data)).expanduser().resolve()
        elif isinstance(elicitation, DeclinedElicitation):
            return _error_result(
                "User declined to provide working directory.",
                "Provide cd=/path in tool call",
                extra={"frontmatter": {}, "tasks": []},
            )
        elif isinstance(elicitation, CancelledElicitation):
            return _error_result(
                "Elicitation cancelled.", "Retry with explicit params", extra={"frontmatter": {}, "tasks": []}
            )
        else:
            return _error_result(
                "Ambiguous cwd.",
                "Provide cd=/path or run from project root",
                extra={"frontmatter": {}, "tasks": []},
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
def thegent_do_next(cd: str | None = None, limit: int = 5) -> ToolResult:
    """
    Find the next actionable work items from PLAN_STATUS, FR_TRACKER, docs/plans/, escalation queue.

    Use when user says "what next", "find the next thing to do", "pick next task".
    Returns next_items with id, description, source, prompt_suggestion. Use prompt_suggestion with thegent_run or thegent_bg to execute.

    Args:
        cd: Optional working directory (default: cwd)
        limit: Max items to return (min: 1, max: 50, default: 5)
    """
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = do_next_impl(cd=cd_path, limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={
            "count": result.get("count", 0),
            "sources_checked": result.get("sources_checked", []),
            "execution_time_ms": elapsed_ms,
        },
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_terminal_list(all: bool = False) -> ToolResult:
    """
    List active terminal panes (tmux).

    Args:
        all: Show all panes, not just Claude Code (default: False)
    """
    from thegent.skills.terminal import is_claude_code_pane, list_tmux_panes

    start_time = time.perf_counter()
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
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_terminal_inspect(pane_id: str, last_lines: int = 50) -> ToolResult:
    """
    Capture the content of a terminal pane.
    """
    from thegent.skills.terminal import capture_tmux_pane

    start_time = time.perf_counter()
    content = capture_tmux_pane(pane_id, last_lines=last_lines)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=content,
        structured_content={"content": content, "pane_id": pane_id, "last_lines": last_lines},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_send(pane_id: str, text: str, enter: bool = True) -> ToolResult:
    """
    Send text/keys to a terminal pane.
    """
    from thegent.skills.terminal import send_to_tmux_pane

    start_time = time.perf_counter()
    success = send_to_tmux_pane(pane_id, text, enter=enter)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": success}),
        structured_content={"success": success},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_lock_resource(resource: str, ttl: int = 60, cd: str | None = None) -> ToolResult:
    """
    Acquire an exclusive lock on a resource (file or directory).
    Returns a token that MUST be used with thegent_unlock_resource.
    Use for non-worktree multi-tenancy coordination.
    """
    from thegent.cli.commands.impl import _default_owner_tag, lock_resource_impl

    start_time = time.perf_counter()
    agent_id = _default_owner_tag(Path(cd) if cd else None)
    res = lock_resource_impl(resource, agent_id, ttl=ttl, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    if res["success"]:
        return ToolResult(
            content=f"Successfully locked {res['resource']} (token: {res['token']})",
            structured_content=res,
            meta={"execution_time_ms": elapsed_ms},
        )
    return _error_result(res["error"], "Retry later or check for stale locks.", extra={"resource": resource})


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_unlock_resource(resource: str, token: str, cd: str | None = None) -> ToolResult:
    """
    Release an exclusive lock on a resource using the token from thegent_lock_resource.
    """
    from thegent.cli.commands.impl import _default_owner_tag, unlock_resource_impl

    start_time = time.perf_counter()
    agent_id = _default_owner_tag(Path(cd) if cd else None)
    res = unlock_resource_impl(resource, agent_id, token, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return ToolResult(
        content=f"Successfully unlocked {resource}",
        structured_content=res,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_verify_context(files: list[str], cd: str | None = None) -> ToolResult:
    """
    Verify if any of the given files have been modified (OCC check).
    Returns current versions (hashes) of files for stale-state detection.
    """
    from thegent.cli.commands.impl import verify_context_impl

    start_time = time.perf_counter()
    res = verify_context_impl(files, cd=Path(cd) if cd else None)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return ToolResult(
        content=json.dumps(res, indent=2),
        structured_content=res,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_attach(pane_id: str) -> ToolResult:
    """
    Get instructions to attach to a terminal session.
    """
    from thegent.skills.terminal import list_tmux_panes

    start_time = time.perf_counter()
    panes = list_tmux_panes()
    p = next((p for p in panes if p.pane_id == pane_id), None)
    if not p:
        return _error_result("Pane not found.", "Run: thegent terminal_list", extra={"pane_id": pane_id})

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    msg = f"To attach to this session, run: tmux attach-session -t {p.session_name}"
    return ToolResult(
        content=msg,
        structured_content={"session": p.session_name, "command": f"tmux attach-session -t {p.session_name}"},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_workstream_claim(item_id: str, agent_id: str) -> ToolResult:
    """
    Claim an item in the unified work stream.
    """
    start_time = time.perf_counter()
    result = work_stream_claim_impl(item_id, agent_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_workstream_complete(item_id: str, agent_id: str) -> ToolResult:
    """
    Mark an item as complete in the unified work stream.
    """
    start_time = time.perf_counter()
    result = work_stream_complete_impl(item_id, agent_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_workstream_query(query: str) -> ToolResult:
    """
    Execute SQL query on workstream database.

    Returns query results as JSON. Use for exploring session/workstream data.
    Example: "SELECT * FROM sessions WHERE status='running' LIMIT 10"
    """
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

    start_time = time.perf_counter()
    try:
        db = WorkstreamDB(settings=ThegentSettings())
        results = db.execute_query(query)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return ToolResult(
            content=json.dumps(results, indent=2),
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
    from thegent.config import ThegentSettings
    from thegent.planning.workstream_db import WorkstreamDB

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
            content=json.dumps(result, indent=2),
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
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_heliosShield_status() -> ToolResult:
    """
    Get status from thegent.mesh harness.
    """
    from thegent.skills.terminal import heliosShield_status

    start_time = time.perf_counter()
    status = heliosShield_status()
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=status,
        structured_content={"status": status},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_ddg_search(
    query: str,
    num_results: int = 5,
    ctx: Any = CurrentContext(),
) -> ToolResult:
    """
    Search DuckDuckGo for heavy web research.

    Args:
        query: Search query string
        num_results: Max results to return (min: 1, max: 20, default: 5)
    """
    from thegent.skills.research import ddg_search

    await ctx.info(f"thegent_ddg_search query={query!r} num_results={num_results}")
    start_time = time.perf_counter()
    results = ddg_search(query, max_results=num_results)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    results_list = results if isinstance(results, list) else [results]
    result_count = len(results_list)
    await ctx.info(f"thegent_ddg_search returned {result_count} result(s) in {elapsed_ms}ms")
    return ToolResult(
        content=json.dumps(results_list),
        structured_content={"results": results_list, "count": result_count},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_reddit_search(query: str, num_results: int = 5) -> ToolResult:
    """
    Search Reddit for discussions and community insights.
    Uses Reddit API (if configured) or site-specific search.

    Args:
        query: Search query string
        num_results: Max results to return (min: 1, max: 20, default: 5)
    """
    from thegent.skills.research import reddit_search

    settings = ThegentSettings()
    start_time = time.perf_counter()
    results = reddit_search(query, max_results=num_results, settings=settings)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(results),
        structured_content=results,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_scrape_url(
    url: str,
    use_playwright: bool = True,
    ctx: Any = CurrentContext(),
) -> ToolResult:
    """
    Scrape content from a URL using stealth tools (Playwright) to bypass blocks.

    Args:
        url: URL to scrape
        use_playwright: Whether to use Playwright for stealth scraping (default: True)
    """
    from thegent.skills.research import scrape_url

    await ctx.info(f"thegent_scrape_url url={url!r} use_playwright={use_playwright}")
    await ctx.report_progress(progress=0, total=3)
    start_time = time.perf_counter()
    await ctx.report_progress(progress=1, total=3)
    result = await scrape_url(url, use_playwright=use_playwright)
    await ctx.report_progress(progress=2, total=3)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    content_len = len(result.get("content", "")) if isinstance(result, dict) else 0
    await ctx.info(f"thegent_scrape_url done content_len={content_len} elapsed={elapsed_ms}ms")
    await ctx.report_progress(progress=3, total=3)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_deep_research(query: str, depth: int = 1) -> ToolResult:
    """
    Execute the Deep Research Protocol (DRP) for comprehensive investigation.
    Orchestrates multiple sources (DDG, Reddit, GitHub) and identifies links for scraping.

    Args:
        query: Research query string
        depth: Exploration depth (default: 1)
    """
    from thegent.skills.research import deep_research_orchestrator

    settings = ThegentSettings()
    start_time = time.perf_counter()
    results = deep_research_orchestrator(query, depth=depth, settings=settings)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(results),
        structured_content=results,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_deep_research(query: str, subreddits: str | None = None) -> ToolResult:
    """
    Perform deep research using the Deep Research Protocol (DRP).
    Bypasses blocks by using custom headers and direct API calls.

    Args:
        query: Search query string
        subreddits: Comma-separated list of subreddits to prioritize
    """
    from thegent.skills.deep_research import perform_deep_research

    start_time = time.perf_counter()
    sub_list = [s.strip() for s in subreddits.split(",") if s.strip()] if subreddits else None
    results = perform_deep_research(query, subreddits=sub_list)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(results),
        structured_content=results,
        meta={"execution_time_ms": elapsed_ms},
    )


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
        result = await ctx.sample(
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


# --- Plan / CLI parity tools ---


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_plan_get_next(cd: str | None = None) -> ToolResult:
    """
    Get first work item prompt for scripting. Use with thegent_run or thegent_bg.
    Equivalent to: thegent plan get-next
    """
    cd_path = Path(cd) if cd else None
    result = do_next_impl(cd=cd_path, limit=1)
    if "error" in result:
        return _error_result(result["error"], result.get("remediation", ""), extra=result)
    items = result.get("next_items", [])
    if not items:
        return _error_result("No pending items.", "Run thegent plan do-next", extra={"next_items": []})
    item = items[0]
    return ToolResult(
        content=json.dumps(item),
        structured_content=item,
        meta={"execution_time_ms": 0},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
def thegent_plan_wait_next(
    cd: str | None = None,
    poll: float = 2.0,
    timeout: float = 0.0,
    sources: str = "dag,do_next,escalation,inbox",
) -> ToolResult:
    """
    Block until next actionable work exists (DAG ready, do_next, escalation, inbox).
    Equivalent to: thegent plan wait-next
    """
    cd_path = Path(cd) if cd else None
    src_tuple = tuple(s.strip() for s in sources.split(",") if s.strip())
    result = wait_next_impl(cd=cd_path, poll_interval=poll, timeout=timeout, sources=src_tuple)
    if "error" in result:
        return _error_result(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": 0},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_history(limit: int = 50) -> ToolResult:
    """
    List execution history (recent runs). Equivalent to: thegent history --limit N
    """
    start_time = time.perf_counter()
    runs = history_impl(limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(runs),
        structured_content=runs,
        meta={"execution_time_ms": elapsed_ms, "count": len(runs)},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_plan_progress(limit: int = 10) -> ToolResult:
    """
    Show recent runs (work-package progress). Alias for thegent_history with smaller default.
    Equivalent to: thegent plan progress --limit N
    """
    start_time = time.perf_counter()
    runs = history_impl(limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(runs),
        structured_content=runs,
        meta={"execution_time_ms": elapsed_ms, "count": len(runs)},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_plan_analyze(
    cd: str | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
) -> ToolResult:
    """
    Run planning simulation overlays (XD1–XD3): PERT, resource contention, continuity risk.
    Equivalent to: thegent plan analyze
    If no flags set, runs all three overlays.
    """
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = plan_analyze_impl(cd=cd_path, pert=pert, resources=resources, continuity=continuity)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if "error" in result:
        return _error_result(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_retry(
    run_id: str,
    agent_override: str | None = None,
    failover: bool = False,
    cd: str | None = None,
    override_reason: str | None = None,
) -> ToolResult:
    """
    Retry a failed run by run_id. Looks up prompt/agent from registry and re-runs.
    Equivalent to: thegent retry <run_id>
    """
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = retry_impl(
        run_id=run_id,
        agent_override=agent_override,
        failover=failover,
        cd=cd_path,
        override_reason=override_reason,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if "error" in result:
        return _error_result(result["error"], result.get("remediation", ""), extra=result)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_plan_incorporate(cd: str | None = None, dry_run: bool = False) -> ToolResult:
    """
    Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md BACKLOG.
    Equivalent to: thegent plan incorporate
    """
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = incorporate_impl(cd=cd_path, dry_run=dry_run)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_dag_status(cd: str | None = None) -> ToolResult:
    """
    For each DAG task with session_id, return id, status, session_id, session_status.
    Equivalent to: thegent dag status
    """
    cd_path = Path(cd) if cd else None
    start_time = time.perf_counter()
    result = dag_status_impl(cd=cd_path)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(result),
        structured_content=result,
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_escalate_list(past_sla_only: bool = False, limit: int = 50) -> ToolResult:
    """
    List escalation queue items (blocked runs). Equivalent to: thegent govern escalate list
    """
    start_time = time.perf_counter()
    items = escalate_list_impl(past_sla_only=past_sla_only, limit=limit)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps(items),
        structured_content=items,
        meta={"execution_time_ms": elapsed_ms, "count": len(items)},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_escalate_add(
    run_id: str,
    reason: str,
    sla_minutes: int = 30,
    owner: str | None = None,
    agent: str | None = None,
    lane: str = "standard",
    priority: int = 0,
) -> ToolResult:
    """
    Add a blocked run to the escalation queue. Equivalent to: thegent govern escalate add
    """
    start_time = time.perf_counter()
    try:
        escalate_add_impl(
            run_id=run_id,
            reason=reason,
            sla_minutes=sla_minutes,
            owner=owner,
            agent=agent,
            lane=lane,
            priority=priority,
        )
    except Exception as e:
        return _error_result(str(e), "Check run_id exists", extra={})
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": True, "run_id": run_id}),
        structured_content={"success": True, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_escalate_approve(run_id: str) -> ToolResult:
    """
    Approve an escalation (policy override). Equivalent to: thegent govern escalate approve
    """
    start_time = time.perf_counter()
    ok = escalate_approve_impl(run_id=run_id)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": ok, "run_id": run_id}),
        structured_content={"success": ok, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_escalate_resolve(run_id: str, resolution: str = "resolved") -> ToolResult:
    """
    Mark an escalation item as resolved. Equivalent to: thegent govern escalate resolve
    """
    start_time = time.perf_counter()
    ok = escalate_resolve_impl(run_id=run_id, resolution=resolution)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    return ToolResult(
        content=json.dumps({"success": ok, "run_id": run_id}),
        structured_content={"success": ok, "run_id": run_id},
        meta={"execution_time_ms": elapsed_ms},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_handoff(owner: str, cd: str | None = None) -> ToolResult:
    """
    Create a handoff snapshot for shift handoff (WP-4006). Transfers active runs to snapshot.
    Equivalent to: thegent orchestrate handoff <owner>
    """
    from thegent.execution import HandoffManager, RunRegistry

    cwd = _resolve_cwd(Path(cd) if cd else None)
    if cwd is None:
        return _error_result("Ambiguous cwd.", "Provide cd=/path", extra={})
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=50)
    run_ids = [r["run_id"] for r in runs if r.get("status") == "running"]
    escalation_items = escalate_list_impl(past_sla_only=False, limit=50)
    escalation_run_ids = [e["run_id"] for e in escalation_items]
    past_sla = escalate_list_impl(past_sla_only=True, limit=50)
    state_summary = {
        "running_count": len(run_ids),
        "escalation_backlog": len(escalation_run_ids),
        "past_sla_count": len(past_sla),
    }
    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    evidence_summary = [
        {"run_id": r.get("run_id"), "status": r.get("status"), "agent": r.get("agent")}
        for r in (completed[-5:] + failed[-5:])
    ]
    next_steps: list[str] = []
    if past_sla:
        next_steps.append(f"Resolve {len(past_sla)} past-SLA escalation(s)")
    if failed:
        next_steps.append(f"Review {len(failed)} failed run(s)")
    if run_ids:
        next_steps.append(f"Monitor {len(run_ids)} active run(s)")
    hm = HandoffManager(settings.session_dir)
    snapshot_id = hm.create_snapshot(
        owner,
        run_ids,
    )
    return ToolResult(
        content=json.dumps({"snapshot_id": snapshot_id, "owner": owner, "run_ids": run_ids}),
        structured_content={"snapshot_id": snapshot_id, "owner": owner, "run_ids": run_ids},
        meta={"execution_time_ms": 0},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_handoff_list(limit: int = 10) -> ToolResult:
    """
    List pending handoff snapshots. Equivalent to: thegent orchestrate handoff-list
    """
    from thegent.execution import HandoffManager

    settings = ThegentSettings()
    hm = HandoffManager(settings.session_dir)
    snapshots = hm.list_pending_snapshots(limit=limit)
    return ToolResult(
        content=json.dumps(snapshots),
        structured_content=snapshots,
        meta={"count": len(snapshots)},
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_handoff_show(snapshot_id: str) -> ToolResult:
    """
    Show full handoff summary for a snapshot. Equivalent to: thegent orchestrate handoff-show
    """
    from thegent.execution import HandoffManager

    settings = ThegentSettings()
    hm = HandoffManager(settings.session_dir)
    snap = hm.get_snapshot(snapshot_id)
    if not snap:
        return _error_result(f"Snapshot {snapshot_id} not found.", "Run thegent_handoff_list", extra={})
    return ToolResult(
        content=json.dumps(snap),
        structured_content=snap,
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_handoff_confirm(snapshot_id: str, incoming_owner: str, confidence: float = 1.0) -> ToolResult:
    """
    Incoming owner confirms handoff completeness. Equivalent to: thegent orchestrate handoff-confirm
    """
    from thegent.execution import HandoffManager

    settings = ThegentSettings()
    hm = HandoffManager(settings.session_dir)
    ok = hm.confirm_handoff(snapshot_id=snapshot_id, incoming_owner=incoming_owner, confidence=confidence)
    return ToolResult(
        content=json.dumps({"success": ok, "snapshot_id": snapshot_id}),
        structured_content={"success": ok, "snapshot_id": snapshot_id},
        meta={},
    )


# --- WP-7001: Prompt queue MCP tools ---


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_queue_list(
    include_done: bool = False,
    include_expired: bool = True,
    limit: int | None = None,
) -> ToolResult:
    """
    List prompt queue items (deferred prompts). Use include_done=True to see completed items.
    Returns items with id for claim/done/release/extend_lease/edit.
    """
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    items = pq.list_all(include_done=include_done, include_expired=include_expired, limit=limit)
    return ToolResult(
        content=json.dumps(items),
        structured_content=items,
        meta={"count": len(items)},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_claim(
    claimer_id: str = "mcp-client",
    project: str | None = None,
    lease_seconds: int = 300,
) -> ToolResult:
    """
    Atomically claim the first pending queue item. Returns claimed item with id, or null if queue empty.
    Use project to filter by project path.
    """
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    claimed = pq.claim(claimer_id=claimer_id, lease_seconds=lease_seconds, project=project)
    if claimed is None:
        return ToolResult(
            content=json.dumps({"claimed": None}),
            structured_content={"claimed": None},
            meta={"error": "No pending items"},
        )
    return ToolResult(
        content=json.dumps(claimed),
        structured_content=claimed,
        meta={"claimed": True},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_done(item_id: int) -> ToolResult:
    """Mark a queue item as done by id. Use id from thegent_queue_list or thegent_queue_claim."""
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    ok = pq.done(item_id)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_add(prompt: str, project: str, agent: str | None = None) -> ToolResult:
    """Add a prompt to the queue (deferred execution). Equivalent to $defer in prompt."""
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    count = pq.append(prompt=prompt, project=project, agent=agent)
    return ToolResult(
        content=json.dumps({"success": True, "pending_count": count}),
        structured_content={"success": True, "pending_count": count},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_edit(item_id: int, prompt: str) -> ToolResult:
    """Edit prompt for a pending or claimed queue item. Cannot edit done items."""
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    ok = pq.edit(item_id=item_id, prompt=prompt)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_release(item_id: int) -> ToolResult:
    """Release a claimed queue item back to pending. Use when worker cannot complete."""
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    ok = pq.release(item_id)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_queue_extend_lease(item_id: int, lease_seconds: int = 300) -> ToolResult:
    """Extend lease for a claimed queue item. Use before lease expires."""
    from thegent.queue.storage import PromptQueue

    settings = ThegentSettings()
    pq = PromptQueue(settings.session_dir)
    ok = pq.extend_lease(item_id=item_id, lease_seconds=lease_seconds)
    return ToolResult(
        content=json.dumps({"success": ok, "item_id": item_id}),
        structured_content={"success": ok, "item_id": item_id},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_route(prompt: str, cd: str | None = None) -> ToolResult:
    """
    Route a prompt to an active terminal session if matching. Falls back to thegent_run if none found.
    Equivalent to: thegent route <prompt>
    """
    from thegent.config import ThegentSettings
    from thegent.routing.task_router import TaskRouter
    from thegent.skills.terminal import send_to_tmux_pane

    settings = ThegentSettings()
    router = TaskRouter(settings)
    target_path = str(cd or Path.cwd())
    pane_id = router.find_active_terminal_for_path(target_path)
    if pane_id:
        success = send_to_tmux_pane(pane_id, prompt)
        return ToolResult(
            content=json.dumps({"routed": True, "pane_id": pane_id, "success": success}),
            structured_content={"routed": True, "pane_id": pane_id, "success": success},
            meta={},
        )
    return ToolResult(
        content=json.dumps({"routed": False, "fallback": "Use thegent_run or thegent_bg"}),
        structured_content={"routed": False, "fallback": "Use thegent_run or thegent_bg"},
        meta={},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_free(
    prompt: str,
    cd: str | None = None,
    mode: str = "write",
    timeout: int | None = None,
    live: bool = True,
    bg: bool = False,
) -> ToolResult:
    """
    Run with free tier (copilot gpt-5-mini). Equivalent to: thegent free "<prompt>"
    Default agent for subagents per CLAUDE.md. Use --bg for background.
    """
    settings = ThegentSettings()
    effective_timeout = timeout if timeout is not None else settings.default_timeout_free
    cd_path = Path(cd) if cd else None
    if bg:
        res = bg_impl(
            agent="copilot",
            prompt=prompt,
            cd=cd_path,
            mode=mode,
            timeout=effective_timeout,
            full=False,
            model="gpt-5-mini",
            owner=None,
        )
        if "error" in res:
            return _error_result(res["error"], res.get("remediation", ""), extra=res)
        return ToolResult(
            content=json.dumps(res),
            structured_content=res,
            meta={"session_id": res.get("session_id")},
        )
    res = run_impl(
        agent="copilot",
        prompt=prompt,
        cd=cd_path,
        mode=mode,
        timeout=effective_timeout,
        full=False,
        live=live,
        model="gpt-5-mini",
    )
    if "error" in res:
        return _error_result(res["error"], res.get("remediation", ""), extra=res)
    return ToolResult(
        content=json.dumps(res),
        structured_content=res,
        meta={"exit_code": res.get("exit_code")},
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_flash(
    prompt: str,
    model: str = "claude-haiku-4.5",
    timeout_s: float = 30.0,
) -> ToolResult:
    """
    Run an ultra-short-lived flash agent that executes a single focused task via one LLM call.

    Flash agents are ephemeral: they fire one LLM completion, enforce a strict timeout,
    and self-terminate. Ideal for sub-30-second focused tasks (summarise, classify, extract).

    Args:
        prompt: The task prompt to execute.
        model: LLM model identifier (default: claude-haiku-4.5).
        timeout_s: Maximum execution time in seconds (default: 30.0).
    """
    from thegent.agents.flash_agent import flash as _flash

    start_time = time.perf_counter()
    result = await _flash(prompt=prompt, model=model, timeout_s=timeout_s)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    payload = {
        "output": result.output,
        "success": result.success,
        "elapsed_s": result.elapsed_s,
        "agent_id": result.agent_id,
    }
    if not result.success:
        return ToolResult(
            content=json.dumps({"error": "flash agent timed out", **payload}),
            structured_content={"error": "flash agent timed out", **payload},
            meta={"execution_time_ms": elapsed_ms, "agent_id": result.agent_id},
        )
    return ToolResult(
        content=result.output,
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms, "agent_id": result.agent_id},
    )


# Sitback: dashboard resource, tool, prompts (FastMCP-first projection)
try:
    import importlib

    sitback_mod = importlib.import_module("thegent.mcp.tools.sitback")
    register_sitback = sitback_mod.register_sitback
    register_sitback(mcp)
except Exception:
    _log.debug("sitback not available; skipping sitback registration")

# Mode tools: Plan, Delegate, Discussion, Research, Validation, Protocol
try:
    from thegent.mcp.tools.modes import register_modes

    register_modes(mcp)
except Exception as e:
    _log.debug("mode tools not available; skipping: %s", e)

# Seed detection and storage tools
try:
    from thegent.mcp.tools.seeds import register_seed_tools

    register_seed_tools(mcp)
except Exception as e:
    _log.debug("seed tools not available; skipping: %s", e)

# Elicitation tools: interactive user input via FastMCP ctx.elicit
try:
    from thegent.mcp.tools.elicitation import register_elicitation_tools

    register_elicitation_tools(mcp)

    from pydantic import BaseModel, Field

    class AgentConfig(BaseModel):
        name: str = Field(..., description="Unique name for the agent")
        timeout_secs: int = Field(90, description="Execution timeout in seconds")
        retry_count: int = Field(3, description="Number of retries on failure")

    @mcp.tool()
    async def thegent_configure_agent(ctx: Any = CurrentContext()) -> str:
        """
        Configure agent parameters via structured elicitation.
        """
        from thegent.mcp.tools.elicitation import elicit_structured

        result = await elicit_structured(ctx, "Configure the agent", AgentConfig)
        if result:
            return f"Agent configured: {result.name} (timeout={result.timeout_secs}s, retries={result.retry_count})"
        return "Agent configuration declined or cancelled."

    @mcp.tool()
    async def thegent_approve_deployment(project: str, ctx: Any = CurrentContext()) -> str:
        """
        Request deployment approval for a specific project.
        """
        from thegent.mcp.tools.elicitation import elicit_confirmation

        result = await elicit_confirmation(ctx, f"Approve deployment for project: {project}?")
        if result is True:
            return f"Deployment for {project} APPROVED."
        if result is False:
            return f"Deployment for {project} DENIED."
        return "Approval request cancelled or unavailable."

except Exception as e:
    _log.debug("elicitation tools not available; skipping: %s", e)

# Tool pattern tools: reusable decorator patterns (confirm, progress, retry)
try:
    from thegent.mcp.tools.patterns import register_tool_pattern_tools

    register_tool_pattern_tools(mcp)
except Exception as e:
    _log.debug("tool pattern tools not available; skipping: %s", e)

# Storage and EventStore tools: persistent KV and event streaming for MCP tools
try:
    from thegent.mcp_storage import (
        McpEventStore,
        McpStorage,
    )
    from thegent.mcp_storage import (
        get_mcp_event_store as _get_mcp_event_store,
    )
    from thegent.mcp_storage import (
        get_mcp_storage as _get_mcp_storage,
    )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_storage_get(key: str) -> ToolResult:
        """Get a value from persistent MCP storage.

        Args:
            key: Storage key (non-empty string).

        Returns: JSON with value (null if missing) and found (bool).
        """
        start_ms = time.monotonic()
        try:
            value = _get_mcp_storage().get(key)
            payload: dict[str, Any] = {"key": key, "value": value, "found": value is not None}
        except ValueError as exc:
            payload = {"error": str(exc), "key": key, "found": False}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def thegent_storage_set(
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> ToolResult:
        """Set a value in persistent MCP storage.

        Args:
            key: Storage key (non-empty string).
            value: JSON-encoded value to store.
            ttl_seconds: Optional TTL in seconds.  None means no expiry.

        Returns: JSON with ok (bool) and error if any.
        """
        start_ms = time.monotonic()
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            payload: dict[str, Any] = {"ok": False, "error": f"value is not valid JSON: {exc}"}
            return ToolResult(
                content=json.dumps(payload),
                structured_content=payload,
                meta={"execution_time_ms": 0},
            )
        try:
            _get_mcp_storage().set(key, parsed, ttl=float(ttl_seconds) if ttl_seconds is not None else None)
            payload = {"ok": True, "key": key}
        except (ValueError, TypeError) as exc:
            payload = {"ok": False, "error": str(exc), "key": key}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return ToolResult(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def thegent_events_emit(event_type: str, payload: str) -> ToolResult:
        """Emit an event to the MCP event store.

        Args:
            event_type: Dot-separated event type string (e.g. "storage.set").
            payload: JSON-encoded dict payload.

        Returns: JSON with event_id on success, or error.
        """
        start_ms = time.monotonic()
        try:
            parsed_payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            err_payload: dict[str, Any] = {"ok": False, "error": f"payload is not valid JSON: {exc}"}
            return ToolResult(
                content=json.dumps(err_payload),
                structured_content=err_payload,
                meta={"execution_time_ms": 0},
            )
        if not isinstance(parsed_payload, dict):
            err_payload = {"ok": False, "error": "payload must be a JSON object (dict)"}
            return ToolResult(
                content=json.dumps(err_payload),
                structured_content=err_payload,
                meta={"execution_time_ms": 0},
            )
        try:
            event_id = _get_mcp_event_store().emit(event_type, parsed_payload)
            result_payload: dict[str, Any] = {"ok": True, "event_id": event_id, "event_type": event_type}
        except (ValueError, TypeError) as exc:
            result_payload = {"ok": False, "error": str(exc)}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return ToolResult(
            content=json.dumps(result_payload),
            structured_content=result_payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_events_replay(since_id: str | None = None) -> ToolResult:
        """Replay events from the MCP event store.

        Args:
            since_id: If provided, return only events after this event_id.
                      If not found, all events are returned.

        Returns: JSON array of event objects.
        """
        start_ms = time.monotonic()
        events = _get_mcp_event_store().replay(since_event_id=since_id)
        result_payload: dict[str, Any] = {"events": events, "count": len(events)}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return ToolResult(
            content=json.dumps(result_payload),
            structured_content=result_payload,
            meta={"execution_time_ms": elapsed},
        )

    _log.info(
        "storage/event tools registered: thegent_storage_get, thegent_storage_set, "
        "thegent_events_emit, thegent_events_replay"
    )
except Exception as _storage_tools_err:
    _log.debug("storage/event tools not available; skipping: %s", _storage_tools_err)

# Task mode: status/cancel tools for long-running async MCP operations
try:
    from thegent.mcp.task_registry import get_task_registry as _get_task_registry

    _task_reg = _get_task_registry()

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_task_status(task_id: str) -> ToolResult:
        """Return status of a background MCP task created with async_task=True.

        Args:
            task_id: The task_id returned when the task was created.

        Returns: JSON with status (running|done|error|cancelled), progress, result, error.
        """
        result = _task_reg.status(task_id)
        return ToolResult(
            content=json.dumps(result),
            structured_content=result,
            meta={"execution_time_ms": 0},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_task_cancel(task_id: str) -> ToolResult:
        """Cancel a running background MCP task.

        Args:
            task_id: The task_id returned when the task was created.

        Returns: JSON with cancelled (bool) and status.
        """
        result = _task_reg.cancel(task_id)
        return ToolResult(
            content=json.dumps(result),
            structured_content=result,
            meta={"execution_time_ms": 0},
        )

    _log.info("task mode tools registered: thegent_task_status, thegent_task_cancel")
except Exception as _task_mode_err:
    _log.debug("task mode tools not available; skipping: %s", _task_mode_err)

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


# ============ Provider/Model Management MCP Endpoints ============


@mcp.tool()
def list_providers(include_credentials: bool = False) -> str:
    """List all configured providers with their settings."""
    import json

    from thegent.provider_model_manager import list_providers

    return json.dumps(list_providers(include_credentials=include_credentials), indent=2)


@mcp.tool()
def get_provider(name: str) -> str:
    """Get a specific provider configuration."""
    import json

    from thegent.provider_model_manager import get_provider

    result = get_provider(name)
    if result is None:
        return json.dumps({"error": f"Provider '{name}' not found"})
    return json.dumps(result, indent=2)


@mcp.tool()
def add_provider(
    name: str,
    base_url: str,
    model: str,
    api_key: str | None = None,
    extra_aliases: list[str] | None = None,
    login_url: str | None = None,
) -> str:
    """Add a new provider configuration."""
    import json

    from thegent.provider_model_manager import add_provider

    success, msg = add_provider(
        name=name,
        base_url=base_url,
        model=model,
        api_key=api_key,
        extra_aliases=extra_aliases,
        login_url=login_url,
    )
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def update_provider(
    name: str,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    extra_aliases: list[str] | None = None,
) -> str:
    """Update an existing provider configuration."""
    import json

    from thegent.provider_model_manager import update_provider

    success, msg = update_provider(
        name=name,
        base_url=base_url,
        model=model,
        api_key=api_key,
        extra_aliases=extra_aliases,
    )
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def delete_provider(name: str, remove_credentials: bool = True) -> str:
    """Delete a provider configuration."""
    import json

    from thegent.provider_model_manager import delete_provider

    success, msg = delete_provider(name, remove_credentials=remove_credentials)
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def list_credentials() -> str:
    """List all configured credentials (API keys and OAuth)."""
    import json

    from thegent.provider_model_manager import list_credentials

    return json.dumps(list_credentials(), indent=2)


@mcp.tool()
def add_api_key(provider: str, api_key: str) -> str:
    """Add or update API key for a provider."""
    import json

    from thegent.provider_model_manager import add_api_key

    success, msg = add_api_key(provider, api_key)
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def remove_api_key(provider: str) -> str:
    """Remove API key for a provider."""
    import json

    from thegent.provider_model_manager import remove_api_key

    success, msg = remove_api_key(provider)
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def validate_provider(name: str) -> str:
    """Validate a provider by testing connectivity and credentials."""
    import json

    from thegent.provider_model_manager import validate_provider

    success, msg, details = validate_provider(name)
    return json.dumps(
        {
            "success": success,
            "message": msg,
            "details": details,
        }
    )


@mcp.tool()
def discover_models(provider: str | None = None) -> str:
    """Discover available models from provider APIs."""
    import json

    from thegent.provider_model_manager import discover_models

    return json.dumps(discover_models(provider), indent=2)


@mcp.tool()
def list_models(provider: str | None = None) -> str:
    """List all models, optionally filtered by provider."""
    import json

    from thegent.provider_model_manager import list_models

    return json.dumps(list_models(provider), indent=2)


@mcp.tool()
def add_model_alias(provider: str, model: str, alias: str) -> str:
    """Add a model alias for a provider."""
    import json

    from thegent.provider_model_manager import add_model_alias

    success, msg = add_model_alias(provider, model, alias)
    return json.dumps({"success": success, "message": msg})


@mcp.tool()
def remove_model_alias(provider: str, alias: str) -> str:
    """Remove a model alias from a provider."""
    import json

    from thegent.provider_model_manager import remove_model_alias

    success, msg = remove_model_alias(provider, alias)
    return json.dumps({"success": success, "message": msg})


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_acp_invoke(
    agent_url: str,
    task: str,
    payload: str = "{}",
) -> str:
    """
    Invoke a remote ACP agent and return its result (FR-ACP-002).

    Uses the ACP <-> MCP bridge to call any ACP-compatible agent endpoint
    over HTTP and return the agent's plain-text response.

    Args:
        agent_url: Base URL of the remote ACP agent (e.g. http://localhost:8420)
        task:      Human-readable task description / prompt sent to the agent
        payload:   JSON string with extra context dict forwarded to the agent
                   (default: empty object)

    Returns: JSON string with {success, result, agent_id, elapsed_ms}
    """
    import json as _json
    import time as _time

    from thegent.adapters.acp_client import ACPClient, ACPServerUnreachableError
    from thegent.adapters.acp_mcp_bridge import ACPAgentCallError, AcpMcpBridge

    try:
        context: dict = _json.loads(payload) if payload else {}
    except _json.JSONDecodeError as exc:
        return _json.dumps({"success": False, "error": f"Invalid payload JSON: {exc}", "result": "", "agent_id": ""})

    bridge = AcpMcpBridge(acp_client=ACPClient(base_url=agent_url))

    start = _time.perf_counter()
    try:
        result_text = await bridge.acp_agent_to_mcp_tool(
            agent_url=agent_url,
            task=task,
            payload=context,
        )
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return _json.dumps(
            {
                "success": True,
                "result": result_text,
                "agent_url": agent_url,
                "elapsed_ms": elapsed_ms,
            }
        )
    except ACPServerUnreachableError as exc:
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return _json.dumps(
            {
                "success": False,
                "error": f"ACP agent unreachable: {exc}",
                "result": "",
                "agent_url": agent_url,
                "elapsed_ms": elapsed_ms,
            }
        )
    except ACPAgentCallError as exc:
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return _json.dumps(
            {
                "success": False,
                "error": str(exc),
                "result": "",
                "agent_url": agent_url,
                "elapsed_ms": elapsed_ms,
            }
        )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_macos_run_script(
    script: str,
    language: Literal["applescript", "jxa"] = "applescript",
) -> str:
    """
    Run an AppleScript or JXA (JavaScript for Automation) script on macOS.

    Wraps *osascript* to give agents agent-driven desktop control on macOS.
    Returns a JSON object with ``{success, output, error}``.

    On non-macOS platforms the tool returns immediately with
    ``{success: false, error: "Not macOS"}``.

    Args:
        script:   Script source code to execute.
        language: Scripting language — ``"applescript"`` (default) or ``"jxa"``.
    """
    import json as _json

    from thegent.automation.macos_desktop import MacOSDesktopAutomation

    automation = MacOSDesktopAutomation()

    result = automation.run_jxa(script) if language == "jxa" else automation.run_applescript(script)

    return _json.dumps(
        {
            "success": result.success,
            "output": result.output,
            "error": result.error,
        }
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_config_resolve(
    tenant_id: str | None = None,
    session_id: str | None = None,
    keys: list[str] | None = None,
) -> dict[str, Any]:
    """WP-CP-5.2: Resolve thegent configuration for a tenant/session context.

    Args:
        tenant_id: Optional tenant identifier.
        session_id: Optional session/run identifier.
        keys: Optional list of specific config keys to resolve.
    """
    from thegent.config_provider import get_config_provider

    provider = get_config_provider()
    return provider.resolve(tenant_id=tenant_id, session_id=session_id, keys=keys)


def http_app(stateless_http: bool = True):
    """Return ASGI app with EventStore (mountable in FastAPI/Starlette).

    stateless_http=True allows per-request JSON-RPC without SSE session
    (for simple clients, CI, verification).

    Additionally registers:
    - POST /v1/responses  → LiteLLM Router Responses API handler
    - WS   /v1/responses/ws → LiteLLM Router WebSocket Responses handler

    These routes enable Claude Code (clode) and Codex CLI to use the
    Responses API format while routing through LiteLLM's multi-provider
    Router for fallback, cost-tracking, and caching.
    """
    app = mcp.http_app(
        event_store=_get_event_store(),
        retry_interval=2000,
        transport="http",
        stateless_http=stateless_http,
    )
    # Some app objects used in testing may not implement add_middleware; guard to avoid attribute errors
    if hasattr(app, "add_middleware"):
        cast("Any", app).add_middleware(BearerAuthMiddleware)

    # Wire LiteLLM Responses API routes so that clode/Codex CLI requests
    # are routed through the LiteLLM Router (multi-provider, with fallback,
    # cost-tracking, and caching support).
    #
    # The StarletteWithLifespan object returned by mcp.http_app() exposes
    # both add_route() (HTTP) and add_websocket_route() (WebSocket).
    if hasattr(app, "add_route") and hasattr(app, "add_websocket_route"):
        from thegent.routing.litellm_responses_handler import (
            handle_responses_request,
            handle_responses_websocket,
        )

        cast("Any", app).add_route(
            "/v1/responses",
            handle_responses_request,
            methods=["POST"],
        )
        cast("Any", app).add_websocket_route(
            "/v1/responses/ws",
            handle_responses_websocket,
        )
        _log.info("registered /v1/responses (POST) and /v1/responses/ws (WebSocket) via LiteLLM Router")
    else:
        _log.warning(
            "http_app: ASGI app does not support add_route/add_websocket_route; /v1/responses routes NOT registered"
        )

    return app


def http_app_factory():
    """Factory for uvicorn --reload."""
    return http_app(stateless_http=True)


def run(host: str | None = None, port: int | None = None, reload: bool = False) -> None:
    """Start the FastMCP server with EventStore and optional Docket."""
    import warnings

    # Suppress websockets deprecation warnings (uvicorn uses websockets.legacy until uvicorn updates)
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="websockets.legacy",
    )
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="uvicorn.protocols.websockets.websockets_impl",
    )

    import uvicorn

    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    # FASTMCP_DOCKET_URL is FastMCP-specific, not thegent-specific, so keep as env var
    # docket_url = os.environ.get("FASTMCP_DOCKET_URL")  # Reserved for future FastMCP integration

    if reload:
        # For reload to work, we need to pass app as a string import path
        uvicorn.run(
            "thegent.mcp_server:http_app_factory",
            host=host or settings.mcp_host,
            port=port or settings.mcp_port,
            reload=True,
            factory=True,
        )
    else:
        app = http_app(stateless_http=True)
        uvicorn.run(
            app,
            host=host or settings.mcp_host,
            port=port or settings.mcp_port,
            lifespan="on",
        )


if __name__ == "__main__":
    run()
