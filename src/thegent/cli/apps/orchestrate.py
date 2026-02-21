"""Logical stream: Sub-agent orchestration commands.

Provides CLI commands for decomposing and executing goals via the
LLMPlangentPlanner -> PlangentExecutor -> SubAgentDispatcher pipeline.

# @trace FR-ORC-088
# @trace WL-088
"""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from thegent.cli.commands.impl import orchestrate_plan_impl, orchestrate_run_impl

console = Console()

app = typer.Typer(
    name="orchestrate",
    help="Sub-agent orchestration: decompose goals and execute via agent DAG.",
)


@app.command("plan", help="Decompose a goal into a DAG plan and display as a rich table.")
def plan_cmd(
    goal: str = typer.Argument(..., help="High-level goal to decompose into sub-tasks."),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum decomposition depth."),
    model: str = typer.Option(
        "claude-haiku-4.5",
        "--model",
        "-m",
        help="LiteLLM model identifier for the LLM planner.",
    ),
    timeout: float = typer.Option(30.0, "--timeout", "-t", help="FlashAgent call timeout in seconds."),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON instead of rich table."),
) -> None:
    """Decompose *goal* into an OrchestrationPlan DAG and display the node table.

    Uses LLMPlangentPlanner to call the model and produce a structured
    decomposition.  Falls back to heuristic decomposition when the model
    is unavailable (logged at WARNING level).

    # @trace FR-ORC-088
    # @trace WL-088
    """
    result = orchestrate_plan_impl(
        goal,
        max_depth=max_depth,
        model=model,
        timeout_s=timeout,
    )

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return

    console.print(f"[bold cyan]Plan:[/bold cyan] {result['plan_id']}")
    console.print(f"[bold]Goal:[/bold] {result['goal']}")
    console.print(f"[dim]Created: {result['created_at']}[/dim]")
    console.print()

    table = Table(title=f"Orchestration Plan — {result['node_count']} nodes", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Task", min_width=30)
    table.add_column("Depends On", no_wrap=False)
    table.add_column("Agent Hint")
    table.add_column("Budget Tokens")

    for idx, node in enumerate(result["nodes"], start=1):
        deps = ", ".join(node["depends_on"]) if node["depends_on"] else "-"
        table.add_row(
            str(idx),
            node["id"][:8] + "...",
            node["task"],
            deps if len(deps) <= 30 else deps[:27] + "...",
            str(node["agent_hint"] or "-"),
            str(node["budget_tokens"] or "-"),
        )

    console.print(table)


@app.command("run", help="Decompose a goal and execute sub-agents, streaming events to stdout.")
def run_cmd(
    goal: str = typer.Argument(..., help="High-level goal to decompose and execute."),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum decomposition depth."),
    model: str = typer.Option(
        "claude-haiku-4.5",
        "--model",
        "-m",
        help="LiteLLM model identifier for the LLM planner.",
    ),
    timeout: float = typer.Option(30.0, "--timeout", "-t", help="FlashAgent call timeout in seconds."),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop on first node failure."),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON result instead of rich output."),
) -> None:
    """Decompose *goal* and execute via PlangentExecutor, streaming SubAgentEvents.

    Each dispatched node emits STARTED and COMPLETED events to the local
    SubAgentEventQueue which are printed to stdout as they are drained.

    Exit code 1 when any node fails.

    # @trace FR-ORC-088
    # @trace WL-088
    """
    result = orchestrate_run_impl(
        goal,
        max_depth=max_depth,
        model=model,
        timeout_s=timeout,
        fail_fast=fail_fast,
    )

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        raise typer.Exit(0 if result["all_passed"] else 1)

    console.print(f"[bold cyan]Plan:[/bold cyan] {result['plan_id']}")
    console.print(f"[bold]Goal:[/bold] {result['goal']}")
    console.print()

    # Print streamed events
    if result["events"]:
        console.print("[bold]Events:[/bold]")
        for evt in result["events"]:
            event_type = evt["event_type"]
            msg = evt.get("message") or event_type
            color = "green" if "completed" in event_type else "yellow"
            console.print(f"  [{color}]{event_type}[/{color}] {msg}")
        console.print()

    # Node summary table
    table = Table(title="Execution Summary", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Task", min_width=30)
    table.add_column("Status")
    table.add_column("Result / Error")

    for idx, node in enumerate(result["nodes"], start=1):
        status = node["status"]
        status_color = "green" if status == "done" else ("red" if status == "failed" else "yellow")
        detail = node.get("result") or node.get("error") or "-"
        table.add_row(
            str(idx),
            node["task"],
            f"[{status_color}]{status}[/{status_color}]",
            str(detail)[:60],
        )

    console.print(table)
    console.print()

    passed_color = "green" if result["all_passed"] else "red"
    console.print(
        f"[bold]Result:[/bold] [{passed_color}]{'PASSED' if result['all_passed'] else 'FAILED'}[/{passed_color}]"
        f"  ({result['success_count']} succeeded, {result['failure_count']} failed)"
    )

    if result["errors"]:
        console.print("[red]Errors:[/red]")
        for err in result["errors"]:
            console.print(f"  - {err}")

    raise typer.Exit(0 if result["all_passed"] else 1)
