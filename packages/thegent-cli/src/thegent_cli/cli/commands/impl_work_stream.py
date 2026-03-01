"""Thegent work stream and planning implementation layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = [
    "continuity_snapshot_impl",
    "do_next_impl",
    "harness_interact_impl",
    "harness_list_actions_impl",
    "harness_register_host_impl",
    "inbox_list_impl",
    "inbox_wait_impl",
    "incorporate_impl",
    "list_agents_impl",
    "list_droids_impl",
    "list_models_impl",
    "plan_analyze_impl",
    "retry_impl",
    "spawn_next_impl",
    "wait_next_impl",
    "work_stream_claim_impl",
    "work_stream_complete_impl",
]


def list_agents_impl() -> list[str]:
    from thegent_cli.cli.services import run_post_surface_helpers
    return run_post_surface_helpers.list_agents_impl()


def list_droids_impl(cd: Any = None) -> list[str]:
    from thegent_cli.cli.commands.impl import _resolve_cwd, _resolve_droids_dir
    from thegent_agents.agents import list_droid_names
    from thegent_core.config import ThegentSettings
    from thegent_cli.cli.services import run_post_surface_helpers

    return run_post_surface_helpers.list_droids_impl(
        cd=cd,
        resolve_cwd=_resolve_cwd,
        resolve_droids_dir=_resolve_droids_dir,
        list_droid_names_fn=list_droid_names,
        settings_factory=ThegentSettings,
    )


def list_models_impl(
    provider: str | None = None,
    use_scraped: bool = True,
    refresh: bool = False,
    include_contract: bool = False,
    by_model: bool = False,
) -> dict[str, Any]:
    from thegent_core.config import ThegentSettings
    from thegent_cli.cli.services import run_post_surface_helpers

    return run_post_surface_helpers.list_models_impl(
        provider=provider,
        use_scraped=use_scraped,
        refresh=refresh,
        include_contract=include_contract,
        by_model=by_model,
        settings_factory=ThegentSettings,
    )


def do_next_impl(cd: Path | None = None, limit: int = 5) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.do_next_impl(cd=cd, limit=limit)


def wait_next_impl(
    *,
    cd: Path | None = None,
    timeout: int = 30,
    poll_interval: float = 0.5,
) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.wait_next_impl(cd=cd, timeout=timeout, poll_interval=poll_interval)


def spawn_next_impl(
    cd: Path | None = None,
    *,
    agent: str = "free",
    limit: int = 10,
    timeout: int | None = None,
    lane: str = "critical",
    override_reason: str = "manual-next-step",
    claim: bool = True,
) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.spawn_next_impl(
        cd=cd, agent=agent, limit=limit, timeout=timeout, lane=lane, override_reason=override_reason, claim=claim
    )


def work_stream_claim_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def work_stream_complete_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def incorporate_impl(cd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.incorporate_impl(cd=cd, dry_run=dry_run)


def plan_analyze_impl(
    cd: Path | None = None,
    pert: bool = False,
    resources: bool = False,
    continuity: bool = False,
) -> dict[str, Any]:
    from thegent_cli.cli.commands.impl import _resolve_cwd, _parse_dag_full
    from thegent_cli.cli.services import run_post_surface_helpers

    return run_post_surface_helpers.plan_analyze_impl(
        cd=cd,
        pert=pert,
        resources=resources,
        continuity=continuity,
        resolve_cwd=_resolve_cwd,
        parse_dag_full=_parse_dag_full,
    )


def retry_impl(
    run_id: str,
    agent_override: str | None = None,
    failover: bool = False,
    cd: Path | None = None,
    override_reason: str | None = None,
) -> dict[str, Any]:
    from thegent_cli.cli.commands.impl import _resolve_cwd
    from thegent_agents.agents import get_fallback_agents
    from thegent_core.config import ThegentSettings
    from thegent_execution.execution import RunRegistry
    from thegent_cli.cli.services import run_post_surface_helpers
    from thegent_cli.cli.commands.impl_core import bg_impl

    return run_post_surface_helpers.retry_impl(
        run_id=run_id,
        agent_override=agent_override,
        failover=failover,
        cd=cd,
        override_reason=override_reason,
        resolve_cwd=_resolve_cwd,
        bg_impl=bg_impl,
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
        get_fallback_agents_fn=get_fallback_agents,
    )


def inbox_wait_impl(timeout: int | None = None) -> dict[str, Any]:
    from thegent_core.config import ThegentSettings
    from thegent_cli.cli.services import run_post_surface_helpers
    return run_post_surface_helpers.inbox_wait_impl(timeout=timeout, settings_factory=ThegentSettings)


def inbox_list_impl(
    owner: str | None = None,
    agent: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    sources: tuple[str, ...] = ("registry", "escalation"),
    limit: int = 50,
) -> list[dict[str, Any]]:
    from thegent_core.config import ThegentSettings
    from thegent_execution.execution import RunRegistry
    from thegent_cli.cli.services import run_post_surface_helpers

    return run_post_surface_helpers.inbox_list_impl(
        owner=owner,
        agent=agent,
        event_type=event_type,
        status=status,
        sources=sources,
        limit=limit,
        settings_factory=ThegentSettings,
        run_registry_cls=RunRegistry,
    )


def continuity_snapshot_impl(
    owner: str,
    run_ids: list[str],
    *,
    state_summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    from thegent_cli.cli.services import work_stream_orchestration
    return work_stream_orchestration.continuity_snapshot_impl(
        owner=owner, run_ids=run_ids, state_summary=state_summary, next_steps=next_steps
    )


def harness_interact_impl(
    *,
    harness: str,
    action: str,
    host_id: str | None = None,
    prompt: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    from thegent_cli.cli.services import run_post_surface_helpers
    return run_post_surface_helpers.harness_interact_impl(
        harness=harness,
        action=action,
        host_id=host_id,
        prompt=prompt,
        session_id=session_id,
    )


def harness_list_actions_impl() -> dict[str, Any]:
    from thegent_cli.cli.services import run_post_surface_helpers
    return run_post_surface_helpers.harness_list_actions_impl()


def harness_register_host_impl() -> dict[str, Any]:
    from thegent_cli.cli.services import run_post_surface_helpers
    return run_post_surface_helpers.harness_register_host_impl()
