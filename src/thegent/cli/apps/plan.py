"""Logical stream: Task and Dependency Planning."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Manage DAG tasks, work streams, and roadmap initiatives.")


@app.command("next", help="Identify next ready tasks from the DAG.")
def plan_next(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json|ids|md)"),
):
    from thegent.cli.commands.cli import dag_ready_cmd

    dag_ready_cmd(format=format)


@app.command("status", help="Show DAG status and visualization.")
def plan_status(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|graph|json|md)"),
):
    from thegent.cli.commands.cli import dag_status_cmd

    dag_status_cmd(format=format)


@app.command("add", help="Add a new task to the DAG.")
def plan_add(
    task_id: str = typer.Argument(..., help="New task ID"),
    agent: str = typer.Option("copilot", "--agent", "-a", help="Agent to assign"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Task prompt/description"),
    depends_on: list[str] | None = typer.Option(None, "--dep", "-d", help="Dependency task IDs"),
):
    from thegent.cli.commands.cli import dag_add_cmd

    deps_str = ",".join(depends_on) if depends_on else None
    dag_add_cmd(task_id=task_id, agent=agent, prompt=prompt, depends_on=deps_str)


@app.command("remove", help="Remove a task from the DAG.")
def plan_remove(task_id: str = typer.Argument(..., help="Task ID to remove")):
    from thegent.cli.commands.cli import dag_remove_cmd

    dag_remove_cmd(task_id=task_id)


@app.command("roadmap", help="Show high-level roadmap initiatives from PLAN.md.")
def plan_roadmap(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli_initiative import initiative_list_cmd

    initiative_list_cmd()


@app.command("work", help="View work-stream items from WORK_STREAM.md.")
def plan_work_stream(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of items to show"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli import workstream_list_cmd

    workstream_list_cmd(limit=limit, format=format)


@app.command("analyze", help="Analyze planning continuity and PERT risk.")
def plan_analyze(
    cd: Path | None = typer.Option(None, "--cd", help="Working directory to analyze"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli import plan_analyze_cmd

    plan_analyze_cmd(cd=cd, format=format)


@app.command("checkpoint", help="Create a DAG state checkpoint.")
def plan_checkpoint(reason: str = typer.Option("Manual checkpoint", "--reason", "-r")):
    from thegent.cli.commands.cli import dag_checkpoint_cmd

    dag_checkpoint_cmd(reason=reason)


@app.command("rollback", help="Rollback DAG state to a checkpoint.")
def plan_rollback(checkpoint_id: str = typer.Argument(..., help="Checkpoint ID to rollback to")):
    from thegent.cli.commands.cli import dag_rollback_cmd

    dag_rollback_cmd(checkpoint_id=checkpoint_id)


@app.command("incorporate", help="Incorporate new items into WORK_STREAM.md (alias for sync work).")
def plan_incorporate(dry_run: bool = typer.Option(False, "--dry-run", "-n")):
    from thegent.cli.commands.cli import plan_incorporate_cmd

    plan_incorporate_cmd(dry_run=dry_run)


@app.command("claim", help="Claim a work item for an agent.")
def plan_claim(
    item_id: str = typer.Argument(..., help="Work item ID to claim"),
    agent_id: str | None = typer.Option(None, "--agent", "-a", help="Agent ID to claim for"),
    cd: Path | None = typer.Option(None, "--cd", help="Working directory"),
):
    from thegent.cli.commands.cli import plan_claim_cmd

    plan_claim_cmd(item_id=item_id, agent_id=agent_id, cd=cd)


@app.command("complete", help="Mark a work item as complete.")
def plan_complete(
    item_id: str = typer.Argument(..., help="Work item ID to complete"),
    agent_id: str | None = typer.Option(None, "--agent", "-a", help="Agent ID that completed it"),
    cd: Path | None = typer.Option(None, "--cd", help="Working directory"),
):
    from thegent.cli.commands.cli import plan_complete_cmd

    plan_complete_cmd(item_id=item_id, agent_id=agent_id, cd=cd)


@app.command("progress", help="Show work stream progress summary.")
def plan_progress(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli import plan_progress_cmd

    plan_progress_cmd(limit=limit, format=format)
