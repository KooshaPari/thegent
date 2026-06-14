"""Main CLI application entry point.

This module provides the main Typer application that serves as the
entry point for the thegent CLI.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="thegent - Unified agent orchestration CLI for Factory skills, droids, and multi-agent workflows."
)


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """Main callback for the thegent CLI."""
    if version:
        typer.echo("thegent version 0.1.0")
        raise typer.Exit()


@app.command("run", help="Run an agent with the given prompt.")
def run_cmd(
    prompt: str = typer.Argument(..., help="The prompt to send to the agent"),
    model: str = typer.Option("gpt-4", "--model", "-M", help="Model to use"),
    provider: str = typer.Option("openai", "--provider", "-P", help="Provider to use"),
    cd: str | None = typer.Option(None, "--cd", help="Working directory"),
) -> None:
    """Run an agent command."""
    typer.echo(f"Running with model={model}, provider={provider}")


@app.command("bg", help="Run an agent in the background.")
def bg_cmd(
    prompt: str = typer.Argument(..., help="The prompt to send to the agent"),
    cd: str | None = typer.Option(None, "--cd", help="Working directory"),
    owner: str | None = typer.Option(None, "--owner", help="Owner tag"),
) -> None:
    """Run an agent in background mode."""
    typer.echo("Starting background session...")


@app.command("status", help="Show status of a session.")
def status_cmd(
    session_id: str = typer.Argument(..., help="Session ID to check"),
) -> None:
    """Show session status."""
    typer.echo(f"Status for session: {session_id}")


@app.command("stop", help="Stop a running session.")
def stop_cmd(
    session_id: str = typer.Argument(..., help="Session ID to stop"),
    force: bool = typer.Option(False, "--force", "-f", help="Force kill"),
) -> None:
    """Stop a session."""
    typer.echo(f"Stopping session: {session_id}")


@app.command("logs", help="Show logs for a session.")
def logs_cmd(
    session_id: str = typer.Argument(..., help="Session ID"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int = typer.Option(20, "--tail", "-n", help="Number of lines to show"),
) -> None:
    """Show session logs."""
    typer.echo(f"Showing logs for session: {session_id}")


# Import sub-apps
from thegent.cli.apps import govern, phench


@app.command("govern", help="Governance operations.")
def govern_cmd() -> None:
    """Governance operations."""
    govern.app()


@app.command("phench", help="Phenotyperench operations.")
def phench_cmd() -> None:
    """Phenotyperench operations."""
    phench.app()


if __name__ == "__main__":
    app()
