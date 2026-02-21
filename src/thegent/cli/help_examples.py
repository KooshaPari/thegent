"""Inline CLI examples for `thegent help <command>`.

Provides a curated dictionary of example invocations for each major command
and a helper that renders them in a Rich panel.

# @trace WL-040 WP-4004
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()

# ---------------------------------------------------------------------------
# Example registry
# ---------------------------------------------------------------------------

COMMAND_EXAMPLES: dict[str, list[str]] = {
    "free": [
        "thegent free 'Summarise the TODO list in README.md'",
        "thegent free 'Fix the failing tests' --bg",
        "thegent free --do-next",
        "thegent free --do-next --repeat 5",
    ],
    "run": [
        "thegent run 'Write unit tests for auth.py'",
        "thegent run 'Refactor the router' -M claude-sonnet-4-5 --bg",
        "thegent run 'Review PR #42' --harness claude",
        "thegent run ps  # list active sessions",
    ],
    "plan": [
        "thegent plan list                     # show all work-stream tasks",
        "thegent plan claim <task-id>           # claim a task before starting",
        "thegent plan complete <task-id>        # mark task done",
        "thegent plan do-next                   # run the next unclaimed item",
        "thegent plan wait-next --timeout 120   # block until new work arrives",
        "thegent plan loop --max 50             # continuous autonomous loop",
        "thegent plan incorporate docs/PLAN.md  # merge fragments into work-stream",
    ],
    "registry": [
        "thegent registry list                  # list all registered personas",
        "thegent registry list --format json    # machine-readable output",
        "thegent registry register ./my-project # register project personas",
        "thegent registry search 'code-review'  # find personas by capability",
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
        "thegent govern list-pending            # show pending HITL approvals",
        "thegent govern list-pending --format json",
        "thegent govern approve <run-id>        # approve a HITL gate",
        "thegent govern reject <run-id>         # reject a HITL gate",
    ],
    "mcp": [
        "thegent sys mcp list                   # list registered MCP servers",
        "thegent sys mcp add <url>              # add an MCP server",
        "thegent mcp prune                      # remove orphaned LSP/MCP processes",
        "thegent mcp prune --dry-run            # preview what would be pruned",
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
