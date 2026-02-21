"""FastMCP server for thegent."""

import asyncio
import json
import logging
import time
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
from fastmcp.server.lifespan import lifespan
from fastmcp.server.transforms import PromptsAsTools, ResourcesAsTools
from fastmcp.tools.tool import ToolResult

from thegent.config import ThegentSettings

# Auto-initialize IDE integrations on startup
from thegent.ide.auto_init import auto_init_on_startup
from thegent.mcp import server_catalog_tools as _server_tools_catalog
from thegent.mcp import server_control_tools as _server_control_tools
from thegent.mcp import server_error_result as _shared_error_result
from thegent.mcp import server_execution_tools as _server_execution_tools
from thegent.mcp import server_load_module as _load_server_module_shared
from thegent.mcp import server_journal_tools as _server_journal_tools
from thegent.mcp import server_ops_tools as _server_ops_tools
from thegent.mcp import server_planning_tools as _server_planning_tools
from thegent.mcp import server_research_tools as _server_research_tools
from thegent.mcp import server_consolidated_tools as _server_consolidated_tools
from thegent.mcp import server_resource_routes as _server_resource_routes
from thegent.mcp import server_runtime_entry as _server_runtime_entry
from thegent.mcp import server_stable_json as _shared_stable_json
from thegent.mcp import server_terminal_tools as _server_terminal_tools
from thegent.mcp import server_bootstrap as _server_bootstrap
from thegent.mcp import server_cache_elicitation_response as _cache_elicitation_response_shared
from thegent.mcp import server_create_elicitation_cache as _create_elicitation_cache_shared
from thegent.mcp import server_default_cwd_from_context as _default_cwd_from_context_shared
from thegent.mcp import server_default_owner_from_context as _default_owner_from_context_shared
from thegent.mcp import server_elicitation_cache_key as _cache_elicitation_key_shared
from thegent.mcp import server_get_cached_elicitation as _get_cached_elicitation_shared
from thegent.mcp import server_resolve_cwd_elicitation as _resolve_cwd_elicitation_shared
from thegent.mcp import server_resolve_owner_elicitation as _resolve_owner_elicitation_shared
from thegent.mcp.server_middleware import setup_middleware as _setup_middleware
from thegent.mcp.server_tool_icons import TOOL_ICONS
from thegent.mcp.server_resources import (
    load_resource_catalog as _load_resource_catalog,
    load_resource_contracts as _load_resource_contracts,
    load_resource_sessions as _load_resource_sessions,
    load_resource_system as _load_resource_system,
    load_resource_workflow as _load_resource_workflow,
    load_resource_workstream as _load_resource_workstream,
    load_workflow_prompts as _load_workflow_prompts,
)
from thegent.mcp.server_runtime_helpers import (
    create_event_store,
    create_http_app,
    health_response,
    lifespan_proxy,
    run_server,
)
from thegent.mcp.server_tool_loader import (
    load_handoff_queue_tools as _load_handoff_queue_tools,
    load_queue_mutations_tools as _load_queue_mutations_tools,
    load_session_tools as _load_session_tools,
    load_tools_batch4 as _load_tools_batch4,
    load_tools_contract_observe as _load_tools_contract_observe,
    load_tools_coordination as _load_tools_coordination,
    load_tools_dynamic_registry as _load_tools_dynamic_registry,
    load_tools_escalation as _load_tools_escalation,
    load_tools_governance as _load_tools_governance,
    load_tools_locking_planning as _load_tools_locking_planning,
    load_tools_planning as _load_tools_planning,
    load_tools_provider_models as _load_tools_provider_models,
    load_tools_prompt_and_handoff as _load_tools_prompt_and_handoff,
    load_tools_queue as _load_tools_queue,
    load_tools_research as _load_tools_research,
    load_tools_runtime as _load_tools_runtime,
    load_tools_sessions as _load_tools_sessions,
    load_tools_skills as _load_tools_skills,
    load_tools_terminal as _load_tools_terminal,
    load_tools_workstream_governance as _load_tools_workstream_governance,
    load_tools_workstream_lsp as _load_tools_workstream_lsp,
)

