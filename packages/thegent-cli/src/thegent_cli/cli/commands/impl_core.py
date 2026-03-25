"""Thegent core run/bg/resume/loop implementation layer."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from thegent_core.config_provider import ConfigProvider

from thegent_core.config import ThegentSettings
from thegent_execution.execution import RunRegistry

__all__ = [
    "bg_impl",
    "loop_impl",
    "resume_impl",
    "run_impl",
]


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
    config_provider: ConfigProvider | None = None,
    tenant_id: str | None = None,
    previous_session_id: str | None = None,
    reasoning_effort: Literal["minimal", "low", "medium", "high", "xhigh"] | None = None,
    output_schema: str | None = None,
    image_paths: list[str] | None = None,
    audio_files: list[str] | None = None,
    google_grounding: bool = False,
) -> dict[str, Any]:
    import asyncio
    from thegent_cli.cli.services import run_execution_core_helpers
    from thegent_core.memory.memory_manager import MemoryManager

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
        impl_ns=sys.modules[__name__],
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
    config_provider: ConfigProvider | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    from thegent_cli.cli.services import run_execution_core_helpers

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
        impl_ns=sys.modules[__name__],
    )


def resume_impl(
    session_id: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> dict[str, Any]:
    from thegent_cli.cli.commands.impl import (
        _normalize_contract_string,
        _resolve_latest_session_id,
        _session_state_path,
    )
    from thegent_cli.cli.services import run_post_surface_helpers

    def _session_send_wrapper(sid: str, message: str) -> dict[str, Any]:
        success, response = session_send_impl(sid, message, msg_type="reprompt")
        return {"success": success, "response": response}

    return run_post_surface_helpers.resume_impl(
        session_id=session_id,
        prompt=prompt,
        skills=skills,
        resolve_latest_session_id=_resolve_latest_session_id,
        session_state_path=_session_state_path,
        normalize_contract_string=_normalize_contract_string,
        session_send_impl=_session_send_wrapper,
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
    from thegent_cli.cli.services import run_post_surface_helpers

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


# Re-export from session_impl for resume_impl
def session_send_impl(session_id: str, message: str, msg_type: str = "reprompt") -> tuple[bool, str]:
    from thegent_cli.cli.commands.session_control_impl import session_send_impl as _session_send_impl

    return _session_send_impl(session_id, message, msg_type=msg_type)
