"""Logical stream: Task and Dependency Planning."""

from pathlib import Path

import typer
from rich.console import Console

from thegent.cli.plan.plan_entity_cmds import app as entity_app

console = Console()
app = typer.Typer(help="Manage DAG tasks, work streams, and roadmap initiatives.")
app.add_typer(entity_app, name="entity", help="Canonical entity CRUD, batch import/export, and sync.")


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
    from thegent.cli.commands.cli import plan_progress_cmd

    plan_progress_cmd(limit=limit, format=format)


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


@app.command("verify-workstream", help="Verify WORK_STREAM coordination invariants.")
def plan_verify_workstream(
    cd: Path | None = typer.Option(None, "--cd", help="Working directory"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli import plan_verify_workstream_cmd

    plan_verify_workstream_cmd(cd=cd, format=format)


@app.command("lint-workstream", help="Validate WORK_STREAM schema.")
def plan_lint_workstream(cd: Path | None = typer.Option(None, "--cd", help="Working directory")) -> None:
    from thegent.cli.commands.cli import plan_lint_workstream_cmd

    plan_lint_workstream_cmd(cd=cd)


@app.command("normalize-workstream", help="Sort and normalize WL sections in WORK_STREAM.")
def plan_normalize_workstream(cd: Path | None = typer.Option(None, "--cd", help="Working directory")) -> None:
    from thegent.cli.commands.cli import plan_normalize_workstream_cmd

    plan_normalize_workstream_cmd(cd=cd)


@app.command("progress", help="Show work stream progress summary.")
def plan_progress(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli import plan_progress_cmd

    plan_progress_cmd(limit=limit, format=format)


# ---------------------------------------------------------------------------
# Harness Terminal Status (integrated under plan for unified view)
# ---------------------------------------------------------------------------


@app.command("sessions", help="List all harness sessions across all agent types.")
def plan_sessions(
    harness: str | None = typer.Option(None, "--harness", "-h", help="Filter by harness type"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
) -> None:
    """List sessions from all agent harnesses."""
    from thegent.cli.commands.impl import harness_interact_impl

    if harness:
        result = harness_interact_impl(harness=harness, action="list_sessions")
    else:
        from thegent.cli.commands.impl import harness_list_actions_impl

        result = harness_list_actions_impl()
        console.print("[cyan]Available harnesses:[/cyan] cursor, codex, claude, ante, droid")
        console.print(f"[cyan]Actions:[/cyan] {result.get('actions', [])}")
        return

    if format == "json":
        import json

        console.print(json.dumps(result, indent=2))
    elif result.get("success"):
        console.print(result.get("stdout", ""))
    else:
        console.print(f"[red]Error:[/red] {result.get('error', '')}")


@app.command("harness-status", help="Get status of all registered harness hosts.")
def plan_harness_status(
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
) -> None:
    """Get status of all harness hosts."""
    from thegent.cli.commands.impl import harness_list_actions_impl
    from thegent.agents.unified_session_index import HarnessType

    status = {
        "harnesses": [h.value for h in HarnessType],
        "actions": harness_list_actions_impl().get("actions", []),
    }

    if format == "json":
        import json

        console.print(json.dumps(status, indent=2))
    else:
        console.print("[cyan]Registered Harness Types:[/cyan]")
        for h in status["harnesses"]:
            console.print(f"  - {h}")
        console.print("[cyan]Available Actions:[/cyan]")
        for a in status["actions"]:
            console.print(f"  - {a}")