_server_auth = _server_bootstrap.load_auth(_load_server_module_shared)
_get_settings = _server_auth.get_settings
BearerAuthMiddleware = _server_auth.BearerAuthMiddleware

_server_lifecycle = _server_bootstrap.load_lifecycle(_load_server_module_shared)
_run_lifecycle = _server_lifecycle.run_lifespan

_server_resource_sessions = _load_resource_sessions(_load_server_module_shared)
_server_resource_catalog = _load_resource_catalog(_load_server_module_shared)
_server_resource_workstream = _load_resource_workstream(_load_server_module_shared)
_server_resource_contracts = _load_resource_contracts(_load_server_module_shared)
_server_resource_system = _load_resource_system(_load_server_module_shared)
_server_resource_workflow = _load_resource_workflow(_load_server_module_shared)
_server_workflow_prompts = _load_workflow_prompts(_load_server_module_shared)

_server_session_tools = _load_session_tools(_load_server_module_shared)
_server_handoff_queue_tools = _load_handoff_queue_tools(_load_server_module_shared)
_server_queue_mutations_tools = _load_queue_mutations_tools(_load_server_module_shared)
_server_tools_sessions = _load_tools_sessions(_load_server_module_shared)
_server_tools_queue = _load_tools_queue(_load_server_module_shared)
_server_tools_terminal = _load_tools_terminal(_load_server_module_shared)
_server_tools_escalation = _load_tools_escalation(_load_server_module_shared)
_server_tools_governance = _load_tools_governance(_load_server_module_shared)
_server_tools_research = _load_tools_research(_load_server_module_shared)
_server_tools_planning = _load_tools_planning(_load_server_module_shared)
_server_tools_contract_observe = _load_tools_contract_observe(_load_server_module_shared)
_server_tools_locking_planning = _load_tools_locking_planning(_load_server_module_shared)
_server_tools_skills = _load_tools_skills(_load_server_module_shared)
_server_tools_coordination = _load_tools_coordination(_load_server_module_shared)
_server_tools_runtime = _load_tools_runtime(_load_server_module_shared)
_server_tools_batch4 = _load_tools_batch4(_load_server_module_shared)
_server_tools_workstream_lsp = _load_tools_workstream_lsp(_load_server_module_shared)
# WL-120 B90-W2-D1: dynamic client tool registration group
_server_tools_workstream_governance = _load_tools_workstream_governance(_load_server_module_shared)
_server_tools_prompt_and_handoff = _load_tools_prompt_and_handoff(_load_server_module_shared)
_server_tools_dynamic_registry = _load_tools_dynamic_registry(_load_server_module_shared)
_server_tools_provider_models = _load_tools_provider_models(_load_server_module_shared)

_server_tools_harness = _load_server_module_shared(
    server_file=Path(__file__),
    module_filename="tools_harness.py",
    module_import_name="thegent.mcp._server_tools_harness",
    failure_message="Unable to load harness tool helpers",
)

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

_log = logging.getLogger(__name__)

# ROB-016: Elicitation timeout (seconds). Fail-safe if client doesn't respond.
ELICIT_TIMEOUT_S = 30

# OPT-018: ElicitationResponse caching with SHA256 of prompt+response.
(
    _ELICITATION_CACHE,
    _cache_elicitation_key,
    _get_cached_elicitation,
    _cache_elicitation_response,
    _resolve_cwd_elicitation,
    _resolve_owner_elicitation,
    _get_default_cwd,
    _get_default_owner,
) = _server_bootstrap.build_elicitation_helpers(
    create_elicitation_cache=_create_elicitation_cache_shared,
    elicitation_cache_key=_cache_elicitation_key_shared,
    get_cached_elicitation=_get_cached_elicitation_shared,
    cache_elicitation_response=_cache_elicitation_response_shared,
    resolve_cwd_elicitation=_resolve_cwd_elicitation_shared,
    resolve_owner_elicitation=_resolve_owner_elicitation_shared,
    default_cwd_from_context=_default_cwd_from_context_shared,
    default_owner_from_context=_default_owner_from_context_shared,
    accepted_elicitation_type=AcceptedElicitation,
    declined_elicitation_type=DeclinedElicitation,
    cancelled_elicitation_type=CancelledElicitation,
)


