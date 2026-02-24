"""Optional MCP tool registrations extracted from server.py."""

from __future__ import annotations

import importlib
import orjson as json
import time
from typing import Any, Callable

from fastmcp.server.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult


def register_storage_event_tools(
    *,
    mcp: Any,
    get_mcp_storage: Callable[[], Any],
    get_mcp_event_store: Callable[[], Any],
    tool_result_type: type[ToolResult] = ToolResult,
) -> dict[str, Callable[..., ToolResult]]:
    """Register storage/event tool wrappers and return exported callables."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_storage_get(key: str) -> ToolResult:
        start_ms = time.monotonic()
        try:
            value = get_mcp_storage().get(key)
            payload: dict[str, Any] = {"key": key, "value": value, "found": value is not None}
        except ValueError as exc:
            payload = {"error": str(exc), "key": key, "found": False}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return tool_result_type(
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
        start_ms = time.monotonic()
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            payload: dict[str, Any] = {"ok": False, "error": f"value is not valid JSON: {exc}"}
            return tool_result_type(
                content=json.dumps(payload),
                structured_content=payload,
                meta={"execution_time_ms": 0},
            )
        try:
            get_mcp_storage().set(key, parsed, ttl=float(ttl_seconds) if ttl_seconds is not None else None)
            payload = {"ok": True, "key": key}
        except (ValueError, TypeError) as exc:
            payload = {"ok": False, "error": str(exc), "key": key}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return tool_result_type(
            content=json.dumps(payload),
            structured_content=payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def thegent_events_emit(event_type: str, payload: str) -> ToolResult:
        start_ms = time.monotonic()
        try:
            parsed_payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            err_payload: dict[str, Any] = {"ok": False, "error": f"payload is not valid JSON: {exc}"}
            return tool_result_type(
                content=json.dumps(err_payload),
                structured_content=err_payload,
                meta={"execution_time_ms": 0},
            )
        if not isinstance(parsed_payload, dict):
            err_payload = {"ok": False, "error": "payload must be a JSON object (dict)"}
            return tool_result_type(
                content=json.dumps(err_payload),
                structured_content=err_payload,
                meta={"execution_time_ms": 0},
            )
        try:
            event_id = get_mcp_event_store().emit(event_type, parsed_payload)
            result_payload: dict[str, Any] = {"ok": True, "event_id": event_id, "event_type": event_type}
        except (ValueError, TypeError) as exc:
            result_payload = {"ok": False, "error": str(exc)}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return tool_result_type(
            content=json.dumps(result_payload),
            structured_content=result_payload,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_events_replay(since_id: str | None = None) -> ToolResult:
        start_ms = time.monotonic()
        events = get_mcp_event_store().replay(since_event_id=since_id)
        result_payload: dict[str, Any] = {"events": events, "count": len(events)}
        elapsed = int((time.monotonic() - start_ms) * 1000)
        return tool_result_type(
            content=json.dumps(result_payload),
            structured_content=result_payload,
            meta={"execution_time_ms": elapsed},
        )

    return {
        "thegent_storage_get": thegent_storage_get,
        "thegent_storage_set": thegent_storage_set,
        "thegent_events_emit": thegent_events_emit,
        "thegent_events_replay": thegent_events_replay,
    }


def register_optional_tools(
    *,
    mcp: Any,
    log: Any,
    current_context: Callable[[], Any] = CurrentContext,
    tool_result_type: type[ToolResult] = ToolResult,
    import_module_fn: Callable[[str], Any] = importlib.import_module,
    register_storage_event_tools_fn: Callable[..., dict[str, Any]] = register_storage_event_tools,
) -> dict[str, Any]:
    """Register optional tool/resource blocks with debug-on-failure semantics."""

    exports: dict[str, Any] = {}

    try:
        sitback_mod = import_module_fn("thegent.mcp.tools.sitback")
        register_sitback = sitback_mod.register_sitback
        register_sitback(mcp)
    except Exception:
        log.debug("sitback not available; skipping sitback registration")

    try:
        register_modes = import_module_fn("thegent.mcp.tools.modes").register_modes
        register_modes(mcp)
    except Exception as e:
        log.debug("mode tools not available; skipping: %s", e)

    try:
        register_seed_tools = import_module_fn("thegent.mcp.tools.seeds").register_seed_tools
        register_seed_tools(mcp)
    except Exception as e:
        log.debug("seed tools not available; skipping: %s", e)

    try:
        elicitation_mod = import_module_fn("thegent.mcp.tools.elicitation")
        register_elicitation_tools = elicitation_mod.register_elicitation_tools
        register_elicitation_tools(mcp)

        pydantic_mod = import_module_fn("pydantic")
        BaseModel = pydantic_mod.BaseModel
        Field = pydantic_mod.Field

        class AgentConfig(BaseModel):
            name: str = Field(..., description="Unique name for the agent")
            timeout_secs: int = Field(90, description="Execution timeout in seconds")
            retry_count: int = Field(3, description="Number of retries on failure")

        @mcp.tool()
        async def thegent_configure_agent(ctx: Any = current_context()) -> str:
            result = await elicitation_mod.elicit_structured(ctx, "Configure the agent", AgentConfig)
            if result:
                return f"Agent configured: {result.name} (timeout={result.timeout_secs}s, retries={result.retry_count})"
            return "Agent configuration declined or cancelled."

        @mcp.tool()
        async def thegent_approve_deployment(project: str, ctx: Any = current_context()) -> str:
            result = await elicitation_mod.elicit_confirmation(ctx, f"Approve deployment for project: {project}?")
            if result is True:
                return f"Deployment for {project} APPROVED."
            if result is False:
                return f"Deployment for {project} DENIED."
            return "Approval request cancelled or unavailable."

        exports["thegent_configure_agent"] = thegent_configure_agent
        exports["thegent_approve_deployment"] = thegent_approve_deployment
    except Exception as e:
        log.debug("elicitation tools not available; skipping: %s", e)

    try:
        register_tool_pattern_tools = import_module_fn("thegent.mcp.tools.patterns").register_tool_pattern_tools
        register_tool_pattern_tools(mcp)
    except Exception as e:
        log.debug("tool pattern tools not available; skipping: %s", e)

    try:
        storage_mod = import_module_fn("thegent.mcp.storage")
        exports.update(
            register_storage_event_tools_fn(
                mcp=mcp,
                get_mcp_storage=storage_mod.get_mcp_storage,
                get_mcp_event_store=storage_mod.get_mcp_event_store,
                tool_result_type=tool_result_type,
            )
        )
        log.info(
            "storage/event tools registered: thegent_storage_get, thegent_storage_set, "
            "thegent_events_emit, thegent_events_replay"
        )
    except Exception as storage_tools_err:
        log.debug("storage/event tools not available; skipping: %s", storage_tools_err)

    return exports
