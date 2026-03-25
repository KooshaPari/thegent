"""CLI command: thegent tools [subcommand]

Subcommands for managing and borrowing thegent MCP tools in other projects.
"""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Manage and borrow thegent MCP tools for use in other projects.")


@app.command("list")
def tools_list(
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Filter by category (session, planning, dag, research, ...)"),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """List all available borrowable thegent MCP tools.

    Examples::

        thegent tools list
        thegent tools list --category research
        thegent tools list --json
    """
    from rich.console import Console
    from rich.table import Table

    from thegent.utils.borrow import ToolBorrower

    borrower = ToolBorrower()
    tools = borrower.list_available_tools()

    if category:
        tools = [t for t in tools if t.category == category.lower()]
        if not tools:
            typer.echo(f"No tools found for category '{category}'.", err=True)
            raise typer.Exit(1)

    if output_json:
        sys.stdout.write(json.dumps([t.to_dict() for t in tools], option=json.OPT_INDENT_2).decode() + "\n")
        raise typer.Exit(0)

    console = Console()
    table = Table(title="Available thegent MCP Tools (borrowable)", show_lines=True)
    table.add_column("Tool Name", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Read-Only", style="dim")
    table.add_column("Description")

    for t in tools:
        ro = "[green]yes[/green]" if t.read_only else "[red]no[/red]"
        table.add_row(t.name, t.category, ro, t.description)

    console.print(table)
    console.print(f"\n[dim]{len(tools)} tool(s) available.[/dim]")


@app.command("borrow")
def tools_borrow(
    tool_names: Annotated[
        str | None,
        typer.Argument(
            help="Comma-separated tool names to borrow (e.g. thegent_run,thegent_ps). Omit to borrow all tools."
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-o", help="Directory where mcp.json is written (default: current dir)"),
    ] = Path(),
    host: Annotated[
        str,
        typer.Option("--host", help="thegent MCP server host (default: 127.0.0.1)"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", help="thegent MCP server port (default: 3847)"),
    ] = 3847,
    no_merge: Annotated[
        bool,
        typer.Option("--no-merge", help="Overwrite mcp.json instead of merging"),
    ] = False,
    print_claude_md: Annotated[
        bool,
        typer.Option("--claude-md", help="Print CLAUDE.md snippet to stdout"),
    ] = False,
    check: Annotated[
        bool,
        typer.Option("--check", help="Check if thegent server is reachable before writing"),
    ] = False,
) -> None:
    """Borrow thegent MCP tools into another project.

    Writes (or updates) an mcp.json file in OUTPUT_DIR so that Claude Code
    in that directory can use the specified thegent tools via the running
    thegent MCP server.

    Examples::

        # Borrow all tools into the current project
        thegent tools borrow

        # Borrow specific tools
        thegent tools borrow thegent_run,thegent_ps,thegent_ddg_search

        # Write to a different project directory
        thegent tools borrow --output-dir ../my-other-project

        # Also print the CLAUDE.md snippet
        thegent tools borrow thegent_run,thegent_ps --claude-md

        # Point at a non-default server
        thegent tools borrow --host 0.0.0.0 --port 4000
    """
    from rich.console import Console

    from thegent.utils.borrow import BorrowConfig, ToolBorrower

    console = Console()
    config = BorrowConfig(host=host, port=port)
    borrower = ToolBorrower(config=config)

    names: list[str] = []
    if tool_names:
        names = [n.strip() for n in tool_names.split(",") if n.strip()]

    if check:
        console.print(f"[dim]Checking thegent server at {config.url}...[/dim]")
        if not borrower.validate_server_reachable():
            console.print(
                f"[yellow]Warning: thegent server not reachable at {config.url}. "
                "Continuing anyway — ensure the server is running before using the tools.[/yellow]"
            )
        else:
            console.print(f"[green]Server reachable at {config.url}[/green]")

    try:
        written = borrower.generate_mcp_json(
            tool_names=names,
            output_path=output_dir,
            merge=not no_merge,
        )
    except ValueError as exc:
        from thegent.errors import print_error

        print_error(str(exc))
        raise typer.Exit(1) from exc

    tool_label = ", ".join(names) if names else "all tools"
    console.print(f"[green]mcp.json updated:[/green] {written}")
    console.print(f"[dim]Borrowed: {tool_label}[/dim]")
    console.print(f"[dim]Server: {config.url}[/dim]")

    if print_claude_md:
        try:
            snippet = borrower.generate_claude_md_snippet(names)
        except ValueError as exc:
            console.print(f"[red]Error generating CLAUDE.md snippet:[/red] {exc}")
            raise typer.Exit(1) from exc

        console.print("\n[bold]CLAUDE.md snippet:[/bold]")
        console.print("---")
        console.print(snippet)
        console.print("---")


@app.command("show")
def tools_show(
    name: Annotated[str, typer.Argument(help="Tool name to show details for")],
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """Show details for a specific thegent MCP tool.

    Examples::

        thegent tools show thegent_run
        thegent tools show thegent_ddg_search --json
    """
    from rich.console import Console
    from rich.panel import Panel

    from thegent.utils.borrow import ToolBorrower

    borrower = ToolBorrower()
    manifest = borrower.get_tool(name)
    if manifest is None:
        typer.echo(f"Tool '{name}' not found. Run 'thegent tools list' to see available tools.", err=True)
        raise typer.Exit(1)

    if output_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), option=json.OPT_INDENT_2).decode() + "\n")
        raise typer.Exit(0)

    console = Console()
    ro = "yes" if manifest.read_only else "no"
    content = (
        f"[bold]Name:[/bold] {manifest.name}\n"
        f"[bold]Category:[/bold] {manifest.category}\n"
        f"[bold]Read-Only:[/bold] {ro}\n"
        f"[bold]Description:[/bold] {manifest.description}\n"
        f"[bold]Module:[/bold] {manifest.module}\n"
        f"[bold]Function:[/bold] {manifest.function}\n"
        f"[bold]Requires:[/bold] {', '.join(manifest.requires)}"
    )
    console.print(Panel(content, title=f"Tool: {manifest.name}", border_style="cyan"))


@app.command("snippet")
def tools_snippet(
    tool_names: Annotated[
        str | None,
        typer.Argument(help="Comma-separated tool names. Omit for all tools."),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="thegent MCP server host (default: 127.0.0.1)"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", help="thegent MCP server port (default: 3847)"),
    ] = 3847,
) -> None:
    """Print a CLAUDE.md snippet for the specified thegent tools.

    Examples::

        thegent tools snippet
        thegent tools snippet thegent_run,thegent_ps,thegent_ddg_search
    """
    from thegent.utils.borrow import BorrowConfig, ToolBorrower

    config = BorrowConfig(host=host, port=port)
    borrower = ToolBorrower(config=config)

    names: list[str] = []
    if tool_names:
        names = [n.strip() for n in tool_names.split(",") if n.strip()]

    try:
        snippet = borrower.generate_claude_md_snippet(names)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    sys.stdout.write(snippet + "\n")
