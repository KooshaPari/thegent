"""Overhauled Git CLI for thegent (Phase 6 / WP-16003).

Replaces standard git with multitenancy-aware, parallel-capable commands.
Leverages gix/gitoxide via native binary and private index files.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from thegent.infra.git_parallelism import GitParallelismManager
from thegent.native.git_native import GitNative

app = typer.Typer(
    help="Overhauled Git: parallel, multitenant, and AST-aware (Phase 6)",
    no_args_is_help=False,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
console = Console()
logger = logging.getLogger(__name__)


def get_agent_id() -> str:
    """Return the current agent ID from settings or default."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.agent_id


def run_system_git(args: list[str]) -> None:
    """Fallback: run the actual git binary."""
    # Find real git binary
    git_bin = Path("/usr/bin/git")
    if not git_bin.exists():
        import shutil

        git_bin_path = shutil.which("git") or "git"
        git_bin = Path(git_bin_path)

    try:
        # Use os.execvp to replace current process with git
        # This is the cleanest way to act as a transparent proxy
        os.execvp(str(git_bin), [str(git_bin), *args])
    except Exception as e:
        console.print(f"[red]Error executing system git: {e}[/red]")
        sys.exit(1)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """Default handler for unknown commands (pass-through to system git)."""
    if ctx.invoked_subcommand is None:
        if not ctx.args:
            # If no command and no args, show help
            console.print(ctx.get_help())
            raise typer.Exit()

        # Pass through all args to system git
        run_system_git(ctx.args)


@app.command("status")
def status(
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID (default: THGENT_AGENT_ID)"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    short: bool = typer.Option(False, "--short", "-s", help="Show short-format status"),
):
    """Show status: combines private index (staged) and worktree (modified)."""
    aid = agent_id or get_agent_id()
    manager = GitParallelismManager(project_root, aid)

    status_text = manager.get_agent_status()

    if short:
        console.print(status_text.strip())
        return

    if not status_text.strip():
        console.print(f"[yellow]No staged changes in private index for agent [bold]{aid}[/bold].[/yellow]")
        # Still show worktree status via GitNative
        gn = GitNative(project_root)
        s = gn.status()
        if s["modified"] or s["untracked"]:
            console.print("\n[bold]Worktree Changes (unstaged):[/bold]")
            for f in s["modified"]:
                console.print(f"  [red]modified:   {f}[/red]")
            for f in s["untracked"]:
                console.print(f"  [red]untracked:  {f}[/red]")
        return

    console.print(f"[bold cyan]Git Status for Agent: {aid}[/bold cyan]")
    console.print(status_text)


@app.command("add")
def add(
    files: list[str] = typer.Argument(..., help="Files to add to private index"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
):
    """Add files to the agent's private index (parallel-safe)."""
    aid = agent_id or get_agent_id()
    manager = GitParallelismManager(project_root, aid)
    if manager.stage_files(files):
        console.print(f"[green]Added {len(files)} files to private index for [bold]{aid}[/bold].[/green]")
    else:
        console.print(f"[red]Failed to add files for agent {aid}.[/red]")
        raise typer.Exit(1)


@app.command("commit")
def commit(
    message: str = typer.Argument(..., help="Commit message"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID"),
    ref: str = typer.Option("HEAD", "--ref", help="Reference to update"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
):
    """Create a commit from private index and update ref using atomic CAS."""
    aid = agent_id or get_agent_id()
    manager = GitParallelismManager(project_root, aid)

    # Auto-resolve ref name
    full_ref = ref
    if not ref.startswith("refs/"):
        try:
            full_ref = subprocess.check_output(["git", "symbolic-ref", "-q", ref], cwd=project_root, text=True).strip()
        except subprocess.CalledProcessError:
            full_ref = "HEAD" if ref == "HEAD" else f"refs/heads/{ref}"

    # 1. Get current ref hash
    try:
        old_hash = subprocess.check_output(["git", "rev-parse", full_ref], cwd=project_root, text=True).strip()
    except subprocess.CalledProcessError:
        console.print(f"[red]Error: Could not resolve reference '{ref}'.[/red]")
        raise typer.Exit(1)

    # 2. Create commit object
    console.print(f"Creating commit object for agent [bold]{aid}[/bold]...")
    new_hash = manager.create_commit_from_index(message, parent_ref=full_ref)

    if not new_hash:
        console.print("[red]Failed to create commit object from private index.[/red]")
        raise typer.Exit(1)

    console.print(f"Commit created: [cyan]{new_hash}[/cyan]")

    # 3. Atomic update ref
    console.print(f"Updating [bold]{full_ref}[/bold] from {old_hash[:8]} to {new_hash[:8]}...")
    if manager.update_ref_cas(full_ref, new_hash, old_hash):
        console.print(f"[bold green]Successfully updated {full_ref}![/bold green]")
    else:
        console.print("[bold red]Update collision detected![/bold red]")
        console.print(
            "[yellow]The reference moved while we were committing. You may need to merge/rebase and retry.[/yellow]"
        )
        raise typer.Exit(1)


@app.command("merge")
def merge(
    base: Path = typer.Argument(..., help="Base file (common ancestor)"),
    ours: Path = typer.Argument(..., help="Our file (current agent changes)"),
    theirs: Path = typer.Argument(..., help="Their file (incoming changes)"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file (default: overwrites ours)"),
):
    """AST-aware merge using Mergiraf (Phase 7)."""
    from thegent.governance.heliosShield_bridge import SmartMerge

    merger = SmartMerge()
    out_path = output or ours

    console.print(f"Performing AST-aware merge: [cyan]{ours.name}[/cyan]...")
    if merger.merge_files(base, ours, theirs, out_path):
        console.print(f"[bold green]Merge successful![/bold green] Result saved to {out_path}")
    else:
        console.print("[bold red]Merge failed or has conflicts.[/bold red]")
        raise typer.Exit(1)


lock_cleanup_app = typer.Typer(help="Remove stale .git/index.lock; manage periodic daemon")
app.add_typer(lock_cleanup_app, name="lock-cleanup")


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


@app.command("log")
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


@app.command("diff")
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
