"""Core runner implementations: run_impl, bg_impl, resume_impl, loop_impl, _apply_pareto_routing.

These large execution engine functions are extracted from impl.py to keep that
module under the 400-line limit. They are re-exported by impl.py for backward compatibility.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

_log = logging.getLogger(__name__)


from thegent.config import ThegentSettings
from thegent.cli.services import run_model_helpers
from thegent.cli.services import run_post_surface_helpers
from thegent.cli.commands.session_meta_impl import (
    _resolve_latest_session_id,
    _session_state_path,
    _normalize_contract_string,
)
from thegent.cli.commands.session_control_impl import session_send_impl
from thegent.execution import RunRegistry

if TYPE_CHECKING:
    from thegent.config_provider import ConfigProvider

# Constants from impl.py that are referenced by the extracted functions
SECONDS_PER_TOOL_CALL = 2.3
_CONTINUATION_TAIL_CHARS = 8000
_CONTINUATION_STDERR_CHARS = 2000
_CONTINUATION_MULTI_HOP_TOTAL_CAP = 12000
_LOG_FOLLOW_POLL_SECONDS = 0.5

def _apply_pareto_routing(
    agent: str | None,
    model: str | None,
    routing: str | None,
    include_contract: bool,
    route_contract: dict[str, Any] | None,
    route_request: dict[str, Any] | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, dict[str, Any] | None]:
    """Apply pareto routing when no explicit agent/model is provided."""
    if routing != "pareto" or agent is not None or model is not None:
        return agent, model, route_contract, route_request

    try:
        from thegent.models.catalog import _get_catalog
        from thegent.utils.routing_impl.pareto_router import QUALITY_PROXY, ParetoRouter, RouteCandidate

        catalog = _get_catalog()
        candidates: list[RouteCandidate] = []
        for routes in catalog.values():
            for r in routes:
                quality = QUALITY_PROXY.get(r.model_alias, 0.5)
                candidates.append(
                    RouteCandidate(
                        model=r.model_alias,
                        provider=r.provider,
                        cost_per_1k=r.cost_weight,
                        quality_score=quality,
                    )
                )
        if not candidates:
            _log.warning("Pareto router: no candidates from catalog; fallback to antigravity/gemini-3-flash")
            return "antigravity", "gemini-3-flash", route_contract, route_request

        selected = ParetoRouter().select(candidates)
        _log.info(
            "Pareto router: selected %s/%s (quality=%.2f, cost=%.2f)",
            selected.provider,
            selected.model,
            selected.quality_score,
            selected.cost_per_1k,
        )

        updated_contract = route_contract
        updated_request = route_request
        if include_contract:
            updated_contract = dict(route_contract or {})
            updated_contract.update(
                {
                    "provider": selected.provider,
                    "model_alias": selected.model,
                    "backend_type": "direct",
                    "routing_policy": "pareto",
                }
            )
            updated_request = dict(route_request or {})
            updated_request.update(
                {
                    "requested_model": "pareto",
                    "policy": "pareto",
                    "resolved_agent": selected.provider,
                    "resolved_model_alias": selected.model,
                }
            )

        return selected.provider, selected.model, updated_contract, updated_request

    except Exception as _pareto_err:
        _log.warning("Pareto router error: %s; fallback to antigravity/gemini-3-flash", _pareto_err)
        return "antigravity", "gemini-3-flash", route_contract, route_request


_validate_explicit_ollama_provider = run_model_helpers.validate_explicit_ollama_provider


def run_impl(
    agent: str | None,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int | None = None,
    full: bool = False,
    live: bool = True,
    model: str | None = None,
    provider: str | None = None,
    run_id: str | None = None,
    owner: str | None = None,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, Any] | None = None,
    lane: str = "standard",
    confidence: float | None = None,
    override_reason: str | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    correlation_id: str | None = None,
    speculative: bool = False,
    arbitration: str | None = None,
    routing: str | None = None,
    enable_search: bool = False,
    debug: bool = False,
    task_id: str | None = None,
    shadow: bool = False,
    lock: list[str] | None = None,
    remote: str | None = None,
    config_provider: "ConfigProvider | None" = None,
    tenant_id: str | None = None,
    previous_session_id: str | None = None,
    reasoning_effort: Literal["minimal", "low", "medium", "high", "xhigh"] | None = None,
    output_schema: str | None = None,
    image_paths: list[str] | None = None,
    audio_files: list[str] | None = None,
    google_grounding: bool = False,
) -> dict[str, Any]:
    import asyncio
    from thegent.cli.services import run_execution_core_helpers
    from thegent.memory.memory_manager import MemoryManager

    # Initialize memory manager (no-op if API key not set)
    _mem_mgr = MemoryManager()

    # Load agent context before run
    if _mem_mgr.enabled:
        asyncio.run(_mem_mgr.load_context(agent or "default"))

    # Execute the core run
    result = run_execution_core_helpers.run_impl_core(
        agent=agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        live=live,
        model=model,
        provider=provider,
        run_id=run_id,
        owner=owner,
        include_contract=include_contract,
        route_contract=route_contract,
        route_request=route_request,
        lane=lane,
        confidence=confidence,
        override_reason=override_reason,
        contract_version=contract_version,
        domain=domain,
        idempotency_token=idempotency_token,
        correlation_id=correlation_id,
        speculative=speculative,
        arbitration=arbitration,
        routing=routing,
        enable_search=enable_search,
        debug=debug,
        task_id=task_id,
        shadow=shadow,
        lock=lock,
        remote=remote,
        config_provider=config_provider,
        tenant_id=tenant_id,
        previous_session_id=previous_session_id,
        reasoning_effort=reasoning_effort,
        output_schema=output_schema,
        image_paths=image_paths,
        audio_files=audio_files,
        google_grounding=google_grounding,
        impl_ns=sys.modules.get("thegent.cli.commands.impl", sys.modules[__name__]),
    )

    # Save discoveries after successful run
    if _mem_mgr.enabled and result.get("exit_code") == 0:
        run_id_str = result.get("run_id", "unknown")
        summary = f"Agent {agent}: completed run {run_id_str}"
        asyncio.run(_mem_mgr.save_discovery(agent or "default", summary))

    return result


def bg_impl(
    *,
    agent: str | None,
    prompt: str,
    cd: Path | None,
    mode: str = "write",
    timeout: int = 90,
    full: bool = False,
    droid: str | None = None,
    model: str | None = None,
    provider: str | None = None,
    owner: str | None = None,
    continue_from: str | None = None,
    continuation_include_stderr: bool = False,
    include_contract: bool = False,
    route_contract: dict[str, Any] | None = None,
    route_request: dict[str, str] | None = None,
    routing: str | None = None,
    failover: bool = False,
    run_id: str | None = None,
    lane: str | None = None,
    confidence: float | None = None,
    contract_version: str | None = None,
    domain: str | None = None,
    idempotency_token: str | None = None,
    speculative: bool = False,
    arbitration: str | None = None,
    override_reason: str | None = None,
    debug: bool = False,
    task_id: str | None = None,
    remote: str | None = None,
    image_paths: list[str] | None = None,
    config_provider: "ConfigProvider | None" = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    from thegent.cli.services import run_execution_core_helpers

    return run_execution_core_helpers.bg_impl_core(
        agent=agent,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=full,
        droid=droid,
        model=model,
        provider=provider,
        owner=owner,
        continue_from=continue_from,
        continuation_include_stderr=continuation_include_stderr,
        include_contract=include_contract,
        route_contract=route_contract,
        route_request=route_request,
        routing=routing,
        failover=failover,
        run_id=run_id,
        lane=lane,
        confidence=confidence,
        contract_version=contract_version,
        domain=domain,
        idempotency_token=idempotency_token,
        speculative=speculative,
        arbitration=arbitration,
        override_reason=override_reason,
        debug=debug,
        task_id=task_id,
        remote=remote,
        image_paths=image_paths,
        config_provider=config_provider,
        tenant_id=tenant_id,
        impl_ns=sys.modules.get("thegent.cli.commands.impl", sys.modules[__name__]),
    )


def resume_impl(
    session_id: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> dict[str, Any]:
    return run_post_surface_helpers.resume_impl(
        session_id=session_id,
        prompt=prompt,
        skills=skills,
        resolve_latest_session_id=_resolve_latest_session_id,
        session_state_path=_session_state_path,
        normalize_contract_string=_normalize_contract_string,
        session_send_impl=lambda sid, message: session_send_impl(sid, message, msg_type="reprompt"),
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
    )


def loop_impl(
    agent: str = "cursor",
    prompt: str = "",
    todo_spec: str = "",
    checker: str = "antigravity",
    mode: str = "soft",
    cd: Path | None = None,
    on_worker_output: Any = None,
    on_progress: Any = None,
) -> dict[str, Any]:
    return run_post_surface_helpers.loop_impl(
        agent=agent,
        prompt=prompt,
        todo_spec=todo_spec,
        checker=checker,
        mode=mode,
        cd=cd,
        on_worker_output=on_worker_output,
        on_progress=on_progress,
        bg_impl=bg_impl,
        settings_factory=ThegentSettings,
    )


list_agents_impl = run_post_surface_helpers.list_agents_impl


__all__ = [
    "_apply_pareto_routing",
    "bg_impl",
    "loop_impl",
    "resume_impl",
    "run_impl",
]
