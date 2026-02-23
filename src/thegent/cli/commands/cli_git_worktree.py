"""Overhauled Git CLI for thegent (Phase 6 / WP-16003).

Replaces standard git with multitenancy-aware, parallel-capable commands.
Leverages gix/gitoxide via native binary and private index files.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from thegent.mesh.git import GitParallelismManager
from thegent.mesh.git_parallelism import WorktreePool
from thegent.native.git_native import GitNative


def _build_worktree_pool(
    project_root: Path,
    target_branch: str,
    pool_root: Path | None,
) -> WorktreePool:
    return WorktreePool(
        project_root=project_root,
        target_branch=target_branch,
        pool_root=pool_root,
    )



def _worktree_agents(pool: WorktreePool) -> list[tuple[str, str]]:
    """Return active worktree rows as (agent_id, branch)."""
    return sorted((agent_id, f"agent/{agent_id}") for agent_id in pool.active_agents())



def get_agent_id() -> str:
    """Return the current agent ID from settings or default."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.agent_id


worktree_app = typer.Typer(help="Manage agent worktree pool lifecycle for multi-agent git coordination.")
app.add_typer(worktree_app, name="worktree", help="Worktree pool management for coordinated agents.")


@worktree_app.command("status")

def worktree_status(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
    json_output: bool = typer.Option(False, "--json", help="Output status as JSON"),
):
    """Show active worktree leases in the pool."""
    pool = _build_worktree_pool(project_root, target_branch=target_branch, pool_root=pool_root)
    agents = _worktree_agents(pool)
    if json_output:
        if not agents:
            console.print("[]")
            return
        payload = [{"agent_id": agent_id, "branch": branch} for agent_id, branch in agents]
        import json

        console.print(json.dumps(payload, indent=2))
        return

    if not agents:
        console.print("[yellow]No active pooled worktrees.[/yellow]")
        return
    console.print(f"[cyan]Active pooled agents ({len(agents)}):[/cyan]")
    for agent_id, branch in agents:
        console.print(f"  - {agent_id} -> {branch}")


@worktree_app.command("list")

def worktree_list(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
    json_output: bool = typer.Option(False, "--json", help="Output list as JSON"),
) -> None:
    """List active worktree agents and their dedicated branch names."""
    pool = _build_worktree_pool(project_root, target_branch=target_branch, pool_root=pool_root)
    agents = _worktree_agents(pool)
    if json_output:
        payload = [{"agent_id": agent_id, "branch": branch} for agent_id, branch in agents]
        import json

        console.print(json.dumps(payload, indent=2))
        return
    if not agents:
        console.print("[yellow]No active pooled worktrees.[/yellow]")
        return
    console.print("[cyan]Active pooled worktrees:[/cyan]")
    for agent_id, branch in agents:
        console.print(f"  - agent: {agent_id}")
        console.print(f"    branch: {branch}")
        console.print(f"    target: {target_branch}")


@worktree_app.command("claim")

def worktree_claim(
    agent_id: str = typer.Argument(..., help="Agent ID to claim a worktree"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
    json_output: bool = typer.Option(False, "--json", help="Output acquisition as JSON"),
):
    """Alias for acquire, matching coordination-focused terminology."""
    worktree_acquire(
        agent_id=agent_id,
        project_root=project_root,
        target_branch=target_branch,
        pool_root=pool_root,
        json_output=json_output,
    )


@worktree_app.command("acquire")

def worktree_acquire(
    agent_id: str = typer.Argument(..., help="Agent ID to lease a worktree"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
    json_output: bool = typer.Option(False, "--json", help="Output acquisition as JSON"),
):
    """Acquire a pooled worktree for an agent."""
    pool = _build_worktree_pool(project_root, target_branch=target_branch, pool_root=pool_root)
    try:
        ctx = pool.acquire_worktree(agent_id)
    except RuntimeError as exc:
        console.print(f"[red]Failed to acquire worktree for {agent_id}: {exc}[/red]")
        raise typer.Exit(1) from exc

    if json_output:
        import json

        console.print(
            json.dumps(
                {
                    "agent_id": agent_id,
                    "path": str(ctx.path),
                    "branch": ctx.branch,
                },
                indent=2,
            )
        )
        return

    console.print(f"[green]Acquired worktree for {agent_id}[/green]")
    console.print(f"path={ctx.path}")
    console.print(f"branch={ctx.branch}")


@worktree_app.command("release")

def worktree_release(
    agent_id: str = typer.Argument(..., help="Agent ID to release"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
):
    """Release a pooled worktree and merge changes back to target branch."""
    pool = _build_worktree_pool(project_root, target_branch=target_branch, pool_root=pool_root)
    if not pool.release_worktree(agent_id):
        console.print(f"[yellow]No active worktree for agent {agent_id}[/yellow]")
        raise typer.Exit(1)
    console.print(f"[green]Released worktree for {agent_id}[/green]")


@worktree_app.command("cleanup-stale")

def worktree_cleanup_stale(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    target_branch: str = typer.Option("HEAD", "--target-branch", "-t", help="Target branch for release merges"),
    pool_root: Path | None = typer.Option(None, "--pool-root", help="Override default pool root"),
):
    """Remove stale entries from the worktree pool state."""
    pool = _build_worktree_pool(project_root, target_branch=target_branch, pool_root=pool_root)
    removed = pool.cleanup_stale()
    console.print(f"[green]Removed {removed} stale pool entry(ies).[/green]")



