"""Helpers for session pressure warnings."""

from __future__ import annotations

from typing import Any


def warn_if_session_count_high(*, settings: Any, console: Any) -> None:
    """Print memory warning when running sessions exceed threshold."""
    thresh = getattr(settings, "session_warn_threshold", 5)
    if not isinstance(thresh, int) or thresh <= 0:
        return

    from thegent.cli.commands.impl import ps_impl

    sessions = ps_impl(all=True)
    running = sum(1 for s in sessions if (s.get("status") or "").lower() == "running")
    if running >= thresh:
        console.print(
            f"[yellow]Tip: {running} active session(s) detected. Each spawns LSP/MCP processes (~1–2 GB).[/yellow]"
        )
        console.print(
            "[dim]Run 'thegent mcp prune --force' to free memory, or 'thegent mcp spotlight-exclude' on macOS.[/dim]"
        )
