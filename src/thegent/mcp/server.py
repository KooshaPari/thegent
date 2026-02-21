"""FastMCP server for thegent."""

import asyncio
import importlib.util
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, cast

from fastmcp import FastMCP
from fastmcp._vendor.docket_di import Depends
from fastmcp.server.elicitation import (
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
from starlette.requests import Request
from starlette.responses import Response

from thegent.config import ThegentSettings

# Auto-initialize IDE integrations on startup
from thegent.ide.auto_init import auto_init_on_startup
from thegent.mcp import server_catalog_tools as _server_tools_catalog
from thegent.mcp import server_error_result as _shared_error_result
from thegent.mcp import server_load_module as _load_server_module_shared
from thegent.mcp import server_stable_json as _shared_stable_json
from thegent.mcp.server_runtime_helpers import (
    create_event_store,
    create_http_app,
    health_response,
    lifespan_proxy,
    run_server,
)


def _load_server_auth_module() -> Any:
    auth_path = Path(__file__).with_suffix("") / "auth.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_auth", auth_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load auth helpers from: {auth_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_auth = _load_server_auth_module()
_get_settings = _server_auth.get_settings
BearerAuthMiddleware = _server_auth.BearerAuthMiddleware


def _load_server_lifecycle_module() -> Any:
    lifecycle_path = Path(__file__).with_suffix("") / "lifecycle.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_lifecycle", lifecycle_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load lifecycle helpers from: {lifecycle_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_lifecycle = _load_server_lifecycle_module()
_run_lifecycle = _server_lifecycle.run_lifespan


def _load_server_resource_sessions_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_sessions.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_sessions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load session resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_sessions = _load_server_resource_sessions_module()


def _load_server_resource_catalog_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_catalog.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_catalog", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load catalog resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_catalog = _load_server_resource_catalog_module()


def _load_server_resource_workstream_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_workstream.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_workstream", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workstream resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_workstream = _load_server_resource_workstream_module()


def _load_server_resource_contracts_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_contracts.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_contracts", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load contracts resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_contracts = _load_server_resource_contracts_module()


def _load_server_resource_system_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_system.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_system", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load system resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_system = _load_server_resource_system_module()


def _load_server_resource_workflow_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "resources_workflow.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_resource_workflow", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workflow resource helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_resource_workflow = _load_server_resource_workflow_module()


def _load_server_workflow_prompts_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "workflow_prompts.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_workflow_prompts", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workflow prompt helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_workflow_prompts = _load_server_workflow_prompts_module()


def _load_server_session_tools_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "session_tools.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_session_tools", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load session tool registrations from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_session_tools = _load_server_session_tools_module()


def _load_server_handoff_queue_tools_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_handoff_queue.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_handoff_queue_tools", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load handoff/queue tool registrations from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_handoff_queue_tools = _load_server_handoff_queue_tools_module()


def _load_server_queue_mutations_tools_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_queue_mutations.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_queue_mutations_tools", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load queue mutation tool registrations from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_queue_mutations_tools = _load_server_queue_mutations_tools_module()


def _load_server_tools_sessions_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_sessions.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_sessions", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load session tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_sessions = _load_server_tools_sessions_module()


def _load_server_tools_queue_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_queue.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_queue", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load queue tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_queue = _load_server_tools_queue_module()


def _load_server_tools_terminal_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_terminal.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_terminal", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load terminal tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_terminal = _load_server_tools_terminal_module()


def _load_server_tools_escalation_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_escalation.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_escalation", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load escalation tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_escalation = _load_server_tools_escalation_module()


def _load_server_tools_governance_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_governance.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_governance", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load governance tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_governance = _load_server_tools_governance_module()


def _load_server_tools_research_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_research.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_research", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load research tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_research = _load_server_tools_research_module()


def _load_server_tools_planning_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_planning.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_planning", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load planning tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_planning = _load_server_tools_planning_module()


def _load_server_tools_contract_observe_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_contract_observe.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_contract_observe", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load contract/observe tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_contract_observe = _load_server_tools_contract_observe_module()


def _load_server_tools_locking_planning_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_locking_planning.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_locking_planning", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load locking/planning tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_locking_planning = _load_server_tools_locking_planning_module()


def _load_server_tools_skills_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_skills.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_skills", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load skills tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_skills = _load_server_tools_skills_module()


def _load_server_tools_coordination_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_coordination.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_coordination", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load coordination tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_coordination = _load_server_tools_coordination_module()


def _load_server_tools_runtime_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_runtime.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_runtime", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load runtime tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_runtime = _load_server_tools_runtime_module()


def _load_server_tools_batch4_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_batch4.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_batch4", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load batch4 tool registrations from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_batch4 = _load_server_tools_batch4_module()


def _load_server_tools_workstream_lsp_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_workstream_lsp.py"
    spec = importlib.util.spec_from_file_location("thegent.mcp._server_tools_workstream_lsp", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workstream/LSP tool helpers from: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_server_tools_workstream_lsp = _load_server_tools_workstream_lsp_module()


def _load_server_tools_workstream_governance_module() -> Any:
    return _load_server_module_shared(
        server_file=Path(__file__),
        module_filename="tools_workstream_governance.py",
        module_import_name="thegent.mcp._server_tools_workstream_governance",
        failure_message="Unable to load workstream/governance tool registrations",
    )


_server_tools_workstream_governance = _load_server_tools_workstream_governance_module()


def _load_server_tools_prompt_and_handoff_module() -> Any:
    return _load_server_module_shared(
        server_file=Path(__file__),
        module_filename="tools_prompt_and_handoff.py",
        module_import_name="thegent.mcp._server_tools_prompt_and_handoff",
        failure_message="Unable to load prompt/handoff tool wrappers",
    )


_server_tools_prompt_and_handoff = _load_server_tools_prompt_and_handoff_module()


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
    govern_approve_impl,
    govern_vet_impl,
    govern_reject_impl,
    govern_list_pending_impl,
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
    session_send_impl,
    status_impl,
    stop_impl,
    wait_impl,
    wait_next_impl,
    work_stream_claim_impl,
    work_stream_complete_impl,
)
from thegent.cli.commands.impl import get_server_meta_impl
from thegent.mcp.server_dispatch_helpers import (
    build_route_request_payload,
    format_acp_response,
    normalize_bg_routing,
    parse_acp_payload,
    write_session_control_file,
)
from thegent.mcp.server_policy_quality_helpers import (
    resource_session_contract_health_gate_helper,
    resource_session_contract_health_report_helper,
    resource_session_contract_health_trend_helper,
    thegent_session_contract_health_gate_helper,
    thegent_session_contract_health_report_helper,
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
from thegent.mcp import server_cache_elicitation_response as _cache_elicitation_response_shared
from thegent.mcp import server_create_elicitation_cache as _create_elicitation_cache_shared
from thegent.mcp import server_default_cwd_from_context as _default_cwd_from_context_shared
from thegent.mcp import server_default_owner_from_context as _default_owner_from_context_shared
from thegent.mcp import server_elicitation_cache_key as _cache_elicitation_key_shared
from thegent.mcp import server_get_cached_elicitation as _get_cached_elicitation_shared
from thegent.mcp import server_resolve_cwd_elicitation as _resolve_cwd_elicitation_shared
from thegent.mcp import server_resolve_owner_elicitation as _resolve_owner_elicitation_shared

_ELICITATION_CACHE = _create_elicitation_cache_shared(maxsize=100, ttl_seconds=300)  # 5 min TTL


def _cache_elicitation_key(prompt: str, response_type: type) -> str:
    """Backward-compatible wrapper for extracted elicitation cache helper."""
    return _cache_elicitation_key_shared(prompt, response_type)


def _get_cached_elicitation(prompt: str, response_type: type) -> Any | None:
    """OPT-018: Backward-compatible wrapper for extracted cache helper."""
    return _get_cached_elicitation_shared(_ELICITATION_CACHE, prompt=prompt, response_type=response_type)


def _cache_elicitation_response(prompt: str, response_type: type, response: Any) -> None:
    """OPT-018: Backward-compatible wrapper for extracted cache helper."""
    _cache_elicitation_response_shared(_ELICITATION_CACHE, prompt=prompt, response_type=response_type, response=response)


def _resolve_cwd_elicitation(response: Any) -> tuple[Path | None, str | None]:
    """Backward-compatible wrapper for extracted elicitation response helper."""
    return _resolve_cwd_elicitation_shared(
        response,
        accepted_elicitation_type=AcceptedElicitation,
        declined_elicitation_type=DeclinedElicitation,
        cancelled_elicitation_type=CancelledElicitation,
    )


def _resolve_owner_elicitation(response: Any, *, default_owner_tag: str) -> tuple[str | None, str | None]:
    """Backward-compatible wrapper for extracted elicitation response helper."""
    return _resolve_owner_elicitation_shared(
        response,
        default_owner_tag=default_owner_tag,
        accepted_elicitation_type=AcceptedElicitation,
        declined_elicitation_type=DeclinedElicitation,
        cancelled_elicitation_type=CancelledElicitation,
    )


def get_default_cwd(ctx: Context = CurrentContext()) -> Path | None:
    """Inject cwd from request meta (meta.cwd). Client can send meta.cwd in request."""
    return _default_cwd_from_context_shared(ctx)


def get_default_owner(ctx: Context = CurrentContext()) -> str | None:
    """Inject owner from request meta (meta.owner). Client can send meta.owner in request."""
    return _default_owner_from_context_shared(ctx)


@lifespan
async def thegent_lifespan(mcp_app: FastMCP) -> AsyncIterator[dict[str, Any] | None]:
    """Startup and teardown for thegent MCP server. See gofastmcp.com/servers/lifespan."""
    async for payload in lifespan_proxy(
        mcp_app=mcp_app,
        run_lifecycle=_run_lifecycle,
        log=_log,
        ps_impl=ps_impl,
        auto_init_on_startup=auto_init_on_startup,
    ):
        yield payload


mcp = FastMCP("thegent", lifespan=thegent_lifespan)
_skills_backend = _server_tools_skills.DiscoverySkillBackend()

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


# Backward-compatible aliases while helpers are extracted into dedicated module.
_stable_json = _shared_stable_json
_error_result = _shared_error_result

(
    thegent_list_droids,
    thegent_list_skills,
    thegent_activate_skill,
    thegent_terminal_route,
    thegent_macos_run_script,
) = _server_tools_batch4.register_batch4_tools(
    mcp=mcp,
    server_tools_catalog=_server_tools_catalog,
    server_tools_skills=_server_tools_skills,
    server_tools_terminal=_server_tools_terminal,
    skills_backend=_skills_backend,
    error_result=_error_result,
    list_droids_impl=list_droids_impl,
    get_default_cwd=get_default_cwd,
    depends=Depends,
)


# --- MCP Resources ---


@mcp.resource(
    "thegent://sessions{?include_contract}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_sessions(include_contract: bool = False) -> str:
    """List all background sessions. Returns JSON array of session metadata."""
    return _server_resource_sessions.resource_sessions_impl(
        include_contract=include_contract,
        ps_impl=ps_impl,
    )


@mcp.resource(
    "thegent://session/{id}/meta{?include_contract}",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_meta(id: str, include_contract: bool = False) -> str:
    """Get session metadata (status, pid, owner) by ID."""
    return _server_resource_sessions.resource_session_meta_impl(
        session_id=id,
        include_contract=include_contract,
        status_impl=status_impl,
    )


@mcp.resource(
    "thegent://session/{id}/logs{?stderr,tail}",
    mime_type="text/plain",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_session_logs(id: str, stderr: bool = False, tail: int | None = None) -> str:
    """Get logs from a background session. Use ?stderr=true for stderr, ?tail=N for last N lines."""
    return _server_resource_sessions.resource_session_logs_impl(
        session_id=id,
        stderr=stderr,
        tail=tail,
        logs_impl=logs_impl,
    )


@mcp.resource(
    "thegent://dag",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_dag() -> str:
    """Get DAG from .factory/dag-session.md as {frontmatter, tasks} JSON."""
    return _server_resource_catalog.resource_dag_impl(dag_list_impl=dag_list_impl)


@mcp.resource(
    "thegent://agents",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_agents() -> str:
    """List available agents. Returns JSON array of {name, backend}."""
    return _server_resource_catalog.resource_agents_impl(list_agents_impl=list_agents_impl)


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
    return _server_resource_catalog.resource_models_impl(
        provider=provider,
        include_contract=include_contract,
        list_models_impl=list_models_impl,
    )


@mcp.resource(
    "thegent://models/contract",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_models_contract() -> str:
    """Return model routing contract schema metadata."""
    return _server_resource_catalog.resource_models_contract_impl()


@mcp.resource(
    "thegent://workstream",
    mime_type="text/markdown",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workstream() -> str:
    """Get the canonical WORK_STREAM.md content."""
    return _server_resource_workstream.resource_workstream_impl()


@mcp.resource(
    "thegent://events/session-complete",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_events_session_complete() -> str:
    """Event stream for session completion events (for auto-launch system)."""
    return _server_resource_workstream.resource_events_session_complete_impl()


@mcp.resource(
    "thegent://workstream/db",
    mime_type="application/json",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def resource_workstream_db() -> str:
    """Workstream database metadata and schema info."""
    return _server_resource_workstream.resource_workstream_db_impl()


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
    return _server_resource_contracts.resource_session_contracts_impl(
        owner=owner,
        all=all,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
        session_contract_audit_impl=session_contract_audit_impl,
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
    return resource_session_contract_health_gate_helper(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        resource_impl=_server_resource_contracts.resource_session_contract_health_gate_impl,
        session_contract_health_gate_impl=session_contract_health_gate_impl,
        stable_json=_stable_json,
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
    return resource_session_contract_health_report_helper(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        resource_impl=_server_resource_contracts.resource_session_contract_health_report_impl,
        session_contract_health_report_impl=session_contract_health_report_impl,
        stable_json=_stable_json,
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
    return resource_session_contract_health_trend_helper(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        resource_impl=_server_resource_contracts.resource_session_contract_health_trend_impl,
        session_contract_health_trend_impl=session_contract_health_trend_impl,
        stable_json=_stable_json,
    )


(
    resource_observe_summary,
    resource_meta,
    resource_operations,
    resource_modes,
) = _server_resource_system.register_system_resources(
    mcp=mcp,
    observe_summary_impl=lambda **kwargs: observe_summary_impl(**kwargs),
    get_server_meta_impl=get_server_meta_impl,
    stable_json=_stable_json,
)


# --- MCP Prompts ---


(
    resource_workflow_triggers,
    thegent_workflow_idea,
    thegent_workflow_quality_green,
    thegent_workflow_next_item,
    thegent_workflow_gardening,
) = _server_workflow_prompts.register_workflow_prompts(
    mcp=mcp,
    server_resource_workflow=_server_resource_workflow,
)


resource_workflow_gardening = _server_workflow_prompts.register_workflow_gardening_resource(
    mcp=mcp,
    server_resource_workflow=_server_resource_workflow,
)


(
    thegent_run_agent,
    thegent_create_wbs,
    thegent_bg_task,
    thegent_govern_vet,
    thegent_handoff,
) = _server_tools_prompt_and_handoff.register_prompt_and_handoff_wrappers(
    mcp=mcp,
    server_workflow_prompts=_server_workflow_prompts,
    server_tools_governance=_server_tools_governance,
    govern_vet_impl=govern_vet_impl,
    server_tools_terminal=_server_tools_terminal,
    resolve_cwd=_resolve_cwd,
    error_result=_error_result,
    settings_factory=ThegentSettings,
    escalate_list_impl=escalate_list_impl,
)


# --- MCP Tools ---


(
    thegent_session_list,
    thegent_session_show,
    thegent_session_logs,
    thegent_session_send,
    thegent_session_attach_hint,
) = _server_session_tools.register_session_tools(
    mcp=mcp,
    server_tools_sessions=_server_tools_sessions,
    ps_impl=ps_impl,
    logs_impl=logs_impl,
    session_send_impl=session_send_impl,
)

_registered_workstream_governance_tools = _server_tools_workstream_governance.register_workstream_governance_tools(
    mcp=mcp,
    server_tools_governance=_server_tools_governance,
    govern_approve_impl=govern_approve_impl,
    govern_reject_impl=govern_reject_impl,
)


# --- WL-105: Dynamic Client Tool Registration ---


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_register_tool(
    session_id: str,
    name: str,
    description: str,
    input_schema: dict[str, Any],
) -> str:
    """
    Register a client-owned tool for a session (WL-105).

    The registered tool becomes available for the model to invoke during the
    session. When the model calls it, a tool_call_requested event is emitted
    to the client via thegent_session_send dynamic_tool_invoke flow.

    Args:
        session_id: The session this tool is scoped to.
        name: Unique tool name within the session.
        description: Human-readable description for the model.
        input_schema: JSON Schema object describing the tool's arguments.

    Returns: JSON with registered tool details.
    """
    from thegent.mcp.dynamic_tools import DynamicToolSpec

    spec = DynamicToolSpec(name=name, description=description, input_schema=input_schema)
    registered = _server_tools_sessions._dynamic_registry.register_dynamic_tool(session_id, spec)
    return json.dumps(
        {
            "success": True,
            "registered": {
                "name": registered.name,
                "description": registered.description,
                "input_schema": registered.input_schema,
            },
        },
        indent=2,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
async def thegent_complete_tool_call(
    session_id: str,
    call_id: str,
    output: str,
    success: bool,
) -> str:
    """
    Deliver a client's response to a pending dynamic tool call (WL-105).

    The client calls this after receiving a tool_call_requested event. Raises
    KeyError if call_id is unknown (fail-loud: never silently drops unknown calls).

    Args:
        session_id: The session this call belongs to.
        call_id: The call_id from the tool_call_requested event.
        output: String output from the client-side tool execution.
        success: True if the tool succeeded.

    Returns: JSON with the tool_call_completed event payload.
    """
    result = _server_tools_sessions._dynamic_registry.resolve_tool_call_for_session(
        session_id=session_id,
        call_id=call_id,
        output=output,
        success=success,
    )
    event = _server_tools_sessions._dynamic_registry.tool_call_completed_event(result)
    return json.dumps({"success": True, "event": event}, indent=2)


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
async def thegent_list_dynamic_tools(
    session_id: str,
) -> str:
    """
    List all client-registered dynamic tools for a session (WL-105).

    Args:
        session_id: The session whose tool registry to query.

    Returns: JSON array of registered tool definitions.
    """
    tools = _server_tools_sessions._dynamic_registry.list_dynamic_tools(session_id)
    return json.dumps(
        {
            "session_id": session_id,
            "tools": [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools
            ],
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
    return _server_tools_runtime.config_resolve_impl(
        tenant_id=tenant_id,
        session_id=session_id,
        overrides=overrides,
        keys=keys,
    )


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
    return _server_tools_runtime.negotiate_contract_impl(
        contract_id=contract_id,
        supported_versions=supported_versions,
        session_contract_negotiate_impl=session_contract_negotiate_impl,
    )


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
            cwd, status = _resolve_cwd_elicitation(cached_response)
            if status == "declined":
                return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
            if status == "cancelled":
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
        else:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit(ELICIT_CWD_MSG, response_type=str),
                    timeout=ELICIT_TIMEOUT_S,
                )
                # OPT-018: Cache the response
                _cache_elicitation_response(ELICIT_CWD_MSG, str, elicitation)
                cwd, status = _resolve_cwd_elicitation(elicitation)
                if status == "declined":
                    return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                if status == "cancelled":
                    return _error_result("Elicitation cancelled.", "Retry with explicit params")
                if status == "ambiguous":
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
            agent,
            prompt,
            cd_path,
            mode,
            timeout,
            full,
            True,
            model,
            None,
            None,
            None,
            False,
            None,
            None,
            "standard",
            confidence,
            arbitration,
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
            full=False,
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
    write_session_control_file(
        session_root=settings.session_dir,
        session_id=session_id,
        filename="takeover.json",
        content=json.dumps({"prompt": prompt}),
    )
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
    write_session_control_file(
        session_root=settings.session_dir,
        session_id=session_id,
        filename="STOP",
        content="STOP",
    )
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
            cwd, status = _resolve_cwd_elicitation(cached_response)
            if status is None:
                elicited_cwd = True
            elif status == "declined":
                return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
            elif status == "cancelled":
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
        else:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit(ELICIT_CWD_MSG, response_type=str),
                    timeout=ELICIT_TIMEOUT_S,
                )
                # OPT-018: Cache the response
                _cache_elicitation_response(ELICIT_CWD_MSG, str, elicitation)
                cwd, status = _resolve_cwd_elicitation(elicitation)
                if status is None:
                    elicited_cwd = True
                elif status == "declined":
                    return _error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                elif status == "cancelled":
                    return _error_result("Elicitation cancelled.", "Retry with explicit params")
                elif status == "ambiguous":
                    return _error_result("Ambiguous cwd.", "Provide cd=/path explicitly")
            except TimeoutError:
                return _error_result(
                    "Elicitation timed out (no response from client).",
                    "Provide cd=/path in tool call",
                )
    cd_path = cwd
    route_contract: dict[str, Any] | None = None
    requested_model = model
    requested_provider = provider or agent
    requested_policy, route_lookup_policy, routing_for_child, failover = normalize_bg_routing(
        routing=routing,
        default_routing=ThegentSettings().default_routing,
        failover=failover,
    )

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
            owner_tag, status = _resolve_owner_elicitation(
                elicitation,
                default_owner_tag=_default_owner_tag(cwd),
            )
            if status == "cancelled":
                return _error_result("Elicitation cancelled.", "Retry with explicit params")
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
        route_request=build_route_request_payload(
            include_contract=include_contract,
            requested_model=requested_model,
            requested_provider_hint=requested_provider,
            policy=requested_policy,
            resolved_model_alias=model,
            resolved_agent=agent,
        ),
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
    return _server_tools_runtime.ps_tool_impl(
        owner=owner,
        all=all,
        include_contract=include_contract,
        ps_impl=ps_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_status(session_id: str, include_contract: bool = False) -> ToolResult:
    """
    Get session status for quick health check.

    Args:
        session_id: Session ID to query

    Returns: ToolResult with session status and metadata
    """
    return _server_tools_runtime.status_tool_impl(
        session_id=session_id,
        include_contract=include_contract,
        status_impl=status_impl,
        log=_log,
    )


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
    return _server_tools_runtime.logs_tool_impl(
        session_id=session_id,
        tail=tail,
        stderr=stderr,
        logs_impl=logs_impl,
        log=_log,
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
    return _server_tools_contract_observe.thegent_inspect_impl(
        session_ids=session_ids,
        owner=owner,
        tail=tail,
        stderr=stderr,
        include_contract=include_contract,
        inspect_impl=inspect_impl,
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
    return _server_tools_contract_observe.thegent_session_contracts_impl(
        owner=owner,
        all=all,
        missing_only=missing_only,
        summary_only=summary_only,
        strict=strict,
        session_contract_audit_impl=session_contract_audit_impl,
    )


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
    return thegent_session_contract_health_gate_helper(
        owner=owner,
        all=all,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_gate_impl=session_contract_health_gate_impl,
        stable_json=_stable_json,
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
    return thegent_session_contract_health_report_helper(
        owner=owner,
        all=all,
        strict=strict,
        top_blocked=top_blocked,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        session_contract_health_report_impl=session_contract_health_report_impl,
        stable_json=_stable_json,
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
    return _server_tools_contract_observe.thegent_session_contract_health_trend_impl(
        payload_type=payload_type,
        owner=owner,
        all=all,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        session_contract_health_trend_impl=session_contract_health_trend_impl,
        stable_json=_stable_json,
        coerce_issue_types=_coerce_issue_types,
    )


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
    return _server_tools_contract_observe.thegent_observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        trend_samples=trend_samples,
        top_escalations=top_escalations,
        observe_summary_impl=observe_summary_impl,
        stable_json=_stable_json,
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
    return _server_tools_coordination.thegent_wait_impl(
        session_id=session_id,
        timeout=timeout,
        logger=_log,
        wait_impl=wait_impl,
    )


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
    return _server_tools_coordination.thegent_inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        limit=limit,
        inbox_list_impl=inbox_list_impl,
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
    return _server_tools_coordination.thegent_inbox_wait_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        poll_interval=poll_interval,
        timeout=timeout,
        logger=_log,
        inbox_list_impl=inbox_list_impl,
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
    return _server_tools_coordination.thegent_stop_impl(
        session_id=session_id,
        force=force,
        logger=_log,
        stop_impl=stop_impl,
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
    return _server_tools_coordination.thegent_pause_impl(
        session_id=session_id,
        reason=reason,
        logger=_log,
        settings_factory=ThegentSettings,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_resume(session_id: str) -> ToolResult:
    """
    WP-1009: Resume a paused session (register resume event in registry).

    Args:
        session_id: Session ID to resume

    Returns: ToolResult with status
    """
    return _server_tools_coordination.thegent_resume_impl(
        session_id=session_id,
        logger=_log,
        settings_factory=ThegentSettings,
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
    return _server_tools_coordination.thegent_continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
        continuity_snapshot_impl=continuity_snapshot_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_operations(operation: str | None = None) -> ToolResult:
    """
    List universal operation taxonomy: orchestrate, govern, recover, observe, plan.

    Args:
        operation: Optional filter (orchestrate | govern | recover | observe | plan)

    Returns: JSON with operations and their commands/mcp_tools.
    """
    return _server_tools_catalog.thegent_list_operations_impl(
        operation=operation,
        stable_json_impl=_stable_json,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_list_modes(mode: str | None = None) -> ToolResult:
    """
    List multi-agent orchestration modes (G-KD-04).

    Args:
        mode: Optional filter (sequential_delegation | parallel_consensus | review_loop)

    Returns: JSON with modes, phases, use_case, risk_profile, selection_hint.
    """
    return _server_tools_catalog.thegent_list_modes_impl(
        mode=mode,
        stable_json_impl=_stable_json,
        error_result_impl=_error_result,
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
    return _server_tools_catalog.thegent_suggest_mode_impl(
        risk=risk,
        urgency=urgency,
        confidence=confidence,
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
    return _server_tools_catalog.thegent_list_agents_impl(
        list_agents_impl=list_agents_impl,
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
    return _server_tools_catalog.thegent_list_models_impl(
        provider=provider,
        include_contract=include_contract,
        by_model=by_model,
        list_models_impl=list_models_impl,
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
    return _server_tools_catalog.thegent_resolve_model_route_impl(
        model=model,
        provider=provider,
        policy=policy,
        error_result_impl=_error_result,
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
    return await _server_tools_planning.thegent_dag_list_impl(
        cd=cd,
        default_cwd=default_cwd,
        ctx=ctx,
        resolve_cwd=_resolve_cwd,
        elicit_cwd_msg=ELICIT_CWD_MSG,
        elicit_timeout_s=ELICIT_TIMEOUT_S,
        accepted_elicitation_type=AcceptedElicitation,
        declined_elicitation_type=DeclinedElicitation,
        cancelled_elicitation_type=CancelledElicitation,
        dag_list_impl=dag_list_impl,
        error_result_impl=_error_result,
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
    return _server_tools_planning.thegent_do_next_impl(
        cd=cd,
        limit=limit,
        do_next_impl=do_next_impl,
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
    return _server_tools_locking_planning.thegent_lock_resource_impl(
        resource=resource,
        ttl=ttl,
        cd=cd,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_unlock_resource(resource: str, token: str, cd: str | None = None) -> ToolResult:
    """
    Release an exclusive lock on a resource using the token from thegent_lock_resource.
    """
    return _server_tools_locking_planning.thegent_unlock_resource_impl(
        resource=resource,
        token=token,
        cd=cd,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_verify_context(files: list[str], cd: str | None = None) -> ToolResult:
    """
    Verify if any of the given files have been modified (OCC check).
    Returns current versions (hashes) of files for stale-state detection.
    """
    return _server_tools_locking_planning.thegent_verify_context_impl(
        files=files,
        cd=cd,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_terminal_attach(pane_id: str) -> ToolResult:
    """
    Get instructions to attach to a terminal session.
    """
    from thegent.skills.terminal import list_tmux_panes

    return _server_tools_terminal.thegent_terminal_attach_impl(
        pane_id=pane_id,
        list_tmux_panes=list_tmux_panes,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_workstream_claim(item_id: str, agent_id: str) -> ToolResult:
    """
    Claim an item in the unified work stream.
    """
    return _server_tools_workstream_lsp.workstream_claim_tool_impl(
        item_id=item_id,
        agent_id=agent_id,
        claim_impl=work_stream_claim_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_lsp_diagnostics(file_path: str) -> ToolResult:
    """WL-109: return normalized LSP diagnostics for a file."""
    from thegent.mcp.lsp_tools import lsp_diagnostics

    return _server_tools_workstream_lsp.lsp_diagnostics_tool_impl(
        file_path=file_path,
        diagnostics_impl=lsp_diagnostics,
        error_result=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_lsp_symbol_lookup(symbol_name: str, file_path: str | None = None) -> ToolResult:
    """WL-109: lookup a symbol through the LSP adapter."""
    from thegent.mcp.lsp_tools import lsp_symbol_lookup

    return _server_tools_workstream_lsp.lsp_symbol_lookup_tool_impl(
        symbol_name=symbol_name,
        file_path=file_path,
        symbol_lookup_impl=lsp_symbol_lookup,
        error_result=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_lsp_hover(file_path: str, line: int, character: int) -> ToolResult:
    """WL-109: return hover information for a source position."""
    from thegent.mcp.lsp_tools import lsp_hover

    return _server_tools_workstream_lsp.lsp_hover_tool_impl(
        file_path=file_path,
        line=line,
        character=character,
        hover_impl=lsp_hover,
        error_result=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_workstream_complete(item_id: str, agent_id: str) -> ToolResult:
    """
    Mark an item as complete in the unified work stream.
    """
    return _server_tools_workstream_lsp.workstream_complete_tool_impl(
        item_id=item_id,
        agent_id=agent_id,
        complete_impl=work_stream_complete_impl,
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
    return await _server_tools_research.thegent_ddg_search_impl(
        query=query,
        num_results=num_results,
        ctx=ctx,
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
    return _server_tools_research.thegent_reddit_search_impl(
        query=query,
        num_results=num_results,
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
    return await _server_tools_research.thegent_scrape_url_impl(
        url=url,
        use_playwright=use_playwright,
        ctx=ctx,
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
    return _server_tools_research.thegent_deep_research_impl(
        query=query,
        subreddits=subreddits,
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
    return await _server_tools_research.thegent_suggest_prompt_impl(
        raw_prompt=raw_prompt,
        ctx=ctx,
        logger=_log,
    )


# --- Plan / CLI parity tools ---


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_plan_get_next(cd: str | None = None) -> ToolResult:
    """
    Get first work item prompt for scripting. Use with thegent_run or thegent_bg.
    Equivalent to: thegent plan get-next
    """
    return _server_tools_planning.thegent_plan_get_next_impl(
        cd=cd,
        do_next_impl=do_next_impl,
        error_result_impl=_error_result,
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
    return _server_tools_planning.thegent_plan_wait_next_impl(
        cd=cd,
        poll=poll,
        timeout=timeout,
        sources=sources,
        wait_next_impl=wait_next_impl,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_history(limit: int = 50) -> ToolResult:
    """
    List execution history (recent runs). Equivalent to: thegent history --limit N
    """
    return _server_tools_planning.thegent_history_impl(
        limit=limit,
        history_impl=history_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_plan_progress(limit: int = 10) -> ToolResult:
    """
    Show recent runs (work-package progress). Alias for thegent_history with smaller default.
    Equivalent to: thegent plan progress --limit N
    """
    return _server_tools_planning.thegent_plan_progress_impl(
        limit=limit,
        history_impl=history_impl,
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
    return _server_tools_planning.thegent_plan_analyze_impl(
        cd=cd,
        pert=pert,
        resources=resources,
        continuity=continuity,
        plan_analyze_impl=plan_analyze_impl,
        error_result_impl=_error_result,
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
    return _server_tools_locking_planning.thegent_retry_impl(
        run_id=run_id,
        agent_override=agent_override,
        failover=failover,
        cd=cd,
        override_reason=override_reason,
        retry_impl=retry_impl,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_plan_incorporate(cd: str | None = None, dry_run: bool = False) -> ToolResult:
    """
    Merge fragments from 02-UNIFIED-WBS into WORK_STREAM.md BACKLOG.
    Equivalent to: thegent plan incorporate
    """
    return _server_tools_locking_planning.thegent_plan_incorporate_impl(
        cd=cd,
        dry_run=dry_run,
        incorporate_impl=incorporate_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_dag_status(cd: str | None = None) -> ToolResult:
    """
    For each DAG task with session_id, return id, status, session_id, session_status.
    Equivalent to: thegent dag status
    """
    return _server_tools_contract_observe.thegent_dag_status_impl(
        cd=cd,
        dag_status_impl=dag_status_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_escalate_list(past_sla_only: bool = False, limit: int = 50) -> ToolResult:
    """
    List escalation queue items (blocked runs). Equivalent to: thegent govern escalate list
    """
    return _server_tools_escalation.thegent_escalate_list_impl(
        past_sla_only=past_sla_only,
        limit=limit,
        escalate_list_impl=escalate_list_impl,
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
    return _server_tools_escalation.thegent_escalate_add_impl(
        run_id=run_id,
        reason=reason,
        sla_minutes=sla_minutes,
        owner=owner,
        agent=agent,
        lane=lane,
        priority=priority,
        escalate_add_impl=escalate_add_impl,
        error_result_impl=_error_result,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_escalate_approve(run_id: str) -> ToolResult:
    """
    Approve an escalation (policy override). Equivalent to: thegent govern escalate approve
    """
    return _server_tools_escalation.thegent_escalate_approve_impl(
        run_id=run_id,
        escalate_approve_impl=escalate_approve_impl,
    )


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
def thegent_escalate_resolve(run_id: str, resolution: str = "resolved") -> ToolResult:
    """
    Mark an escalation item as resolved. Equivalent to: thegent govern escalate resolve
    """
    return _server_tools_escalation.thegent_escalate_resolve_impl(
        run_id=run_id,
        resolution=resolution,
        escalate_resolve_impl=escalate_resolve_impl,
    )


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def thegent_govern_list_pending() -> ToolResult:
    """
    List all pending HITL approval requests (G-GP-05 / WL-019).

    Returns events from governance_events.jsonl with event_type=await_approval
    and status=pending.
    Equivalent to: thegent govern list-pending
    """
    return _server_tools_escalation.thegent_govern_list_pending_impl(
        govern_list_pending_impl=govern_list_pending_impl,
    )


(
    thegent_handoff_list,
    thegent_handoff_show,
    thegent_handoff_confirm,
    thegent_queue_list,
    thegent_queue_claim,
) = _server_handoff_queue_tools.register_handoff_queue_tools(
    mcp=mcp,
    server_tools_terminal=_server_tools_terminal,
    server_tools_queue=_server_tools_queue,
    settings_factory=ThegentSettings,
    error_result=_error_result,
)


# --- WP-7001: Prompt queue MCP tools ---


(
    thegent_queue_done,
    thegent_queue_add,
    thegent_queue_edit,
    thegent_queue_release,
    thegent_queue_extend_lease,
) = _server_queue_mutations_tools.register_queue_mutation_tools(
    mcp=mcp,
    server_tools_queue=_server_tools_queue,
    settings_factory=ThegentSettings,
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
    from thegent.mcp.storage import (
        get_mcp_event_store as _get_mcp_event_store,
    )
    from thegent.mcp.storage import (
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
    del request
    return health_response()


def _get_event_store() -> EventStore:
    """EventStore: MemoryStore default, Redis when FASTMCP_EVENT_STORE_URL set."""
    from key_value.aio.stores.redis import RedisStore

    return cast(
        "EventStore",
        create_event_store(
            env=os.environ,
            event_store_cls=EventStore,
            redis_store_cls=RedisStore,
        ),
    )


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
    import time as _time

    from thegent.adapters.acp_client import ACPClient, ACPServerUnreachableError
    from thegent.adapters.acp_mcp_bridge import ACPAgentCallError, AcpMcpBridge

    context, payload_error = parse_acp_payload(payload)
    if payload_error:
        return format_acp_response(
            success=False,
            error=payload_error,
            result="",
            agent_url=agent_url,
            elapsed_ms=0,
        )

    bridge = AcpMcpBridge(acp_client=ACPClient(base_url=agent_url))

    start = _time.perf_counter()
    try:
        result_text = await bridge.acp_agent_to_mcp_tool(
            agent_url=agent_url,
            task=task,
            payload=context or {},
        )
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return format_acp_response(
            success=True,
            result=result_text,
            agent_url=agent_url,
            elapsed_ms=elapsed_ms,
        )
    except ACPServerUnreachableError as exc:
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return format_acp_response(
            success=False,
            error=f"ACP agent unreachable: {exc}",
            result="",
            agent_url=agent_url,
            elapsed_ms=elapsed_ms,
        )
    except ACPAgentCallError as exc:
        elapsed_ms = int((_time.perf_counter() - start) * 1000)
        return format_acp_response(
            success=False,
            error=str(exc),
            result="",
            agent_url=agent_url,
            elapsed_ms=elapsed_ms,
        )


# ---------------------------------------------------------------------------
# Git Journal Tools (Micro-commit audit trail, local-only)
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_create_session(
    session_id: str,
    repo_path: str = ".",
    track_secrets: bool = True,
) -> dict[str, Any]:
    """Create a new git journal session for micro-commit audit trail.

    The journal creates micro-commits for every file change using git refs
    that are NEVER pushed to remote. This provides a complete local audit
    trail including secrets and sensitive files.

    Args:
        session_id: Unique identifier for this session
        repo_path: Path to git repository root
        track_secrets: Whether to track files that may contain secrets
    """
    from thegent.audit.shadow_audit_git import GitJournal

    journal = GitJournal(
        Path(repo_path).resolve(),
        session_id,
        track_secrets=track_secrets,
        auto_commit=True,
    )

    return {
        "status": "created",
        "session_id": session_id,
        "audit_ref": journal.audit_ref,
        "message": "Git journal session created. Changes will be tracked with micro-commits.",
        "note": "Audit refs are local-only and never pushed to remote.",
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_record_change(
    session_id: str,
    file_path: str,
    action: str = "modified",
    repo_path: str = ".",
    content: str | None = None,
) -> dict[str, Any]:
    """Record a file change as a micro-commit in the journal.

    Args:
        session_id: The journal session ID
        file_path: Path to the file (relative to repo root)
        action: Action type (modified, created, deleted)
        repo_path: Path to git repository root
        content: Optional file content (for remote file tracking)
    """
    from thegent.audit.shadow_audit_git import GitJournal

    journal = GitJournal(Path(repo_path).resolve(), session_id)

    # If content provided, use it; otherwise read from file
    if content is not None:
        file_content = content.encode()
    else:
        full_path = Path(repo_path).resolve() / file_path
        if full_path.exists():
            file_content = full_path.read_bytes()
        else:
            file_content = None

    sha = journal.record_file_change(
        file_path,
        content=file_content,
        action=action,
    )

    return {
        "status": "recorded",
        "sha": sha,
        "file_path": file_path,
        "action": action,
        "session_id": session_id,
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_snapshot(
    session_id: str,
    message: str = "snapshot",
    repo_path: str = ".",
) -> dict[str, Any]:
    """Create a snapshot of the current working tree state.

    This reads all tracked files and creates a commit representing
    the current state. Useful for periodic snapshots.

    Args:
        session_id: The journal session ID
        message: Optional message for the snapshot
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournal

    journal = GitJournal(Path(repo_path).resolve(), session_id)
    sha = journal.record_snapshot(message)

    return {
        "status": "snapshot_created",
        "sha": sha,
        "session_id": session_id,
        "message": message,
    }


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def journal_get_log(
    session_id: str,
    repo_path: str = ".",
) -> dict[str, Any]:
    """Get the audit log for a journal session.

    Args:
        session_id: The journal session ID
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournal

    journal = GitJournal(Path(repo_path).resolve(), session_id)
    log_entries = journal.get_audit_log()

    return {
        "session_id": session_id,
        "entries": log_entries,
        "total": len(log_entries),
    }


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def journal_list_sessions(
    repo_path: str = ".",
) -> dict[str, Any]:
    """List all git journal sessions in a repository.

    Args:
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournal

    sessions = GitJournal.list_sessions(Path(repo_path).resolve())

    return {
        "sessions": sessions,
        "total": len(sessions),
        "note": "All audit refs are local-only and never pushed to remote.",
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_finalize(
    session_id: str,
    message: str = "session complete",
    repo_path: str = ".",
) -> dict[str, Any]:
    """Finalize a journal session with a summary commit.

    Args:
        session_id: The journal session ID
        message: Optional message for the final commit
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournal

    journal = GitJournal(Path(repo_path).resolve(), session_id)
    sha = journal.finalize_session(message)

    return {
        "status": "finalized",
        "sha": sha,
        "session_id": session_id,
        "audit_ref": journal.audit_ref,
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_prune(
    repo_path: str = ".",
    max_age_days: int = 30,
) -> dict[str, Any]:
    """Prune old journal sessions.

    Args:
        repo_path: Path to git repository root
        max_age_days: Maximum age in days to keep sessions
    """
    from thegent.audit.shadow_audit_git import GitJournal

    pruned = GitJournal.prune_old_sessions(Path(repo_path).resolve(), max_age_days)

    return {
        "pruned_count": pruned,
        "max_age_days": max_age_days,
        "message": f"Pruned {pruned} sessions older than {max_age_days} days",
    }


# ---------------------------------------------------------------------------
# Enhanced Git Journal Tools (P1 features: watching, attestation, native scanner)
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_create_enhanced(
    session_id: str,
    repo_path: str = ".",
    track_secrets: bool = True,
    enable_watching: bool = False,
    enable_attestation: bool = False,
    batch_size: int = 10,
) -> dict[str, Any]:
    """Create an enhanced git journal session with P1 features.

    Enhanced features:
    - Native secret scanner integration (BKM-11)
    - Real-time file watching (watchman/fswatch/FSMonitor)
    - Cryptographic attestation (SHA-256)
    - Batching for performance

    Args:
        session_id: Unique identifier for this session
        repo_path: Path to git repository root
        track_secrets: Whether to track/scrub secrets
        enable_watching: Enable real-time file watching
        enable_attestation: Enable cryptographic attestation
        batch_size: Number of changes to batch before commit
    """
    from thegent.audit.shadow_audit_git import GitJournalEnhanced

    journal = GitJournalEnhanced(
        Path(repo_path).resolve(),
        session_id,
        track_secrets=track_secrets,
        auto_commit=True,
        enable_watching=enable_watching,
        enable_attestation=enable_attestation,
        batch_size=batch_size,
    )

    stats = journal.get_performance_stats()

    return {
        "status": "created",
        "session_id": session_id,
        "audit_ref": journal.audit_ref,
        "message": "Enhanced git journal session created.",
        "features": {
            "native_scanner": stats["native_scanner"],
            "watcher": stats["watcher"],
            "attestation": enable_attestation,
            "batch_size": batch_size,
        },
        "note": "Audit refs are local-only and never pushed to remote.",
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_start_watching(
    session_id: str,
    repo_path: str = ".",
) -> dict[str, Any]:
    """Start real-time file watching for a journal session.

    Uses watchman, fswatch, or Git FSMonitor depending on availability.

    Args:
        session_id: The journal session ID
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournalEnhanced

    journal = GitJournalEnhanced(
        Path(repo_path).resolve(),
        session_id,
        enable_watching=True,
    )

    journal.start_watching()
    stats = journal.get_performance_stats()

    return {
        "status": "watching_started",
        "session_id": session_id,
        "watcher": stats["watcher"],
        "message": f"File watching started using {stats['watcher'] or 'none'}",
    }


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def journal_get_attestations(
    session_id: str,
    repo_path: str = ".",
) -> dict[str, Any]:
    """Get cryptographic attestations for a journal session.

    Attestations provide verifiable proof of audit trail integrity.

    Args:
        session_id: The journal session ID
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournalEnhanced

    journal = GitJournalEnhanced(
        Path(repo_path).resolve(),
        session_id,
        enable_attestation=True,
    )

    attestations = journal.get_attestations()

    # Verify each attestation
    verified = []
    for att in attestations:
        is_valid = journal.verify_attestation(att)
        verified.append(
            {
                "commit_sha": att["commit_sha"],
                "timestamp": att["timestamp"],
                "algorithm": att["algorithm"],
                "verified": is_valid,
            }
        )

    return {
        "session_id": session_id,
        "attestations": verified,
        "total": len(attestations),
        "all_verified": all(a["verified"] for a in verified),
    }


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
def journal_get_stats(
    session_id: str,
    repo_path: str = ".",
) -> dict[str, Any]:
    """Get performance statistics for a journal session.

    Args:
        session_id: The journal session ID
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournalEnhanced

    journal = GitJournalEnhanced(Path(repo_path).resolve(), session_id)
    stats = journal.get_performance_stats()

    return {
        "session_id": session_id,
        "stats": stats,
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
async def journal_record_async(
    session_id: str,
    file_path: str,
    action: str = "modified",
    repo_path: str = ".",
    content: str | None = None,
) -> dict[str, Any]:
    """Record a file change asynchronously in the journal.

    Non-blocking operation for high-performance scenarios.

    Args:
        session_id: The journal session ID
        file_path: Path to the file (relative to repo root)
        action: Action type (modified, created, deleted)
        repo_path: Path to git repository root
        content: Optional file content
    """
    from thegent.audit.shadow_audit_git import GitJournalAsync

    journal = GitJournalAsync.create(
        Path(repo_path).resolve(),
        session_id,
        enhanced=True,
    )

    file_content = content.encode() if content else None
    sha = await journal.record_file_change(file_path, file_content, action=action)

    return {
        "status": "recorded_async",
        "sha": sha,
        "file_path": file_path,
        "action": action,
        "session_id": session_id,
    }


@mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
def journal_flush_batch(
    session_id: str,
    repo_path: str = ".",
) -> dict[str, Any]:
    """Flush pending batched changes as a single commit.

    Creates one commit for all pending changes, improving performance
    when batch_size > 1.

    Args:
        session_id: The journal session ID
        repo_path: Path to git repository root
    """
    from thegent.audit.shadow_audit_git import GitJournalEnhanced

    journal = GitJournalEnhanced(Path(repo_path).resolve(), session_id)
    sha = journal._flush_batch()

    return {
        "status": "flushed",
        "sha": sha,
        "session_id": session_id,
        "message": "Batched changes flushed to single commit",
    }


# ---------------------------------------------------------------------------
# WL-085: SubAgentEvent streaming MCP tool
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
def thegent_orchestration_events(
    max_events: int = 100,
    timeout_ms: int = 0,
) -> ToolResult:
    """
    WL-085: Drain SubAgentEvents from the process-global event queue.

    Returns all events currently queued by SubAgentDispatcher (started,
    completed). Intended for real-time TUI and client consumption via
    polling or SSE.

    Args:
        max_events: Maximum number of events to return in one call (default: 100).
        timeout_ms: If >0, wait up to this many milliseconds for at least one
            event before returning.  0 means non-blocking drain only.

    Returns:
        ToolResult with structured_content {"events": [...], "count": N}.

    # @trace WL-085
    """
    import asyncio as _asyncio

    from thegent.orchestration.event_queue import get_global_event_queue

    _log.debug("thegent_orchestration_events max_events=%d timeout_ms=%d", max_events, timeout_ms)
    start_time = time.perf_counter()

    queue = get_global_event_queue()
    events: list[dict[str, Any]] = []

    if timeout_ms > 0 and queue.empty:
        # Block briefly waiting for the first event; run in a short async loop.
        async def _wait_one() -> None:
            try:
                evt = await _asyncio.wait_for(queue.get(), timeout=timeout_ms / 1000.0)
                events.append(evt.model_dump())
            except _asyncio.TimeoutError:
                pass

        _asyncio.run(_wait_one())

    # Drain up to max_events without discarding excess events from the queue.
    remaining = max_events - len(events)
    for _ in range(remaining):
        if queue.empty:
            break
        evt = queue.get_nowait()
        events.append(evt.model_dump())

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    payload: dict[str, Any] = {"events": events, "count": len(events)}
    return ToolResult(
        content=json.dumps(payload),
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms},
    )


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
    return create_http_app(
        mcp=cast("Any", mcp),
        event_store=_get_event_store(),
        bearer_auth_middleware=BearerAuthMiddleware,
        log=_log,
        stateless_http=stateless_http,
    )


def http_app_factory():
    """Factory for uvicorn --reload."""
    return http_app(stateless_http=True)


def run(host: str | None = None, port: int | None = None, reload: bool = False) -> None:
    """Start the FastMCP server with EventStore and optional Docket."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    # FASTMCP_DOCKET_URL is FastMCP-specific, not thegent-specific, so keep as env var
    # docket_url = os.environ.get("FASTMCP_DOCKET_URL")  # Reserved for future FastMCP integration
    run_server(
        host=host,
        port=port,
        reload=reload,
        settings=settings,
        http_app_factory_import_path="thegent.mcp_server:http_app_factory",
        http_app_builder=http_app,
    )


if __name__ == "__main__":
    run()
