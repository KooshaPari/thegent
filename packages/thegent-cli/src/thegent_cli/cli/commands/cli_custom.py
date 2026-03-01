import typer
from rich.console import Console
from rich.table import Table

console = Console()


def context_history_cmd(
    query: str | None = typer.Option(None, "--query", "-q", help="Search string for command content"),
    task_id: str | None = typer.Option(None, "--task-id", "-t", help="Filter by task ID"),
    cwd: str | None = typer.Option(None, "--cwd", "-c", help="Filter by working directory"),
    limit: int = typer.Option(50, "--limit", "-l", help="Number of entries to show"),
) -> None:
    """Search and display context-aware shell history."""
    from thegent_core.infra.history import ContextHistory

    history = ContextHistory()
    results = history.search(query=query, task_id=task_id, cwd=cwd, limit=limit)

    if not results:
        console.print("[dim]No shell history matching criteria found.[/dim]")
        return

    table = Table(title="Context-Aware Shell History")
    table.add_column("ID", style="dim")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Task ID", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Exit", justify="right")
    table.add_column("CWD", style="blue", overflow="fold")

    for entry in results:
        table.add_row(
            str(entry.id),
            entry.timestamp.split("T")[-1][:8] if "T" in entry.timestamp else entry.timestamp,
            entry.task_id or "—",
            entry.command,
            str(entry.exit_code),
            entry.cwd,
        )
    console.print(table)


def scratchpad_cmd(
    action: str = typer.Argument("show", help="Action: show, add, clear, pop"),
    content: str | None = typer.Argument(None, help="Content to add (for 'add' action)"),
) -> None:
    """Manage the AI command drafting scratchpad."""
    from thegent_skills.skills.scratchpad import AIScratchpad

    scratch = AIScratchpad()

    if action == "show":
        lines = scratch.state.buffer
        if not lines:
            console.print("[dim]Scratchpad is empty.[/dim]")
            return

        console.print("[bold cyan]AI Scratchpad Content:[/bold cyan]")
        for i, line in enumerate(lines):
            console.print(f"[dim]{i + 1:2d} |[/dim] {line}")

    elif action == "add":
        if not content:
            console.print("[red]Error: content required for 'add'[/red]")
            return
        scratch.add_line(content)
        console.print("[green]Added to scratchpad.[/green]")

    elif action == "clear":
        scratch.clear()
        console.print("[yellow]Scratchpad cleared.[/yellow]")

    elif action == "pop":
        scratch.delete_last()
        console.print("[yellow]Removed last line from scratchpad.[/yellow]")


def memory_cmd(
    action: str = typer.Argument("show", help="Action: show, add, query"),
    content: str | None = typer.Argument(None, help="Node content (for 'add' action)"),
    node_id: str | None = typer.Option(None, "--id", "-i", help="Node ID"),
    type: str = typer.Option("concept", "--type", "-t", help="Node type"),
    query: str | None = typer.Option(None, "--query", "-q", help="Search query"),
) -> None:
    """Manage hierarchical memory (MemoryMesh v2)."""
    from thegent_core.infra.memory import MemoryMeshV2, MemoryNode

    mem = MemoryMeshV2()

    if action == "add":
        if not node_id or not content:
            console.print("[red]Error: --id and --content required for 'add'[/red]")
            return
        node = MemoryNode(id=node_id, type=type, content=content)
        mem.add_knowledge(node)
        console.print(f"[green]Added knowledge node: {node_id}[/green]")

    elif action == "query":
        if not query:
            console.print("[red]Error: --query required for 'query'[/red]")
            return
        results = mem.query_knowledge(query)
        if not results:
            console.print("[dim]No matching knowledge found.[/dim]")
            return

        table = Table(title=f"Semantic Memory Query: {query}")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Content", style="green")

        for node in results:
            table.add_row(node.id, node.type, node.content)
        console.print(table)

    elif action == "show":
        if node_id:
            results = [n for n in mem.query_knowledge("") if n.id == node_id]
            if not results:
                console.print(f"[red]Node not found: {node_id}[/red]")
                return
            node = results[0]
            console.print(f"[bold cyan]Node ID:[/bold cyan] {node.id}")
            console.print(f"[bold cyan]Type:[/bold cyan]    {node.type}")
            console.print(f"[bold cyan]Content:[/bold cyan] {node.content}")

            related = mem.get_related_nodes(node.id)
            if related:
                console.print("\n[bold cyan]Related Nodes:[/bold cyan]")
                for r in related:
                    console.print(f"  → {r.id} ({r.type})")
        else:
            console.print(
                "[yellow]Use 'memory query --query <text>' to search or 'memory show --id <id>' for details.[/yellow]"
            )
