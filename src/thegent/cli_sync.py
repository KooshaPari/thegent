
import typer
from rich.console import Console
from rich.table import Table

from thegent.sync import SyncComponent, SyncOrchestrator, SyncResult, SyncStatus, registry

console = Console()
app = typer.Typer(help="Unified sync, update, and audit commands.")

# --- Component Implementations ---


class RulesSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("rules", "Sync agent rules (CLAUDE.md -> platforms)")

    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli_impl import rules_sync_impl

        result = rules_sync_impl(force=force, check=dry_run)
        if result["success"]:
            msg = "Rules synced successfully" if not dry_run else "Rules check complete"
            return SyncResult(self.name, SyncStatus.SUCCESS, msg, details=result)
        return SyncResult(self.name, SyncStatus.FAILED, result.get("error", "Unknown error"))


class PromptsSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("prompts", "Harvest idea seeds from prompt history")

    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        if dry_run:
            return SyncResult(self.name, SyncStatus.SKIPPED, "Harvest skipped in dry-run")
        from thegent.prompts import run_harvest

        exit_code, msg = run_harvest()
        status = SyncStatus.SUCCESS if exit_code == 0 else SyncStatus.FAILED
        return SyncResult(self.name, status, msg)


class DagSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("dag", "Synchronize DAG state")

    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli_impl import dag_sync_impl

        # dag_sync_impl doesn't have a dry_run mode easily accessible here,
        # but it's generally safe to run as it just reconciles state.
        if dry_run:
            return SyncResult(self.name, SyncStatus.SKIPPED, "DAG sync skipped in dry-run")
        result = dag_sync_impl()
        if result.get("success", True):
            return SyncResult(self.name, SyncStatus.SUCCESS, "DAG state synchronized")
        return SyncResult(self.name, SyncStatus.FAILED, result.get("error", "DAG sync failed"))


class WorkStreamSyncComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("work-stream", "Incorporate work stream fragments", depends_on=["dag"])

    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.cli import plan_incorporate_cmd

        try:
            # plan_incorporate_cmd prints directly to console, so we might want to capture it or just call it
            plan_incorporate_cmd(dry_run=dry_run)
            return SyncResult(self.name, SyncStatus.SUCCESS, "Work stream incorporated")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, str(e))


class CatalogUpdateComponent(SyncComponent):
    def __init__(self) -> None:
        super().__init__("catalog", "Update model catalog by scraping providers")

    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        from thegent.models.scrapers import get_scraped_catalog

        try:
            get_scraped_catalog(refresh=not dry_run)
            return SyncResult(self.name, SyncStatus.SUCCESS, "Model catalog updated")
        except Exception as e:
            return SyncResult(self.name, SyncStatus.FAILED, str(e))


# --- Registration ---

registry.register(RulesSyncComponent())
registry.register(PromptsSyncComponent())
registry.register(DagSyncComponent())
registry.register(WorkStreamSyncComponent())
registry.register(CatalogUpdateComponent())

# --- CLI Commands ---


@app.command("sync")
def sync_cmd(
    components: list[str] | None = typer.Argument(None, help="Components to sync (default: all)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force sync even if up-to-date"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would sync"),
):
    """Unified sync command for all thegent components."""
    orchestrator = SyncOrchestrator(registry)
    results = orchestrator.sync(names=components, dry_run=dry_run, force=force)

    table = Table(title="Sync Results")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Duration")
    table.add_column("Message")

    for res in results:
        status_color = (
            "green" if res.status == SyncStatus.SUCCESS else "red" if res.status == SyncStatus.FAILED else "yellow"
        )
        table.add_row(
            res.component, f"[{status_color}]{res.status.value}[/{status_color}]", f"{res.duration:.2f}s", res.message
        )

    console.print(table)


@app.command("update")
def update_cmd(
    components: list[str] | None = typer.Argument(None, help="Components to update (default: all)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would update"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update even if current"),
):
    """Unified update command for all thegent components."""
    # For now, update is just an alias for sync with catalog included
    # In the future, it will include dependency updates etc.
    if not components:
        components = ["catalog"]

    sync_cmd(components=components, dry_run=dry_run, force=force)


@app.command("audit")
def audit_cmd():
    """Comprehensive system audit."""
    from thegent.doctor import run_doctor

    # Audit is currently delegated to the existing doctor command
    run_doctor(fix=False)


if __name__ == "__main__":
    app()
