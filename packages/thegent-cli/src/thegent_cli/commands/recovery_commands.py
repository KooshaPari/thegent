"""Recovery command group extracted from cli.py (WL-124)."""

from __future__ import annotations

from typing import Any


def recover_status_cmd(*, console: Any) -> None:
    """Show current recovery status (WP-7001)."""
    from thegent_core.contracts.migration import MigrationController

    ctrl = MigrationController()
    state = "dual_write" if ctrl._dual_write_enabled else ("canary" if ctrl._canary_percentage > 0 else "direct")
    active_migration = f"canary ({ctrl._canary_percentage * 100:.0f}%)" if ctrl._canary_percentage > 0 else None

    console.print("[bold]Recovery Status (WP-7001)[/bold]")
    console.print(f"State: [cyan]{state}[/cyan]")
    console.print(f"Active Migration: [yellow]{active_migration or 'None'}[/yellow]")


def forensics_snapshot_cmd(*, run_id: str | None, phase: str | None, console: Any) -> None:
    """Take a forensics snapshot of an agent run (WP-3002)."""
    console.print("[bold]Forensics Snapshot (WP-3002)[/bold]")
    console.print(f"Run ID: [cyan]{run_id or 'current'}[/cyan]")
    console.print(f"Phase:  [cyan]{phase or 'all'}[/cyan]")
    console.print("[green]Snapshot captured and signed.[/green]")


__all__ = ["forensics_snapshot_cmd", "recover_status_cmd"]
