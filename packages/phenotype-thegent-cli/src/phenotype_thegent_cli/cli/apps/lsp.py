"""LSP and JetBrains MCP tools management."""

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="LSP servers and JetBrains MCP tools management.")


@app.command("list", help="List all available LSP servers.")
def lsp_list():
    """List all available LSP servers."""
    from phenotype_thegent_cli.lsp.commands import list_all_lsp_servers

    servers = list_all_lsp_servers()
    for lang, info in servers.items():
        status = "[green]✓[/green]" if info["installed"] else "[red]✗[/red]"
        console.print(f"{status} {lang}: {info['description']}")


@app.command("restart", help="Restart LSP server for a language.")
def lsp_restart(language: str = typer.Argument(..., help="Language identifier")):
    """Restart an LSP server."""
    console.print(f"[yellow]Restarting {language} LSP server...[/yellow]")
    console.print("[dim]Not implemented yet[/dim]")


@app.command("prune", help="Stop all LSP server processes.")
def lsp_prune():
    """Stop all LSP server processes."""
    console.print("[yellow]Pruning LSP servers...[/yellow]")
    console.print("[dim]Not implemented yet[/dim]")


@app.command("jetbrains-mcp-tools", help="Manage JetBrains MCP tools.")
def jetbrains_mcp_tools(
    list_tools: bool = typer.Option(False, "--list", help="List available JetBrains MCP tools"),
    status: bool = typer.Option(False, "--status", help="Check JetBrains MCP server status"),
    test: bool = typer.Option(False, "--test", help="Test JetBrains MCP connection"),
):
    """List available JetBrains MCP tools and their status."""
    if list_tools:
        import asyncio

        from phenotype_thegent_cli.ide.jetbrains_tools import check_jetbrains_mcp_available, jetbrains_list_tools

        available = check_jetbrains_mcp_available()
        tools = asyncio.run(jetbrains_list_tools())
        console.print(
            f"[bold]JetBrains MCP Server:[/bold] {'[green]Available[/green]' if available else '[red]Not Available[/red]'}"
        )
        console.print("[bold]Port:[/bold] 8766")
        console.print()
        console.print(tools)
    elif status:
        from phenotype_thegent_cli.ide.jetbrains_tools import check_jetbrains_mcp_available

        available = check_jetbrains_mcp_available()
        if available:
            console.print("[green]JetBrains MCP server is running[/green]")
        else:
            console.print("[red]JetBrains MCP server is not running[/red]")
            console.print("Make sure JetBrains IDE is running with the MCP plugin enabled")
    elif test:
        console.print("[yellow]Testing JetBrains MCP connection...[/yellow]")
        from phenotype_thegent_cli.ide.jetbrains_tools import check_jetbrains_mcp_available

        available = check_jetbrains_mcp_available()
        if available:
            console.print("[green]Connection successful![/green]")
        else:
            console.print("[red]Connection failed - ensure JetBrains IDE MCP plugin is running[/red]")
    else:
        console.print("[yellow]Use --list, --status, or --test flag[/yellow]")
        console.print("Example: thegent lsp jetbrains-mcp-tools --list")
