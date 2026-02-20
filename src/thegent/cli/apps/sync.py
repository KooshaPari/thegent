"""Logical stream: System State Synchronization."""

import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from . import models

console = Console()
app = typer.Typer(help="Synchronize rules, DAG, and model catalog.")

app.add_typer(models.app, name="models", help="Manage custom models and providers.")


@app.command("all", help="Synchronize all system components.")
def sync_all(
    components: list[str] | None = typer.Option(None, "--component", "-c", help="Specific components to sync"),
    force: bool = typer.Option(False, "--force", "-f", help="Force synchronization"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate synchronization"),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=components, force=force, dry_run=dry_run, format=format))


@app.command("rules", help="Sync CLAUDE.md to all platform-specific rule files.")
def sync_rules(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["rules"], force=force))


@app.command("dag", help="Synchronize DAG state from session meta files.")
def sync_dag(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["dag"], force=force))


@app.command("work", help="Incorporate new work items into WORK_STREAM.md.")
def sync_work_stream(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["work-stream"], force=force))


@app.command("catalog", help="Update the model catalog by scraping providers.")
def sync_catalog(force: bool = typer.Option(False, "--force", "-f")):
    from thegent.cli.commands.cli_sync import sync_cmd_impl

    asyncio.run(sync_cmd_impl(components=["catalog"], force=force))


@app.command("update", help="Update system components and dependencies.")
def sync_update(
    components: list[str] | None = typer.Option(None, "--component", "-c", help="Specific components to update"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate update"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update"),
):
    from thegent.cli.commands.cli_sync import update_cmd_impl

    asyncio.run(update_cmd_impl(components=components, dry_run=dry_run, force=force))
