"""Logical stream: Agent Registry — capability index, recommendation, and health doctor (WL-034)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Agent Registry: capability index, recommendations, and health checks (WL-034).")


@app.command("recommend", help="Recommend agents for a task using capability index (no LLM).")
def registry_recommend(
    task: str = typer.Argument(..., help="Task description to match agents against"),
    top_n: int = typer.Option(3, "--top", "-n", help="Number of top recommendations to return"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """Recommend the best agents for a task using local TF-IDF keyword scoring.

    Scans ~/.claude/agents/*.md and .claude/agents/*.md for agents with
    declared capabilities and description. No LLM calls required.
    """
    import json
    import sys

    from thegent.agents.capability_index import CapabilityIndex

    index = CapabilityIndex.get()
    recommendations = index.recommend(task, top_n=top_n)

    fmt = format.lower()

    if fmt == "json":
        payload = [
            {
                "name": r.name,
                "score": r.score,
                "description": r.description,
                "capabilities": r.capabilities,
                "path": str(r.path),
            }
            for r in recommendations
        ]
        sys.stdout.write(json.dumps(payload) + "\n")
        return

    if not recommendations:
        console.print("[dim]No matching agents found for that task description.[/dim]")
        console.print(
            "[dim]Tip: Add 'capabilities: [keyword1, keyword2]' to agent frontmatter to improve matching.[/dim]"
        )
        return

    tbl = Table(title=f"Agent Recommendations for: {task[:60]}")
    tbl.add_column("#", style="dim", width=3)
    tbl.add_column("Agent", style="bold cyan")
    tbl.add_column("Score", justify="right")
    tbl.add_column("Capabilities")
    tbl.add_column("Description")

    for i, rec in enumerate(recommendations, 1):
        caps = ", ".join(rec.capabilities) if rec.capabilities else "[dim]none[/dim]"
        desc = rec.description[:60] + "..." if len(rec.description) > 60 else rec.description
        tbl.add_row(str(i), rec.name, f"{rec.score:.4f}", caps, desc or "[dim]—[/dim]")

    console.print(tbl)


@app.command("doctor", help="Validate all registered agents for runner config and frontmatter health.")
def registry_doctor(
    format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
    fail_on_issues: bool = typer.Option(False, "--fail", help="Exit non-zero if any agents have issues"),
) -> None:
    """Check every agent in the registry for:
    - Valid parseable YAML frontmatter
    - A 'model' or 'runner' field
    - No dangling or empty references

    Prints a health status table. Use --fail to exit 1 if issues found.
    """
    import json
    import sys

    from thegent.agents.capability_index import CapabilityIndex

    index = CapabilityIndex.get()
    results = index.doctor()
    fmt = format.lower()

    if fmt == "json":
        payload = [
            {
                "name": r.name,
                "path": str(r.path),
                "healthy": r.healthy,
                "valid_frontmatter": r.valid_frontmatter,
                "has_runner_config": r.has_runner_config,
                "issues": r.issues,
            }
            for r in results
        ]
        sys.stdout.write(json.dumps(payload) + "\n")
        if fail_on_issues and any(not r.healthy for r in results):
            raise typer.Exit(1)
        return

    if not results:
        console.print("[dim]No agents found in ~/.claude/agents/ or .claude/agents/[/dim]")
        return

    tbl = Table(title="Agent Registry Health")
    tbl.add_column("Agent", style="bold")
    tbl.add_column("Status")
    tbl.add_column("Frontmatter")
    tbl.add_column("Runner Config")
    tbl.add_column("Issues")

    has_issues = False
    for r in results:
        status = "[green]OK[/green]" if r.healthy else "[red]FAIL[/red]"
        fm_ok = "[green]OK[/green]" if r.valid_frontmatter else "[red]FAIL[/red]"
        rc_ok = "[green]OK[/green]" if r.has_runner_config else "[yellow]WARN[/yellow]"
        issue_text = "; ".join(r.issues) if r.issues else "[dim]none[/dim]"
        tbl.add_row(r.name, status, fm_ok, rc_ok, issue_text)
        if not r.healthy:
            has_issues = True

    console.print(tbl)

    healthy_count = sum(1 for r in results if r.healthy)
    console.print(f"\n[bold]{healthy_count}/{len(results)}[/bold] agents healthy.")

    if fail_on_issues and has_issues:
        raise typer.Exit(1)


@app.command("list", help="List all agents in the capability index.")
def registry_list(
    capability: str | None = typer.Option(None, "--capability", "-c", help="Filter by capability"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json"),
) -> None:
    """List agents from the capability index with their declared capabilities."""
    import json
    import sys

    from thegent.agents.capability_index import CapabilityIndex

    index = CapabilityIndex.get()

    if capability:
        agents = index.agents_for_capability(capability)
    else:
        agents = index.all_agents()

    fmt = format.lower()

    if fmt == "json":
        payload = [
            {
                "name": a.name,
                "description": a.description,
                "capabilities": a.capabilities,
                "model": a.model,
                "runner": a.runner,
                "path": str(a.path),
            }
            for a in agents
        ]
        sys.stdout.write(json.dumps(payload) + "\n")
        return

    if not agents:
        msg = f"No agents with capability '{capability}'" if capability else "No agents found"
        console.print(f"[dim]{msg}[/dim]")
        return

    tbl = Table(title="Agent Capability Index")
    tbl.add_column("Agent", style="bold cyan")
    tbl.add_column("Model/Runner")
    tbl.add_column("Capabilities")
    tbl.add_column("Description")

    for a in agents:
        runner_info = a.model or a.runner or "[dim]—[/dim]"
        caps = ", ".join(a.capabilities) if a.capabilities else "[dim]none[/dim]"
        desc = a.description[:60] + "..." if len(a.description) > 60 else a.description
        tbl.add_row(a.name, runner_info, caps, desc or "[dim]—[/dim]")

    console.print(tbl)


def recommend_agent(task_description: str, top_n: int = 3) -> list:  # type: ignore[type-arg]
    """Public API: recommend agents for a task. Returns list of AgentRecommendation.

    Used by thegent free auto-agent selection.
    """
    from thegent.agents.capability_index import CapabilityIndex

    return CapabilityIndex.get().recommend(task_description, top_n=top_n)
