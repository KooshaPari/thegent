"""Logical stream: System Integrity and Health Audit."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

console = Console()
app = typer.Typer(help="Audit system health, security, and planning risk.")


@app.command("all", help="Run comprehensive system health, security, and planning audit.")
def audit_all(
    types: list[str] | None = typer.Option(None, "--type", "-t", help="Specific audit types to run"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues automatically"),
    severity: str = typer.Option(
        "all", "--severity", "-s", help="Minimum severity to show (low|medium|high|critical|all)"
    ),
    format: str = typer.Option("rich", "--format", "-F", help="Output format (rich|json)"),
):
    from phenotype_thegent_cli.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=types, fix=fix, severity=severity, format=format))


@app.command("doctor", help="Check system health, environment, and dependencies.")
def audit_doctor(fix: bool = typer.Option(False, "--fix", help="Attempt to fix detected issues")):
    from phenotype_thegent_cli.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=["doctor"], fix=fix))


@app.command("plan", help="Audit planning continuity, roadmap progress, and PERT risk.")
def audit_plan():
    """Heavy audit of the plan: PLAN.md, WORK_STREAM.md, and DAG consistency."""
    from phenotype_thegent_cli.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=["initiative", "plan", "dag"]))


@app.command("security", help="Audit data protection, privacy, and compliance.")
def audit_security(format: str = typer.Option("rich", "--format", "-F")):
    from phenotype_thegent_cli.cli.commands.cli import compliance_report_cmd, data_protection_cmd

    data_protection_cmd(format=format)
    compliance_report_cmd(format=format)


@app.command("sweep", help="Run policy drift sweep (WP-3005).")
def audit_sweep(format: str = typer.Option("rich", "--format", "-F")):
    from phenotype_thegent_cli.cli.commands.cli import sweep_cmd

    sweep_cmd(format=format)


@app.command("registry", help="Verify integrity of the execution run registry.")
def audit_registry(format: str = typer.Option("rich", "--format", "-F")):
    from phenotype_thegent_cli.cli.commands.cli import audit_verify_cmd

    audit_verify_cmd(format=format)


@app.command("fatigue", help="Check for interruption fatigue and alert levels.")
def audit_fatigue():
    from phenotype_thegent_cli.cli.commands.cli import interruption_list_cmd

    interruption_list_cmd()


@app.command("costs", help="Audit usage costs and resource allocation.")
def audit_costs(format: str = typer.Option("rich", "--format", "-F")):
    from phenotype_thegent_cli.cli.commands.cli import cost_status_cmd

    cost_status_cmd(format=format)


# ---------------------------------------------------------------------------
# Git Journal Commands (Micro-commit audit trail)
# ---------------------------------------------------------------------------


@app.command("journal", help="Manage git journal for micro-commit audit trail.")
def audit_journal(
    action: str = typer.Argument("list", help="Action (list|status|snapshot|prune|show|watch|attest|stats|stream)"),
    session_id: str | None = typer.Option(None, "--session", "-s", help="Session ID"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    max_age: int = typer.Option(30, "--max-age", "-a", help="Max age in days for prune"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Enable real-time watching"),
    attest: bool = typer.Option(False, "--attest", help="Enable cryptographic attestation"),
    batch_size: int = typer.Option(10, "--batch", "-b", help="Batch size for commits"),
    enhanced: bool = typer.Option(True, "--enhanced/--basic", help="Use enhanced journal"),
    stream: bool = typer.Option(False, "--stream", help="Enable Kafka event streaming"),
    follow: bool = typer.Option(False, "--follow", help="Keep watch command attached until interrupted."),
    bootstrap_servers: str = typer.Option("localhost:9092", "--kafka-servers", help="Kafka bootstrap servers"),
    topic: str = typer.Option("thegent-audit-events", "--kafka-topic", help="Kafka topic for events"),
):
    """Manage git journal for micro-commit audit trail.

    The git journal creates micro-commits for every file change using
    git refs that are never pushed to remote. This provides a complete
    local audit trail including secrets and sensitive files.

    Actions:
        list     - List all audit sessions
        status   - Show journal status for current session
        snapshot - Create a snapshot of current working tree
        prune    - Remove old audit sessions
        show     - Show audit log for a session
        watch    - Start real-time file watching
        attest   - Show attestations for a session
        stats    - Show performance statistics

    Enhanced Features (--enhanced):
        - Native secret scanner integration
        - Real-time file watching (watchman/fswatch/FSMonitor)
        - Cryptographic attestation (SHA-256)
        - Batching for performance
    """
    repo_path = Path(path).resolve()

    # Always use GitJournalEnhanced since enhanced=True by default
    JournalClass = GitJournalEnhanced

    if action == "list":
        sessions = JournalClass.list_sessions(repo_path)

        if not sessions:
            console.print("[yellow]No audit sessions found[/yellow]")
            return

        table = Table(title="Git Journal Sessions (Local Only)")
        table.add_column("Session ID", style="cyan")
        table.add_column("Last Commit", style="green")
        table.add_column("SHA", style="dim")

        for session in sessions:
            table.add_row(
                session["session_id"],
                session["last_commit"],
                session["sha"][:8],
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(sessions)} sessions (never pushed to remote)[/dim]")

    elif action == "status":
        if not session_id:
            console.print("[red]Error: --session required for status[/red]")
            raise typer.Exit(1)

        journal = JournalClass(repo_path, session_id)
        log_entries = journal.get_audit_log()

        if not log_entries:
            console.print(f"[yellow]No entries for session {session_id}[/yellow]")
            return

        table = Table(title=f"Journal Status: {session_id}")
        table.add_column("SHA", style="dim")
        table.add_column("Message", style="green")
        table.add_column("Timestamp", style="cyan")

        for entry in log_entries[:20]:  # Show last 20
            table.add_row(
                entry["sha"][:8],
                entry["message"][:60],
                entry["timestamp"],
            )

        console.print(table)
        console.print(f"\n[dim]Total commits: {len(log_entries)}[/dim]")

    elif action == "snapshot":
        if not session_id:
            import uuid

            session_id = f"manual-{uuid.uuid4().hex[:8]}"
            console.print(f"[cyan]Creating session: {session_id}[/cyan]")

        journal = JournalClass(
            repo_path,
            session_id,
            enable_watching=watch,
            enable_attestation=attest,
            batch_size=batch_size,
        )
        sha = journal.record_snapshot("manual snapshot")

        console.print(f"[green]Created snapshot: {sha[:8]}[/green]")
        console.print(f"[dim]Session: {session_id}[/dim]")
        console.print("[dim]This audit trail is local-only (never pushed)[/dim]")

        if enhanced:
            stats = journal.get_performance_stats()
            console.print(
                f"\n[dim]Enhanced mode: native_scanner={stats['native_scanner']} watcher={stats['watcher']}[/dim]"
            )

    elif action == "prune":
        pruned = JournalClass.prune_old_sessions(repo_path, max_age)
        console.print(f"[green]Pruned {pruned} old audit sessions[/green]")

    elif action == "show":
        if not session_id:
            console.print("[red]Error: --session required for show[/red]")
            raise typer.Exit(1)

        journal = JournalClass(repo_path, session_id)
        log_entries = journal.get_audit_log()

        if not log_entries:
            console.print(f"[yellow]No entries for session {session_id}[/yellow]")
            return

        console.print(f"[bold]Audit Log: {session_id}[/bold]\n")

        for entry in log_entries:
            console.print(f"[dim]{entry['sha'][:8]}[/dim] {entry['timestamp']}")
            console.print(f"  {entry['message']}\n")

    elif action == "watch":
        if not session_id:
            import uuid

            session_id = f"watch-{uuid.uuid4().hex[:8]}"
            console.print(f"[cyan]Creating watch session: {session_id}[/cyan]")

        journal = JournalClass(
            repo_path,
            session_id,
            enable_watching=True,
            enable_attestation=attest,
            batch_size=batch_size,
        )

        console.print("[green]Starting real-time file watching...[/green]")
        console.print(f"[dim]Session: {session_id}[/dim]")
        console.print(f"[dim]Repository: {repo_path}[/dim]")

        stats = journal.get_performance_stats()
        console.print(f"[dim]Watcher: {stats['watcher'] or 'none available'}[/dim]")

        if stats["watcher"]:
            journal.start_watching()
            if not follow:
                console.print("[green]Watcher started in detached mode.[/green]")
                console.print("[dim]Re-run with --follow to keep this command attached.[/dim]")
                return
            console.print("[green]Watching for changes (Ctrl+C to stop)...[/green]")
            try:
                import time

                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping watcher...[/yellow]")
                sha = journal.finalize_session("watcher stopped")
                console.print(f"[green]Finalized session: {sha[:8]}[/green]")
        else:
            console.print("[yellow]No file watcher available. Install watchman or fswatch.[/yellow]")

    elif action == "attest":
        if not session_id:
            console.print("[red]Error: --session required for attest[/red]")
            raise typer.Exit(1)

        journal = JournalClass(repo_path, session_id, enable_attestation=True)
        attestations = journal.get_attestations()

        if not attestations:
            console.print(f"[yellow]No attestations for session {session_id}[/yellow]")
            return

        table = Table(title=f"Attestations: {session_id}")
        table.add_column("Commit", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Algorithm", style="dim")
        table.add_column("Verified", style="yellow")

        for att in attestations:
            verified = journal.verify_attestation(att)
            table.add_row(
                att["commit_sha"][:8],
                att["timestamp"],
                att["algorithm"],
                "✓" if verified else "✗",
            )

        console.print(table)

    elif action == "stats":
        if not session_id:
            console.print("[red]Error: --session required for stats[/red]")
            raise typer.Exit(1)

        journal = JournalClass(repo_path, session_id)
        stats = journal.get_performance_stats()

        table = Table(title=f"Journal Stats: {session_id}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key, str(value))

        console.print(table)

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Valid actions: list, status, snapshot, prune, show, watch, attest, stats")
        raise typer.Exit(1)
