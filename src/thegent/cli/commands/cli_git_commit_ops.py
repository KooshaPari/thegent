"""Thegent Git: commit, add, merge, and status operations.

Phase 6 / WP-16003: Extracted from cli_git.py for modular management.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from thegent.cli.commands.cli_git_identity import resolve_author_env
from thegent.mesh.git import GitParallelismManager

console = Console()
logger = logging.getLogger(__name__)


def get_agent_id() -> str:
    """Return the current agent ID from settings or default."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.agent_id


def run_system_git(args: list[str], *, actor_profile: str | None = None) -> None:
    """Fallback: run the actual git binary."""
    env: dict[str, str] | None = None
    if args and args[0] == "commit":
        effective_profile = actor_profile or os.getenv("THGENT_GIT_ACTOR_PROFILE")
        env = resolve_author_env(
            project_root=Path.cwd(),
            actor_profile=effective_profile,
            agent_id=get_agent_id(),
        )

    # Find real git binary
    git_bin = Path("/usr/bin/git")
    if not git_bin.exists():
        import shutil

        git_bin_path = shutil.which("git") or "git"
        git_bin = Path(git_bin_path)

    try:
        # Use os.execvpe to replace current process with git and preserve/override env.
        system_env = os.environ.copy()
        if env:
            system_env.update(env)
        os.execvpe(str(git_bin), [str(git_bin), *args], system_env)
    except Exception as e:
        console.print(f"[red]Error executing system git: {e}[/red]")
        sys.exit(1)


def status(
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID (default: THGENT_AGENT_ID)"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    short: bool = typer.Option(False, "--short", "-s", help="Show short-format status"),
):
    """Show status: combines private index (staged) and worktree (modified)."""
    from thegent.native.git_native import GitNative

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


def lock_status(
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    stale_after_s: float = typer.Option(
        90.0,
        "--stale-after",
        help="Lock age in seconds for stale classification.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Output status as JSON"),
):
    """Inspect current `.git/index.lock` state."""
    manager = GitParallelismManager(project_root, get_agent_id())
    status_payload = manager.index_lock_status(stale_after_s=stale_after_s)
    if json_output:
        import json

        console.print(json.dumps(status_payload, indent=2))
        return

    if not status_payload["exists"]:
        console.print("[green]No index.lock present.[/green]")
        return

    age = status_payload["age_seconds"]
    age_text = f"{age:.2f}s" if isinstance(age, float) else "unknown"
    stale_text = "STALE" if status_payload["is_stale"] else "FRESH"
    holder_text = "active" if status_payload["open_holder_detected"] else "idle"
    console.print(f"index.lock: {status_payload['path']}")
    console.print(f"age: {age_text}")
    console.print(f"status: {stale_text} (threshold {status_payload['stale_after_seconds']}s)")
    console.print(f"holder: {holder_text}")


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


