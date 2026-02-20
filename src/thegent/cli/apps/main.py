"""Thegent 3.0: Unified Agent Orchestration Entry Point.
Consolidates all legacy command sprawl into a clean, logical hierarchy.
"""

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(
    name="thegent",
    help="Unified Agent Orchestration OS - The Optimal System",
    no_args_is_help=True,
    add_completion=True,
)

# Modular Stream Registrations
from thegent.cli.apps import audit, isolation, plan, run, sync, sys, team
from thegent.mesh.main import app as mesh_app

app.add_typer(run.app, name="run", help="Execution: Agent tasks, background runs, and history.")
app.add_typer(sync.app, name="sync", help="Synchronization: Rules, DAG, work-stream, and catalog.")
app.add_typer(audit.app, name="audit", help="Integrity: System health, security, and planning risk.")
app.add_typer(plan.app, name="plan", help="Roadmap: DAG tasks, work streams, and initiatives.")
app.add_typer(team.app, name="team", help="Swarm: Coordination, teammates, and hierarchy.")
app.add_typer(sys.app, name="sys", help="System: Setup, MCP, LSP, and configuration.")
app.add_typer(isolation.app, name="isolation", help="Isolation: Multi-tenancy, L1/L2 nesting, and SHM.")
app.add_typer(mesh_app, name="mesh", help="Mesh: Local agent coordination, status, and discovery.")


# Top-level Shortcuts
@app.command("do", help="Quick-run a prompt with the default agent.")
def quick_do(prompt: str = typer.Argument(..., help="Prompt to execute")):
    from thegent.cli.apps.run import run_agent

    run_agent(prompt=prompt)


@app.command("ps", help="List active background sessions (shortcut for `thegent run ps`).")
def quick_ps(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions, not just current owner"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner tag"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|md)"),
    include_contract: bool = typer.Option(False, "--include-contract", help="Include routing contract metadata"),
):
    from thegent.cli.apps.run import run_ps

    run_ps(
        all_sessions=all_sessions,
        owner=owner,
        format=format,
        include_contract=include_contract,
    )


@app.command("install", help="Compatibility install command (legacy alias).")
def install_compat(
    target: str = typer.Option(
        "all", "--target", "-t", help="Install target (all, codex, droid, cursor, harness, etc.)"
    ),
    mode: str = typer.Option("smart", "--mode", "-m", help="Install mode: smart, overwrite, skip, undo"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print detailed install output"),
    url: str | None = typer.Option(None, "--url", help="MCP URL override"),
    install_service: bool = typer.Option(False, "--install-service", help="Install service hooks where supported"),
) -> None:
    """Run installer flows previously exposed as `thegent install`."""
    try:
        from thegent.install import run_install
    except ImportError as exc:
        console.print(f"[red]Install subsystem unavailable: {exc}[/red]")
        raise typer.Exit(1) from exc

    run_install(
        target=target,
        mode=mode,
        dry_run=dry_run,
        verbose=verbose,
        url=url,
        install_service=install_service,
    )


@app.callback(invoke_without_command=True)
def main_welcome(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]Thegent 3.0 (Optimal)[/bold cyan]\n"
                "[dim]The Optimized Agent Orchestration System[/dim]\n\n"
                "Key Streams:\n"
                "  [green]thegent run[/green]       Execute agent tasks\n"
                "  [green]thegent sync[/green]      Synchronize system state\n"
                "  [green]thegent audit[/green]     Check system health/risk\n"
                "  [green]thegent plan[/green]      Manage the roadmap\n",
                title="thegent",
                border_style="blue",
            )
        )


if __name__ == "__main__":
    app()
