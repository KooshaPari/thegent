"""Utility commands for dex CLI.

Session management and utility commands.
Extracted from dex_main.py for maintainability.
"""

from __future__ import annotations

import typer
from rich.console import Console


console = Console()


def register_dex_utility_commands(app: typer.Typer) -> None:
    """Register utility commands with the app.

    Args:
        app: Typer app to register commands with
    """

    @app.command("ps")
    def dex_ps() -> None:
        """List running dex sessions."""
        # TODO: Implement session listing via agentapi++
        console.print("[yellow]Session listing not yet implemented[/yellow]")
        console.print("Use: agentapi ps")

    @app.command("logs")
    def dex_logs(
        session_id: str = typer.Argument(..., help="Session ID"),
        follow: bool = typer.Option(False, "-f", "--follow", help="Follow logs"),
    ) -> None:
        """View logs for a dex session."""
        console.print(f"[yellow]Logs for {session_id}[/yellow]")
        if follow:
            console.print("Following...")

    @app.command("status")
    def dex_status(
        session_id: str | None = typer.Argument(None, help="Session ID"),
    ) -> None:
        """Show status of dex sessions."""
        if session_id:
            console.print(f"[cyan]Status for session: {session_id}[/cyan]")
        else:
            console.print("[cyan]Overall dex status[/cyan]")
            # TODO: Query agentapi++ for status

    @app.command("resume")
    def dex_resume(
        session_id: str = typer.Argument(..., help="Session ID to resume"),
    ) -> None:
        """Resume a paused dex session."""
        console.print(f"[green]Resuming session: {session_id}[/green]")
        # TODO: Implement via agentapi++

    @app.command("fork")
    def dex_fork(
        session_id: str = typer.Argument(..., help="Session ID to fork"),
    ) -> None:
        """Fork a dex session."""
        console.print(f"[green]Forking session: {session_id}[/green]")
        # TODO: Implement via agentapi++

    @app.command("stop")
    def dex_stop(
        session_id: str = typer.Argument(..., help="Session ID to stop"),
        force: bool = typer.Option(False, "-f", "--force", help="Force stop"),
    ) -> None:
        """Stop a running dex session."""
        from thegent.dex_main import _resolve_native_codex
        from thegent.infra.shim_subprocess import run as shim_run

        args = ["stop", session_id]
        if force:
            args.append("--force")

        codex_path = _resolve_native_codex()
        if not codex_path:
            console.print("[red]Codex CLI not found[/red]")
            raise typer.Exit(1)

        result = shim_run([codex_path, *args], check=False)
        raise typer.Exit(result.returncode)

    @app.command("wait")
    def dex_wait(
        session_id: str = typer.Argument(..., help="Session ID to wait for"),
    ) -> None:
        """Wait for a dex session to complete."""
        console.print(f"[cyan]Waiting for session: {session_id}[/cyan]")
        # TODO: Implement via agentapi++

    @app.command("inspect")
    def dex_inspect(
        session_id: str = typer.Argument(..., help="Session ID to inspect"),
    ) -> None:
        """Inspect a dex session in detail."""
        console.print(f"[cyan]Inspecting session: {session_id}[/cyan]")
        # TODO: Implement via agentapi++

    @app.command("history")
    def dex_history(
        limit: int = typer.Option(20, "-n", "--limit", help="Number of entries"),
    ) -> None:
        """Show dex session history."""
        console.print(f"[cyan]Last {limit} sessions[/cyan]")
        # TODO: Query session history from agentapi++

    @app.command("doctor")
    def dex_doctor() -> None:
        """Run dex diagnostics."""
        from thegent.dex_main import _resolve_native_codex

        console.print("\n[bold cyan]Dex Doctor[/bold cyan]\n")

        # Check codex binary
        codex_path = _resolve_native_codex()
        if codex_path:
            console.print(f"[green]✓[/green] Codex found: {codex_path}")
        else:
            console.print("[red]✗[/red] Codex not found")

        # Check cliproxy
        import shutil

        if shutil.which("cliproxy") or shutil.which("cli-proxy-api-plus"):
            console.print("[green]✓[/green] cliproxy available")
        else:
            console.print("[yellow]![/yellow] cliproxy not found (optional)")

        console.print("\n[green]Doctor complete[/green]")

    @app.command("config")
    def dex_config(
        key: str | None = typer.Argument(None, help="Config key"),
        value: str | None = typer.Argument(None, help="Config value"),
    ) -> None:
        """View or edit dex configuration."""
        if key and value:
            console.print(f"[green]Setting {key} = {value}[/green]")
            # TODO: Implement config setting
        elif key:
            console.print(f"[cyan]{key}: (not set)[/cyan]")
        else:
            console.print("[cyan]Dex configuration[/cyan]")
            # TODO: Show all config

    _ = (
        dex_ps,
        dex_logs,
        dex_status,
        dex_resume,
        dex_fork,
        dex_stop,
        dex_wait,
        dex_inspect,
        dex_history,
        dex_doctor,
        dex_config,
    )


__all__ = [
    "register_dex_utility_commands",
]
