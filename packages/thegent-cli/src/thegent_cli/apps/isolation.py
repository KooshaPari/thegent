"""Thegent Isolation: Multi-tenancy and Sandboxing Control."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Manage agent isolation and multi-tenancy.")


@app.command("check")
def isolation_check(mode: str = typer.Option("sub-user", "--mode", help="Isolation mode to check")):
    """Check the status of the isolation system."""
    from thegent_cli.commands.impl import isolation_check_impl

    isolation_check_impl(mode=mode)


@app.command("share-run")
def isolation_share_run(
    command: list[str] = typer.Argument(..., help="Command to run shared"),
    tenant_id: str = typer.Option("default", "--tenant", help="Tenant ID"),
    role: str | None = typer.Option(None, "--role", help="L1 Role (e.g. frontend_lead)"),
):
    """Run a command shared across tenants using CLI-Share debouncing."""
    from thegent_execution.isolation.sub_user_provider import SubUserIsolationProvider

    provider = SubUserIsolationProvider(enable_l1_nesting=bool(role))
    context = provider.allocate_tenant(tenant_id, role=role)

    console.print(f"[bold blue]Executing shared command:[/bold blue] {' '.join(command)}")
    result = provider.execute_in_context(context, command, share=True)

    console.print(result["stdout"])
    if result.get("cached"):
        console.print("[dim][Attached to existing run / result served from cache][/dim]")

    raise typer.Exit(code=result["returncode"])
