"""WL-015: `thegent rules` CLI commands.

Cross-platform rules synchronization for Cursor, Claude Code, and Codex.

FR Traceability: FR-HAX-002
"""

from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer(help="Cross-platform rules synchronization (FR-HAX-002).")


@app.command("sync")
def rules_sync(
    project_dir: Path | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project root directory (defaults to current directory).",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Report what would be written without writing any files.",
    ),
    platform: str | None = typer.Option(
        None,
        "--platform",
        help="Platform to sync: cursor | claude | codex | all (default: all).",
    ),
) -> None:
    """Sync canonical rules from .thegent/rules/ to all target platforms.

    Reads each *.md rule file in <project>/.thegent/rules/, parses its
    frontmatter, and writes platform-specific outputs:

    \b
      cursor  -> .cursor/rules/thegent-rules.mdc
      claude  -> CLAUDE.md  (managed section)
      codex   -> .codex/skills/SKILL.md
    """
    from phenotype_thegent_core.core.rules_sync import ALL_PLATFORMS, Platform, RulesSyncManager

    root = (project_dir or Path.cwd()).resolve()

    # Validate --platform value
    effective_platforms: list[Platform]
    if platform is None or platform == "all":
        effective_platforms = list(ALL_PLATFORMS)
    elif platform in ALL_PLATFORMS:
        effective_platforms = [platform]  # type: ignore[list-item]
    else:
        console.print(f"[red]Unknown platform {platform!r}. Choose: cursor | claude | codex | all[/red]")
        raise typer.Exit(1)

    manager = RulesSyncManager()

    result = manager.sync_all(root, platforms=effective_platforms, dry_run=dry_run)

    if not result.success:
        for err in result.errors:
            console.print(f"[red]Error: {err}[/red]")
        raise typer.Exit(1)

    if not result.records:
        console.print("[yellow]No rules matched the selected platform(s). Nothing to sync.[/yellow]")
        return

    verb = "Would write" if dry_run else "Wrote"
    table = Table(title=f"Rules Sync {'(dry run) ' if dry_run else ''}— {result.rules_loaded} rule(s) loaded")
    table.add_column("Platform", style="cyan")
    table.add_column("Destination", style="green")
    table.add_column("Action", style="dim")

    for record in result.records:
        try:
            dest_display = str(record.destination.relative_to(root))
        except ValueError:
            dest_display = str(record.destination)

        action_display = "[dim]dry-run[/dim]" if record.action == "dry_run" else f"[green]{verb.lower()}[/green]"
        table.add_row(record.platform, dest_display, action_display)

    console.print(table)
    console.print(
        f"\n[green]{verb} {len(result.records)} file(s) in {result.duration:.3f}s.[/green]"
        if not dry_run
        else f"\n[yellow]Dry run: {len(result.records)} file(s) would be written.[/yellow]"
    )
