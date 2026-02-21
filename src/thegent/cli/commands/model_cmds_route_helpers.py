"""Route payload helpers for model_cmds."""
from __future__ import annotations

from typing import Any


def build_available_routes(
    *,
    routes: list[Any],
    speed_map: dict[str, float],
    quality_map: dict[str, float],
) -> list[dict[str, Any]]:
    """Serialize available routes for CLI contract output."""
    available_routes: list[dict[str, Any]] = []
    for route in routes:
        row: dict[str, Any] = {
            "provider": route.provider,
            "backend_type": route.backend_type,
            "model_alias": route.model_alias,
            "priority": route.priority,
        }
        if route.provider in speed_map:
            row["speed_index"] = round(speed_map[route.provider], 4)
        if route.provider in quality_map:
            row["quality_index"] = round(quality_map[route.provider], 4)
        available_routes.append(row)
    return available_routes


def build_resolved_route(
    *,
    route: Any,
    speed_map: dict[str, float],
    quality_map: dict[str, float],
) -> dict[str, Any]:
    """Serialize selected route for CLI contract output."""
    resolved: dict[str, Any] = {
        "provider": route.provider,
        "model_alias": route.model_alias,
        "backend_type": route.backend_type,
        "priority": route.priority,
        "schema_version": route.schema_version,
    }
    if route.provider in speed_map:
        resolved["speed_index"] = round(speed_map[route.provider], 4)
    if route.provider in quality_map:
        resolved["quality_index"] = round(quality_map[route.provider], 4)
    return resolved