def get_default_cwd(ctx: Context = CurrentContext()) -> Path | None:
    """Inject cwd from request meta (meta.cwd). Client can send meta.cwd in request."""
    return _get_default_cwd(ctx)


def get_default_owner(ctx: Context = CurrentContext()) -> str | None:
    """Inject owner from request meta (meta.owner). Client can send meta.owner in request."""
    return _get_default_owner(ctx)


thegent_lifespan = _server_bootstrap.build_lifespan(
    lifespan_decorator=lifespan,
    lifespan_proxy=lifespan_proxy,
    run_lifecycle=_run_lifecycle,
    log=_log,
    ps_impl=ps_impl,
    auto_init_on_startup=auto_init_on_startup,
)


mcp = FastMCP("thegent", lifespan=thegent_lifespan)
app = mcp  # Public alias used by cut-over gate: from thegent.mcp.server import app
_skills_backend = _server_tools_skills.DiscoverySkillBackend()

# --- Middleware (order: first added = outermost) ---
_setup_middleware(mcp)


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


(
    resource_sessions,
    resource_session_meta,
    resource_session_logs,
    resource_dag,
    resource_agents,
    resource_models,
    resource_models_contract,
    resource_workstream,
    resource_events_session_complete,
    resource_workstream_db,
    resource_session_contracts,
    resource_session_contract_health_gate,
    resource_session_contract_health_report,
    resource_session_contract_health_trend,
) = _server_resource_routes.register_resource_routes(
    mcp=mcp,
    server_resource_sessions=_server_resource_sessions,
    server_resource_catalog=_server_resource_catalog,
    server_resource_workstream=_server_resource_workstream,
    server_resource_contracts=_server_resource_contracts,
    resource_session_contract_health_gate_helper=resource_session_contract_health_gate_helper,
    resource_session_contract_health_report_helper=resource_session_contract_health_report_helper,
    resource_session_contract_health_trend_helper=resource_session_contract_health_trend_helper,
    ps_impl=ps_impl,
    status_impl=status_impl,
    logs_impl=logs_impl,
    dag_list_impl=dag_list_impl,
    list_agents_impl=list_agents_impl,
    list_models_impl=list_models_impl,
    session_contract_audit_impl=session_contract_audit_impl,
    session_contract_health_gate_impl=session_contract_health_gate_impl,
    session_contract_health_report_impl=session_contract_health_report_impl,
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


# --- Harness TUI Interaction Tools ---
(
    thegent_harness_interact,
    thegent_harness_list_actions,
    thegent_harness_get_command,
    thegent_harness_register_host,
) = _server_tools_harness.register_harness_tools(
    mcp=mcp,
    server_tools_harness=_server_tools_harness,
)


# --- WL-105: Dynamic Client Tool Registration (WL-120 B90-W2-D1: extracted) ---

(
    thegent_register_tool,
    thegent_complete_tool_call,
    thegent_list_dynamic_tools,
) = _server_tools_dynamic_registry.register_dynamic_registry_tools(
    mcp=mcp,
    server_tools_sessions=_server_tools_sessions,
    error_result=_error_result,
)

(
    thegent_list_operations,
    thegent_list_modes,
    thegent_suggest_mode,
    thegent_list_agents,
    thegent_list_models,
    thegent_resolve_model_route,
    thegent_session_contracts,
    thegent_session_contract_health_gate,
    thegent_session_contract_health_report,
    thegent_session_contract_health_trend,
    thegent_observe_summary,
) = _server_ops_tools.register_ops_tools(
    mcp=mcp,
    server_tools_catalog=_server_tools_catalog,
    server_tools_contract_observe=_server_tools_contract_observe,
    stable_json=_stable_json,
    error_result=_error_result,
    list_agents_impl=list_agents_impl,
    list_models_impl=list_models_impl,
    observe_summary_impl=observe_summary_impl,
    session_contract_audit_impl=session_contract_audit_impl,
    session_contract_health_gate_impl=session_contract_health_gate_impl,
    session_contract_health_report_impl=session_contract_health_report_impl,
    session_contract_health_trend_impl=session_contract_health_trend_impl,
    session_contract_health_gate_helper=thegent_session_contract_health_gate_helper,
    session_contract_health_report_helper=thegent_session_contract_health_report_helper,
    coerce_issue_types=_coerce_issue_types,
)

(
    thegent_config_resolve,
    thegent_negotiate_contract,
    thegent_run,
    thegent_loop,
    thegent_loop_takeover,
    thegent_loop_stop,
    thegent_bg,
    thegent_free,
    thegent_flash,
) = _server_execution_tools.register_execution_tools(
    mcp=mcp,
    server_tools_runtime=_server_tools_runtime,
    error_result=_error_result,
    get_default_cwd=get_default_cwd,
    get_default_owner=get_default_owner,
    resolve_cwd=_resolve_cwd,
    run_impl=run_impl,
    bg_impl=bg_impl,
    session_contract_negotiate_impl=session_contract_negotiate_impl,
    write_session_control_file=write_session_control_file,
    normalize_bg_routing=normalize_bg_routing,
    build_route_request_payload=build_route_request_payload,
    settings_factory=ThegentSettings,
    default_owner_tag=_default_owner_tag,
    resolve_cwd_elicitation=_resolve_cwd_elicitation,
    resolve_owner_elicitation=_resolve_owner_elicitation,
    get_cached_elicitation=_get_cached_elicitation,
    cache_elicitation_response=_cache_elicitation_response,
    accepted_elicitation_type=AcceptedElicitation,
    output_parser_schema_version=OUTPUT_PARSER_SCHEMA_VERSION,
    elicit_timeout_s=ELICIT_TIMEOUT_S,
    elicit_cwd_msg=ELICIT_CWD_MSG,
    elicit_owner_msg=ELICIT_OWNER_MSG,
)

(
    thegent_ps,
    thegent_status,
    thegent_logs,
    thegent_inspect,
    thegent_wait,
    thegent_inbox_list,
    thegent_inbox_wait,
    thegent_stop,
    thegent_pause,
    thegent_resume,
    thegent_continuity_snapshot,
) = _server_control_tools.register_control_tools(
    mcp=mcp,
    server_tools_runtime=_server_tools_runtime,
    server_tools_contract_observe=_server_tools_contract_observe,
    server_tools_coordination=_server_tools_coordination,
    ps_impl=ps_impl,
    status_impl=status_impl,
    logs_impl=logs_impl,
    inspect_impl=inspect_impl,
    wait_impl=wait_impl,
    inbox_list_impl=inbox_list_impl,
    stop_impl=stop_impl,
    continuity_snapshot_impl=continuity_snapshot_impl,
    settings_factory=ThegentSettings,
    logger=_log,
)


(
    thegent_dag_list,
    thegent_do_next,
    thegent_lock_resource,
    thegent_unlock_resource,
    thegent_verify_context,
    thegent_plan_get_next,
    thegent_plan_wait_next,
    thegent_history,
    thegent_plan_progress,
    thegent_plan_analyze,
    thegent_retry,
    thegent_plan_incorporate,
    thegent_dag_status,
    thegent_escalate_list,
    thegent_escalate_add,
    thegent_escalate_approve,
    thegent_escalate_resolve,
    thegent_govern_list_pending,
) = _server_planning_tools.register_planning_tools(
    mcp=mcp,
    server_tools_planning=_server_tools_planning,
    server_tools_locking_planning=_server_tools_locking_planning,
    server_tools_contract_observe=_server_tools_contract_observe,
    server_tools_escalation=_server_tools_escalation,
    get_default_cwd=get_default_cwd,
    resolve_cwd=_resolve_cwd,
    elicit_cwd_msg=ELICIT_CWD_MSG,
    elicit_timeout_s=ELICIT_TIMEOUT_S,
    accepted_elicitation_type=AcceptedElicitation,
    declined_elicitation_type=DeclinedElicitation,
    cancelled_elicitation_type=CancelledElicitation,
    dag_list_impl=dag_list_impl,
    do_next_impl=do_next_impl,
    wait_next_impl=wait_next_impl,
    history_impl=history_impl,
    plan_analyze_impl=plan_analyze_impl,
    retry_impl=retry_impl,
    incorporate_impl=incorporate_impl,
    dag_status_impl=dag_status_impl,
    escalate_list_impl=escalate_list_impl,
    escalate_add_impl=escalate_add_impl,
    escalate_approve_impl=escalate_approve_impl,
    escalate_resolve_impl=escalate_resolve_impl,
    govern_list_pending_impl=govern_list_pending_impl,
    error_result=_error_result,
)


(
    thegent_terminal_list,
    thegent_terminal_inspect,
    thegent_terminal_send,
    thegent_terminal_attach,
    thegent_workstream_claim,
    thegent_lsp_diagnostics,
    thegent_lsp_symbol_lookup,
    thegent_lsp_hover,
    thegent_workstream_complete,
) = _server_terminal_tools.register_terminal_tools(
    mcp=mcp,
    server_tools_terminal=_server_tools_terminal,
    server_tools_workstream_lsp=_server_tools_workstream_lsp,
    error_result=_error_result,
    work_stream_claim_impl=work_stream_claim_impl,
    work_stream_complete_impl=work_stream_complete_impl,
)

(
    thegent_ddg_search,
    thegent_reddit_search,
    thegent_scrape_url,
    thegent_deep_research,
    thegent_suggest_prompt,
) = _server_research_tools.register_research_tools(
    mcp=mcp,
    server_tools_research=_server_tools_research,
    logger=_log,
)


# --- Consolidated Tools (reduced tool count via parameter-based actions) ---
(
    thegent_web,
    thegent_queue,
    thegent_session,
    thegent_workstream,
) = _server_consolidated_tools.register_consolidated_tools(
    mcp=mcp,
    logger=_log,
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


# ============ Provider/Model Management MCP Endpoints ============


(
    list_providers,
    get_provider,
    add_provider,
    update_provider,
    delete_provider,
    list_credentials,
    add_api_key,
    remove_api_key,
    validate_provider,
    discover_models,
    list_models,
    add_model_alias,
    remove_model_alias,
) = _server_tools_provider_models.register_provider_model_tools(mcp=mcp)


(
    journal_create_session,
    journal_record_change,
    journal_snapshot,
    journal_get_log,
    journal_list_sessions,
    journal_finalize,
    journal_prune,
    journal_create_enhanced,
    journal_start_watching,
    journal_get_attestations,
    journal_get_stats,
    journal_record_async,
    journal_flush_batch,
    thegent_orchestration_events,
) = _server_journal_tools.register_journal_tools(mcp=mcp, logger=_log)

(
    health,
    _get_event_store,
    thegent_acp_invoke,
    http_app,
    http_app_factory,
    run,
) = _server_runtime_entry.register_runtime_entry(
    mcp=mcp,
    health_response=health_response,
    create_event_store=create_event_store,
    create_http_app=create_http_app,
    bearer_auth_middleware=BearerAuthMiddleware,
    log=_log,
    parse_acp_payload=parse_acp_payload,
    format_acp_response=format_acp_response,
    run_server=run_server,
    settings_factory=ThegentSettings,
    http_app_factory_import_path="thegent.mcp_server:http_app_factory",
)


if __name__ == "__main__":
    run()