def commit(
    message: str = typer.Argument(..., help="Commit message"),
    agent_id: str = typer.Option(None, "--agent", "-a", help="Agent ID"),
    actor_profile: str | None = typer.Option(
        None,
        "--actor-profile",
        help="Actor profile for git identity override (human|agent|codex|claude|...).",
    ),
    ref: str = typer.Option("HEAD", "--ref", help="Reference to update"),
    project_root: Path = typer.Option(Path.cwd(), "--root", "-r", help="Project root directory"),
    lock_timeout: float = typer.Option(8.0, "--lock-timeout", help="Seconds to wait for index lock"),
    stale_after_s: float = typer.Option(
        90.0,
        "--stale-after",
        help="Lock age in seconds before stale cleanup is attempted (negative to disable age gate).",
    ),
    allow_stale_cleanup: bool = typer.Option(
        True,
        "--allow-stale-cleanup/--no-allow-stale-cleanup",
        help="Enable automatic stale .git/index.lock cleanup.",
    ),
):
    """Create a commit from private index and update ref using atomic CAS."""
    aid = agent_id or get_agent_id()
    manager = GitParallelismManager(project_root, aid)
    author_env = resolve_author_env(project_root=project_root, actor_profile=actor_profile, agent_id=aid)

    # Multi-tenant guard: do not spin forever on shared index lock.
    if not manager.wait_for_index_lock(
        timeout_s=lock_timeout,
        stale_after_s=stale_after_s,
        allow_stale_cleanup=allow_stale_cleanup,
    ):
        ours = manager.staged_files()
        queue_file = manager.queue_commit_conflict(
            ref=ref,
            reason="index_lock_contention",
            ours=ours,
            theirs=[],
            overlap=[],
        )
        console.print("[bold yellow]Git index is locked by another tenant/agent.[/bold yellow]")
        console.print(f"[yellow]Queued commit request:[/yellow] {queue_file}")
        console.print("[yellow]Prompt:[/yellow] resolve current git writer, then retry `thegent git commit`.")
        raise typer.Exit(2)

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
    new_hash = manager.create_commit_from_index(message, parent_ref=full_ref, author_env=author_env)

    if not new_hash:
        console.print("[red]Failed to create commit object from private index.[/red]")
        raise typer.Exit(1)

    console.print(f"Commit created: [cyan]{new_hash}[/cyan]")

    # 3. Atomic update ref
    console.print(f"Updating [bold]{full_ref}[/bold] from {old_hash[:8]} to {new_hash[:8]}...")
    if manager.update_ref_cas(full_ref, new_hash, old_hash):
        console.print(f"[bold green]Successfully updated {full_ref}![/bold green]")
        return

    # CAS moved: resolve if unrelated, queue+prompt if related.
    refreshed = manager._get_ref_hash(full_ref)
    if not refreshed:
        console.print("[bold red]Ref update failed and ref cannot be resolved.[/bold red]")
        raise typer.Exit(1)

    ours = manager.staged_files()
    theirs = manager.changed_files_between(old_hash, refreshed)
    overlap = manager.related_overlap(ours, theirs)

    if overlap:
        console.print("[bold yellow]Related change overlap detected.[/bold yellow]")
        console.print(f"[yellow]Overlap files:[/yellow] {', '.join(overlap)}")

        # Strategy 1: attempt native 3-way merge commit for related overlap.
        auto_merge_enabled = os.environ.get("THGENT_GIT_AUTO_MERGE_OVERLAP", "true").lower() in ("1", "true", "yes")
        if auto_merge_enabled:
            console.print("[cyan]Attempting auto 3-way merge strategy...[/cyan]")
            merged_hash = manager.try_auto_merge_commit(
                new_hash,
                refreshed,
                message,
                author_env=author_env,
            )
            if merged_hash:
                if manager.update_ref_cas(full_ref, merged_hash, refreshed):
                    console.print(f"[bold green]Auto-merged overlap and updated {full_ref}![/bold green]")
                    return
                queue_file = manager.queue_commit_conflict(
                    ref=full_ref,
                    reason="overlap_auto_merge_cas_failed",
                    ours=ours,
                    theirs=theirs,
                    overlap=overlap,
                    old_hash=refreshed,
                    new_hash=merged_hash,
                )
                console.print("[bold red]Auto-merge produced commit but CAS update failed.[/bold red]")
                console.print(f"[yellow]Queued for manual resolution:[/yellow] {queue_file}")
                raise typer.Exit(2)

        # Strategy 2: queue + prompt for manual conflict handling.
        queue_file = manager.queue_commit_conflict(
            ref=full_ref,
            reason="related_change_overlap",
            ours=ours,
            theirs=theirs,
            overlap=overlap,
            old_hash=old_hash,
            new_hash=refreshed,
        )
        console.print(f"[yellow]Queued for manual resolution:[/yellow] {queue_file}")
        console.print(
            "[yellow]Prompt:[/yellow] review overlap, merge/rebase if needed, then rerun `thegent git commit`."
        )
        raise typer.Exit(2)

    # No overlap: auto-resolve by rebuilding commit against refreshed parent, then CAS again.
    console.print("[cyan]Ref moved without overlapping files; auto-resolving commit parent...[/cyan]")
    new_hash_resolved = manager.create_commit_from_index(
        message,
        parent_ref=full_ref,
        author_env=author_env,
    )
    if not new_hash_resolved:
        console.print("[red]Failed to rebuild commit object for auto-resolution.[/red]")
        raise typer.Exit(1)
    if manager.update_ref_cas(full_ref, new_hash_resolved, refreshed):
        console.print(f"[bold green]Auto-resolved and updated {full_ref}![/bold green]")
    else:
        queue_file = manager.queue_commit_conflict(
            ref=full_ref,
            reason="cas_retry_exhausted",
            ours=ours,
            theirs=theirs,
            overlap=[],
            old_hash=refreshed,
            new_hash=new_hash_resolved,
        )
        console.print("[bold red]Update collision persists after auto-resolution.[/bold red]")
        console.print(f"[yellow]Queued for retry/resolution:[/yellow] {queue_file}")
        raise typer.Exit(2)


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


__all__ = [
    "add",
    "commit",
    "get_agent_id",
    "lock_status",
    "merge",
    "run_system_git",
    "status",
]
