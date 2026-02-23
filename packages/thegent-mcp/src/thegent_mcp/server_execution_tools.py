"""Execution-oriented MCP tool registration helpers."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, cast

from fastmcp import FastMCP
from fastmcp._vendor.docket_di import Depends
from fastmcp.server.dependencies import CurrentContext
from fastmcp.server.tasks.config import TaskConfig
from fastmcp.tools.tool import ToolResult


def register_execution_tools(
    *,
    mcp: FastMCP,
    server_tools_runtime: Any,
    error_result: Any,
    get_default_cwd: Any,
    get_default_owner: Any,
    resolve_cwd: Any,
    run_impl: Any,
    bg_impl: Any,
    session_contract_negotiate_impl: Any,
    write_session_control_file: Any,
    normalize_bg_routing: Any,
    build_route_request_payload: Any,
    settings_factory: Any,
    default_owner_tag: Any,
    resolve_cwd_elicitation: Any,
    resolve_owner_elicitation: Any,
    get_cached_elicitation: Any,
    cache_elicitation_response: Any,
    accepted_elicitation_type: Any,
    output_parser_schema_version: str,
    elicit_timeout_s: int,
    elicit_cwd_msg: str,
    elicit_owner_msg: str,
) -> tuple[object, ...]:
    """Register execution-related MCP tools and return stable handler bindings."""

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
        return server_tools_runtime.config_resolve_impl(
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
        return server_tools_runtime.negotiate_contract_impl(
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
        if not prompt:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit("What task should I perform?", response_type=str),
                    timeout=elicit_timeout_s,
                )
                if isinstance(elicitation, accepted_elicitation_type):
                    prompt = cast("str", elicitation.data)
                else:
                    return error_result("Prompt is required to run a task.", "Provide 'prompt' in tool call.")
            except TimeoutError:
                return error_result("Elicitation timed out (no prompt provided).", "Provide 'prompt' in tool call.")

        request_payload: dict[str, Any] = {
            "model": model,
            "provider_hint": provider,
            "policy": None,
            "route_contract": None,
        }
        if model and not agent:
            from thegent.models import resolve_route, resolve_route_contract

            settings = settings_factory()
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
                return error_result(
                    f"No route for model '{model}'.",
                    "Run: thegent list-models",
                )
            agent, model = resolved[0], resolved[1]
            if include_contract:
                route = resolve_route_contract(
                    model,
                    provider_hint=provider,
                    policy=cast(
                        "Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']",
                        policy,
                    ),
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
            from thegent.models import ModelCatalog, resolve_route, resolve_route_contract

            settings = settings_factory()
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
                return error_result(
                    f"Model '{model}' not available via provider '{agent}'.{suffix}",
                    "Run: thegent list-models" if not available else f"Available: {available}. Or: thegent list-models",
                )
            agent, model = resolved[0], resolved[1]
            if include_contract:
                route = resolve_route_contract(
                    model,
                    provider_hint=agent,
                    policy=cast(
                        "Literal['prefer_direct', 'prefer_proxy', 'failover', 'round_robin', 'cheapest']",
                        policy,
                    ),
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
            return error_result("Provide agent or model for routing.", "Run: thegent list-agents")

        await ctx.info(f"thegent_run agent={agent} cd={cd} timeout={timeout}")
        cd_path = Path(cd) if cd else default_cwd
        cwd = resolve_cwd(cd_path)
        if cwd is None:
            cached_response = get_cached_elicitation(elicit_cwd_msg, str)
            if cached_response is not None:
                cwd, status = resolve_cwd_elicitation(cached_response)
                if status == "declined":
                    return error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                if status == "cancelled":
                    return error_result("Elicitation cancelled.", "Retry with explicit params")
            else:
                try:
                    elicitation = await asyncio.wait_for(
                        ctx.elicit(elicit_cwd_msg, response_type=str),
                        timeout=elicit_timeout_s,
                    )
                    cache_elicitation_response(elicit_cwd_msg, str, elicitation)
                    cwd, status = resolve_cwd_elicitation(elicitation)
                    if status == "declined":
                        return error_result(
                            "User declined to provide working directory.",
                            "Provide cd=/path in tool call",
                        )
                    if status == "cancelled":
                        return error_result("Elicitation cancelled.", "Retry with explicit params")
                    if status == "ambiguous":
                        return error_result("Ambiguous cwd.", "Provide cd=/path explicitly")
                except TimeoutError:
                    return error_result(
                        "Elicitation timed out (no response from client).",
                        "Provide cd=/path in tool call",
                    )
        cd_path = cwd

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
                payload["extraction_schema_version"] = output_parser_schema_version
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
        cwd = resolve_cwd(cd_path)
        if cwd is None:
            return error_result("CWD not found.", "Provide cd=/path or run from project root")

        start_time = time.perf_counter()

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
            await ctx.report_progress(progress=0, total=100)

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
        settings = settings_factory()
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
        settings = settings_factory()
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
        """
        if not prompt:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit("What background task should I perform?", response_type=str),
                    timeout=elicit_timeout_s,
                )
                if isinstance(elicitation, accepted_elicitation_type):
                    prompt = cast("str", elicitation.data)
                else:
                    return error_result("Prompt is required for background task.", "Provide 'prompt' in tool call.")
            except TimeoutError:
                return error_result("Elicitation timed out (no prompt provided).", "Provide 'prompt' in tool call.")

        await ctx.info(f"thegent_bg agent={agent} cd={cd} owner={owner}")
        cd_path = Path(cd) if cd else default_cwd
        cwd = resolve_cwd(cast("Path | None", cd_path))
        elicited_cwd = False
        if cwd is None:
            cached_response = get_cached_elicitation(elicit_cwd_msg, str)
            if cached_response is not None:
                cwd, status = resolve_cwd_elicitation(cached_response)
                if status is None:
                    elicited_cwd = True
                elif status == "declined":
                    return error_result("User declined to provide working directory.", "Provide cd=/path in tool call")
                elif status == "cancelled":
                    return error_result("Elicitation cancelled.", "Retry with explicit params")
            else:
                try:
                    elicitation = await asyncio.wait_for(
                        ctx.elicit(elicit_cwd_msg, response_type=str),
                        timeout=elicit_timeout_s,
                    )
                    cache_elicitation_response(elicit_cwd_msg, str, elicitation)
                    cwd, status = resolve_cwd_elicitation(elicitation)
                    if status is None:
                        elicited_cwd = True
                    elif status == "declined":
                        return error_result(
                            "User declined to provide working directory.",
                            "Provide cd=/path in tool call",
                        )
                    elif status == "cancelled":
                        return error_result("Elicitation cancelled.", "Retry with explicit params")
                    elif status == "ambiguous":
                        return error_result("Ambiguous cwd.", "Provide cd=/path explicitly")
                except TimeoutError:
                    return error_result(
                        "Elicitation timed out (no response from client).",
                        "Provide cd=/path in tool call",
                    )
        cd_path = cwd
        route_contract: dict[str, Any] | None = None
        requested_model = model
        requested_provider = provider or agent
        requested_policy, route_lookup_policy, routing_for_child, failover = normalize_bg_routing(
            routing=routing,
            default_routing=settings_factory().default_routing,
            failover=failover,
        )

        owner_tag = owner or default_owner
        if owner_tag is None and elicited_cwd:
            try:
                elicitation = await asyncio.wait_for(
                    ctx.elicit(elicit_owner_msg, response_type=str),
                    timeout=elicit_timeout_s,
                )
            except TimeoutError:
                owner_tag = default_owner_tag(cwd)
            else:
                owner_tag, status = resolve_owner_elicitation(
                    elicitation,
                    default_owner_tag=default_owner_tag(cwd),
                )
                if status == "cancelled":
                    return error_result("Elicitation cancelled.", "Retry with explicit params")
        elif owner_tag is None:
            owner_tag = default_owner_tag(cwd)

        if include_contract and model:
            try:
                from thegent.models import resolve_route_contract
                from thegent.models import route_contract as catalog_route_contract

                contract = resolve_route_contract(
                    model,
                    provider_hint=requested_provider or None,
                    policy=cast(
                        "Literal['prefer_direct','prefer_proxy','failover','round_robin','cheapest']",
                        route_lookup_policy,
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
        settings = settings_factory()
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
                return error_result(res["error"], res.get("remediation", ""), extra=res)
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
            return error_result(res["error"], res.get("remediation", ""), extra=res)
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

    return (
        thegent_config_resolve,
        thegent_negotiate_contract,
        thegent_run,
        thegent_loop,
        thegent_loop_takeover,
        thegent_loop_stop,
        thegent_bg,
        thegent_free,
        thegent_flash,
    )
