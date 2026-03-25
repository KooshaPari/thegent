"""Thegent CLI model/agent commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _normalize_output_format,
    _resolve_cwd,
    _resolve_droids_dir,
    console,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)
from thegent.cli.commands.model_cmds_agents_helpers import render_agents_table, render_droids_table
from thegent.cli.commands.model_cmds_catalog_helpers import (
    emit_by_model_view,
    emit_contract_view,
    provider_sequence,
    run_provider_listings,
)
from thegent.cli.commands.model_cmds_metrics_helpers import (
    build_index_data,
    collect_metrics_rows,
    emit_cost_values_output,
    emit_index_output,
    emit_metrics_output,
    flatten_cost_values,
)
from thegent.cli.commands.model_cmds_rules import (
    _list_antigravity_models,
    _list_claude_models,
    _list_codex_models,
    _list_copilot_models,
    _list_cursor_api_models,
    _list_gemini_models,
    _list_glm_models,
    _list_kiro_models,
    _list_minimax_models,
)
from thegent.cli.commands.model_cmds_route_helpers import build_available_routes, build_resolved_route


def list_agents_cmd() -> None:
    """List available agents."""
    agents = list_agent_names()
    render_agents_table(agents, resolve_agent=resolve_agent, console=console)


def list_droids_cmd(cd: Path | None = None) -> None:
    """List available droids."""
    settings = ThegentSettings()
    resolved_cd = _resolve_cwd(cd)
    droids_dir = _resolve_droids_dir(resolved_cd, settings)
    droids = list_droid_names(droids_dir)
    if not droids:
        console.print("[yellow]No droids found.[/yellow]")
        return
    render_droids_table(droids, console=console)


def list_models_cmd(
    provider: str | None = None,
    by_model: bool = False,
    refresh: bool = False,
    include_contract: bool = False,
) -> None:
    """List available models (scraped from CLIs/config)."""
    if include_contract:
        emit_contract_view(provider=provider, refresh=refresh, console=console)
        return

    if by_model:
        emit_by_model_view(refresh=refresh, console=console)
        return
    providers = provider_sequence(provider)
    run_provider_listings(
        providers,
        handlers={
            "minimax": _list_minimax_models,
            "glm": _list_glm_models,
            "cursor": _list_cursor_api_models,
            "gemini": _list_gemini_models,
            "copilot": _list_copilot_models,
            "interactive_agent": _list_claude_models,
            "claude": _list_claude_models,
            "headless_agent": _list_codex_models,
            "codex": _list_codex_models,
            "antigravity": _list_antigravity_models,
            "kiro": _list_kiro_models,
        },
    )


def speed_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show speed index (0-1, higher=faster) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
    falls back to Route.latency_ms.
    """
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
    indices = get_model_provider_speed_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Speed Index (0-1, higher=faster)",
        value_label="Speed Index",
        console=console,
    )


def quality_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show quality index (0-1) for all models.

    Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
    falls back to Route.accuracy_score.
    """
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )

    if no_cache:
        invalidate_quality_index_cache()
    indices = get_model_provider_quality_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Quality Index (0-1, higher=better)",
        value_label="Quality Index",
        console=console,
    )


def metrics_cmd(
    format: str | None = None,
    no_cache: bool = False,
    limit: int = 50,
) -> None:
    """Show cost, speed, and quality indices for all model-provider pairs (unified view)."""
    from thegent.models.cost_values import get_model_provider_costs
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
        invalidate_quality_index_cache()
    costs = get_model_provider_costs()
    speed = get_model_provider_speed_indices(use_cache=not no_cache)
    quality = get_model_provider_quality_indices(use_cache=not no_cache)

    rows = collect_metrics_rows(costs=costs, speed=speed, quality=quality, limit=limit)

    fmt = _normalize_output_format(format)
    emit_metrics_output(rows=rows, limit=limit, fmt=fmt, console=console)


def cost_values_cmd(format: str | None = None) -> None:
    """Show cost values ($/1k tokens) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.
    """
    from thegent.models.cost_values import get_model_provider_costs

    costs = get_model_provider_costs()
    data = flatten_cost_values(costs)

    fmt = _normalize_output_format(format)
    emit_cost_values_output(data=data, fmt=fmt, console=console)


def resolve_model_route_cmd(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
    quality_floor: float = 0.0,
    lane: str | None = None,
) -> None:
    """Resolve a model to a preferred route and emit contract-style output."""
    from thegent.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )
    from thegent.models.quality_values import get_model_provider_quality_indices
    from thegent.models.speed_values import get_model_provider_speed_indices

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        console.print(
            "[red]Invalid routing policy. Use prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto.[/red]"
        )
        raise typer.Exit(1)

    normalized = normalize_model_id(model)
    route = resolve_route_contract(
        model,
        provider_hint=provider,
        policy=policy_value,
    )
    speed_map = get_model_provider_speed_indices().get(normalized, {})
    quality_map = get_model_provider_quality_indices().get(normalized, {})
    routes = sorted(
        ModelCatalog.routes_for(model),
        key=lambda r: (r.provider, r.priority, r.model_alias),
    )
    available_routes = build_available_routes(routes=routes, speed_map=speed_map, quality_map=quality_map)

    payload: dict[str, Any] = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is None:
        if available_routes:
            console.print("[yellow]No route matched the provided hint. Showing available routes below.[/yellow]")
        else:
            console.print(f"[red]No route for model '{model}'.[/red]")
        console.print_json(data=payload)
        raise typer.Exit(1)

    resolved = build_resolved_route(route=route, speed_map=speed_map, quality_map=quality_map)
    payload["resolved_route"] = resolved
    console.print_json(data=payload)
