"""Overhauled Git CLI for thegent (Phase 6 / WP-16003).

Replaces standard git with multitenancy-aware, parallel-capable commands.
Leverages gix/gitoxide via native binary and private index files.

Main re-export facade; implementation split across cli_git_log_ops and cli_git_commit_ops.
"""

import typer
from rich.console import Console

from phenotype_thegent_agint.cli.commands.cli_git_commit_ops import (
    add,
    commit,
    lock_status,
    merge,
    run_system_git,
    status,
)
from phenotype_thegent_agint.cli.commands.cli_git_log_ops import (
    diff,
    lock_cleanup_app,
    log,
    register_lock_cleanup_commands,
    register_worktree_commands,
    worktree_app,
)

app = typer.Typer(
    help="Overhauled Git: parallel, multitenant, and AST-aware (Phase 6)",
    no_args_is_help=False,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
console = Console()


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


# Register worktree and lock-cleanup subcommands
register_worktree_commands(app)
register_lock_cleanup_commands(app)

# Register main git commands
app.command("status")(status)
app.command("lock-status")(lock_status)
app.command("add")(add)
app.command("commit")(commit)
app.command("merge")(merge)
app.command("log")(log)
app.command("diff")(diff)


__all__ = [
    "app",
    "console",
    "callback",
    # Exported from split modules for backward compatibility
    "add",
    "commit",
    "diff",
    "lock_status",
    "lock_cleanup_app",
    "log",
    "merge",
    "run_system_git",
    "status",
    "worktree_app",
]
