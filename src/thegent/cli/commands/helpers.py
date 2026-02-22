"""Shared helper primitives extracted from cli.py for WL-138 decomposition."""

from __future__ import annotations

from typing import Any, cast

import typer

from thegent.config import ThegentSettings
from thegent.execution import RunRegistry


__all__ = ["_safe_dict", "_safe_list", "_resolve_run_id", "_resolve_session_id"]


def _safe_dict(val: object) -> dict[str, Any]:
    """Return val as dict[str, Any], or empty dict if not a dict."""
    return cast("dict[str, Any]", val) if isinstance(val, dict) else {}


def _safe_list(val: object) -> list[Any]:
    """Return val as list[Any], or empty list if not a list."""
    return cast("list[Any]", val) if isinstance(val, list) else []


def _resolve_run_id(run_id: str | None, console: Any) -> str:
    """Resolve run_id, defaulting to latest if None."""
    if run_id:
        return run_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_run_id()
    if not latest:
        console.print("[red]No run ID provided and no previous runs found.[/red]")
        raise typer.Exit(1)
    return latest


def _resolve_session_id(session_id: str | None, console: Any) -> str:
    """Resolve session_id, defaulting to latest if None."""
    if session_id:
        return session_id
    settings = ThegentSettings()
    registry = RunRegistry(settings.session_dir)
    latest = registry.get_latest_session_id()
    if not latest:
        console.print("[red]No session ID provided and no previous sessions found.[/red]")
        raise typer.Exit(1)
    return latest
