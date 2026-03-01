"""Thegent Git: log, diff, worktree, and lock-cleanup operations.

Phase 6 / WP-16003: Extracted from cli_git.py for modular management.
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

console = Console()
logger = logging.getLogger(__name__)


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


def register_worktree_commands(parent_app: typer.Typer) -> None:
    """Register worktree subcommands to parent app."""
    parent_app.add_typer(worktree_app, name="worktree", help="Worktree pool management for coordinated agents.")


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


lock_cleanup_app = typer.Typer(help="Remove stale .git/index.lock; manage periodic daemon")


def register_lock_cleanup_commands(parent_app: typer.Typer) -> None:
    """Register lock-cleanup subcommands to parent app."""
    parent_app.add_typer(lock_cleanup_app, name="lock-cleanup")


@lock_cleanup_app.callback(invoke_without_command=True)
def lock_cleanup_main(
    ctx: typer.Context,
    path: list[Path] = typer.Option(None, "--path", "-p", help="Paths to scan for .git/index.lock"),
    max_age: int = typer.Option(60, "--max-age", "-m", help="Remove locks older than N seconds"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be removed"),
):
    """Remove stale .git/index.lock files."""
    if ctx.invoked_subcommand is not None:
        return
    from thegent.git_lock_manage import run_lock_cleanup

    paths = [p for p in (path or []) if p.exists()] if path else None
    removed, skipped = run_lock_cleanup(paths=paths, max_age=max_age, dry_run=dry_run)
    if dry_run:
        console.print(f"[dim]Would remove {removed} stale lock(s), skip {skipped}[/dim]")
    else:
        console.print(f"[green]Removed {removed} stale lock(s), skipped {skipped}[/green]")


@lock_cleanup_app.command("service")
def lock_cleanup_service(
    action: str = typer.Argument(..., help="Action: install, start, stop, status, uninstall"),
):
    """Install or manage lock-cleanup daemon."""
    from thegent.git_lock_manage import (
        lock_cleanup_install,
        lock_cleanup_start,
        lock_cleanup_status,
        lock_cleanup_stop,
        lock_cleanup_uninstall,
    )

    if action == "install":
        ok, msg = lock_cleanup_install()
    elif action == "start":
        ok, msg = lock_cleanup_start()
    elif action == "stop":
        ok, msg = lock_cleanup_stop()
    elif action == "status":
        ok, msg = lock_cleanup_status()
    elif action == "uninstall":
        ok, msg = lock_cleanup_uninstall()
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)

    console.print(msg)
    if not ok and action in ("install", "start", "stop", "uninstall"):
        raise typer.Exit(1)


def log(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of commits to show"),
):
    """Show commit log."""
    try:
        output = subprocess.check_output(
            ["git", "log", f"-n{limit}", "--oneline", "--graph", "--decorate"], cwd=project_root, text=True
        )
        console.print(output)
    except subprocess.CalledProcessError:
        console.print("[red]Failed to retrieve git log.[/red]")


def diff(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID"),
    use_delta: bool = typer.Option(True, "--delta/--no-delta", help="Use delta for formatted diff output if available"),
):
    """Show changes: compares worktree against private index (or HEAD)."""
    aid = agent_id or get_agent_id()
    manager = GitParallelismManager(project_root, aid)
    manager.ensure_index()

    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(manager.agent_index)

    try:
        if use_delta:
            import shutil

            delta_bin = shutil.which("delta")
            if delta_bin:
                # Use delta as a pager for git diff
                # We use subprocess.Popen to pipe the output correctly
                diff_proc = subprocess.Popen(
                    ["git", "diff", "--color=always"],
                    cwd=project_root,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                delta_proc = subprocess.Popen([delta_bin], stdin=diff_proc.stdout, cwd=project_root)
                diff_proc.stdout.close()
                delta_proc.communicate()
                return

        output = subprocess.check_output(["git", "diff"], cwd=project_root, env=env, text=True)
        if not output.strip():
            console.print("[yellow]No changes between worktree and private index.[/yellow]")
        else:
            console.print(output)
    except subprocess.CalledProcessError:
        console.print("[red]Failed to run git diff.[/red]")


__all__ = [
    "get_agent_id",
    "log",
    "diff",
    "lock_cleanup_app",
    "lock_cleanup_main",
    "lock_cleanup_service",
    "register_lock_cleanup_commands",
    "register_worktree_commands",
    "worktree_acquire",
    "worktree_app",
    "worktree_claim",
    "worktree_cleanup_stale",
    "worktree_list",
    "worktree_release",
    "worktree_status",
]
