"""Inline CLI examples for `thegent help <command>`.

Provides a curated dictionary of example invocations for each major command
and a helper that renders them in a Rich panel.

# @trace WL-040 WP-4004
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console(width=120)

ROOT_HELP_SHORTCUTS: list[str] = [
    "  [green]thegent help worktree[/green] Show structured worktree commands",
    "  [green]thegent help git[/green]      Show structured git worktree commands",
]

ROOT_HELP_SHORTCUT_BLOCK = "\n".join(ROOT_HELP_SHORTCUTS)


def _refresh_examples(command_prefix: str) -> list[str]:
    """Build refresh examples for the requested command prefix."""
    return [
        f"{command_prefix} refresh <change-anchor> --ref origin/canary",
        f"{command_prefix} refresh <change-anchor> --remote origin --strategy merge",
    ]


def _migration_examples(command_prefix: str) -> list[str]:
    """Build legacy migration examples for the requested command prefix."""
    return [
        f"{command_prefix} migrate-legacy /tmp/legacy-cache infra m migrate-cache",
        f"{command_prefix} migrate-legacy /tmp/legacy-cache infra m migrate-cache blocked",
    ]

# ---------------------------------------------------------------------------
# Example registry
# ---------------------------------------------------------------------------

COMMAND_EXAMPLES: dict[str, list[str]] = {
    "free": [
        "thegent run free 'Summarise the TODO list in README.md'",
        "thegent run free 'Fix the failing tests' --bg",
        "thegent plan next",
        "thegent run agent 'Continuously process work items' --loop",
    ],
    "run": [
        "thegent run free 'Write unit tests for auth.py'",
        "thegent run agent 'Refactor the router' --model claude-sonnet-4-5 --bg",
        "thegent run agent 'Review PR #42' --model claude-sonnet-4-5",
        "thegent run ps  # list active sessions",
    ],
    "plan": [
        "thegent plan claim <task-id>           # claim a task before starting",
        "thegent plan complete <task-id>        # mark task done",
        "thegent plan next                     # run the next unclaimed item",
        "thegent plan work                     # show work-stream items",
        "thegent run agent 'Continuously process work items' --loop",
        "thegent plan incorporate --dry-run   # merge fragments into work-stream",
    ],
    "registry": [
        "thegent registry list                  # list registered personas",
        "thegent registry recommend code-review # recommend a persona for a task",
        "thegent registry doctor                # validate registry health",
        "thegent registry list --format json    # machine-readable output",
    ],
    "status": [
        "thegent status <session-id>            # JSON status of a session",
        "thegent status <session-id> --format rich",
    ],
    "doctor": [
        "thegent doctor                         # run all health checks",
        "thegent doctor --fix                   # attempt automatic repairs",
        "thegent doctor --network               # include network diagnostics",
        "thegent doctor --deps                  # deep dependency audit",
        "thegent doctor --runtime               # multi-runtime diagnostics",
    ],
    "govern": [
        "thegent govern approve <run-id>        # approve a HITL gate",
        "thegent govern reject <run-id>         # reject a HITL gate",
        "thegent govern vet <run-id>            # vet a run before promotion",
    ],
    "mcp": [
        "thegent sys mcp list                   # list registered MCP servers",
        "thegent sys mcp add --server codex --command 'thegent mcp'  # add an MCP server",
        "thegent mcp prune                      # remove orphaned LSP/MCP processes",
        "thegent mcp prune --dry-run            # preview what would be pruned",
    ],
    "git": [
        "thegent git worktree governance new <domain> <scale> <change-anchor> [start-point]",
        "thegent git worktree governance state <change-anchor> <new-state>",
        *_migration_examples("thegent git worktree governance"),
        "thegent git worktree governance list",
        *_refresh_examples("thegent git worktree governance"),
        "thegent git worktree governance check",
    ],
    "worktree": [
        "thegent worktree new <domain> <scale> <change-anchor> [start-point]",
        "thegent worktree state <change-anchor> <new-state>",
        *_migration_examples("thegent worktree"),
        "thegent worktree list",
        "thegent worktree prune [--dry-run]",
        *_refresh_examples("thegent worktree"),
        "thegent worktree check",
    ],
    "ps": [
        "thegent ps                             # list sessions for current owner",
        "thegent ps --all                       # list all sessions",
        "thegent ps --format json               # machine-readable output",
        "thegent ps --include-contract          # include routing contract metadata",
    ],
}


def show_help_examples(command: str) -> None:
    """Print inline examples for *command* in a formatted Rich panel.

    # @trace WL-040 WP-4004

    Args:
        command: The command name to look up (case-insensitive).
    """
    key = command.lower().strip()
    examples = COMMAND_EXAMPLES.get(key)

    if examples is None:
        # Fuzzy fallback: partial match
        matches = [k for k in COMMAND_EXAMPLES if key in k or k in key]
        if matches:
            key = matches[0]
            if key != command.lower().strip():
                console.print(f"[dim]Using fuzzy help examples for '{key}'.[/dim]")
            examples = COMMAND_EXAMPLES[key]
        else:
            available = ", ".join(sorted(COMMAND_EXAMPLES))
            console.print(f"[yellow]No examples found for '{command}'.[/yellow]\n[dim]Available: {available}[/dim]")
            return

    lines = "\n".join(f"  [dim]$[/dim] [green]{ex}[/green]" for ex in examples)
    console.print(
        Panel(
            lines,
            title=f"[bold cyan]thegent {key}[/bold cyan] — examples",
            border_style="cyan",
            padding=(1, 2),
        )
    )
