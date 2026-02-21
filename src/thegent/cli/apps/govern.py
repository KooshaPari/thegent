"""Logical stream: Governance approvals and escalation controls."""

from __future__ import annotations

import json

import typer
from rich.console import Console

console = Console()

app = typer.Typer(help="Governance controls: approvals, rejections, and escalation operations.")


@app.command("approve", help="Approve a paused/escalated run for continuation.")
def govern_approve(
    run_id: str = typer.Argument(..., help="Run ID to approve"),
    reason: str | None = typer.Option(None, "--reason", "-r", help="Approval reason"),
) -> None:
    from thegent.cli.commands.impl import govern_approve_impl
    from thegent.cli.services.governance import govern_get_pending_approval_impl
    from thegent.governance.diff_renderer import DiffPayload, DiffRenderer

    try:
        pending = govern_get_pending_approval_impl(run_id=run_id)
        unified_diff = str(pending.get("unified_diff") or "")
        if unified_diff:
            payload = DiffPayload(before="", after="", unified_diff=unified_diff)
            console.print("[bold cyan]Review Diff:[/bold cyan]")
            console.print(f"[dim]{DiffRenderer.render_summary(payload)}[/dim]")
            console.print(DiffRenderer.render_ansi(payload))
        else:
            console.print("[dim]No unified diff available for this approval request.[/dim]")
        if reason is None:
            reason = typer.prompt("Approval reason", default="approved")
        result = govern_approve_impl(run_id=run_id, reason=reason)
        console.print(f"[green]Approved:[/green] {result['run_id']}")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command("reject", help="Reject a paused/escalated run and record reason.")
def govern_reject(
    run_id: str = typer.Argument(..., help="Run ID to reject"),
    reason: str = typer.Option("rejected", "--reason", "-r", help="Rejection reason"),
) -> None:
    from thegent.cli.commands.impl import govern_reject_impl

    try:
        result = govern_reject_impl(run_id=run_id, reason=reason)
        console.print(f"[yellow]Rejected:[/yellow] {result['run_id']}")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command("vet", help="Evaluate a run against governance vetter checks.")
def govern_vet(
    run_id: str = typer.Argument(..., help="Run ID to vet"),
    policy: str = typer.Option("default", "--policy", help="Vetter policy name"),
    session: str | None = typer.Option(None, "--session", help="Override session directory path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview checks without executing"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON result"),
) -> None:
    from thegent.cli.commands.impl import govern_vet_impl

    try:
        result = govern_vet_impl(run_id=run_id, policy=policy, session=session, dry_run=dry_run)
        if json_output:
            typer.echo(json.dumps(result, indent=2))
            return

        console.print(f"[cyan]Run:[/cyan] {result['run_id']}")
        console.print(f"[cyan]Policy:[/cyan] {result['policy']}")
        console.print(f"[cyan]Verdict:[/cyan] {result['verdict']}")
        for check in result.get("checks", []):
            status = "pass" if check.get("passed") else ("dry-run" if check.get("passed") is None else "fail")
            console.print(f"- {check.get('check_name')}: {status}")
        if result.get("verdict") == "rejected":
            raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command("register-host", help="Register a new host for remote agent harness execution.")
def govern_register_host(
    host_id: str = typer.Argument(..., help="Unique host identifier"),
    harness: str = typer.Argument(..., help="Harness type (cursor, codex, claude, ante, droid)"),
    prefix: str = typer.Option("", "--prefix", "-p", help="Command prefix (e.g., 'ssh user@host')"),
) -> None:
    """Register a new host device for remote harness execution."""
    from thegent.cli.commands.impl import harness_register_host_impl

    result = harness_register_host_impl(
        host_id=host_id,
        harness=harness,
        command_prefix=prefix,
    )

    if result.get("success"):
        console.print(f"[green]Registered:[/green] {host_id} ({harness})")
    else:
        console.print(f"[red]Error:[/red] {result.get('error', 'Unknown error')}")


@app.command("resolve-config", help="Resolve configuration overrides for a tenant or session.")
def govern_resolve_config(
    tenant_id: str | None = typer.Option(None, "--tenant", help="Tenant ID"),
    session_id: str | None = typer.Option(None, "--session", help="Session ID"),
    key: str | None = typer.Option(None, "--key", "-k", help="Specific config key to resolve"),
) -> None:
    """Resolve configuration overrides for a tenant or session."""
    from thegent.mcp.server.tools_runtime import config_resolve_impl

    result = config_resolve_impl(
        tenant_id=tenant_id,
        session_id=session_id,
        overrides={"key": key} if key else {},
    )

    import json
    if result.get("success"):
        console.print(json.dumps(result.get("config", {}), indent=2))
    else:
        console.print(f"[red]Error:[/red] {result.get('error', 'Unknown')}")


@app.command("negotiate", help="Negotiate a contract version with the agent.")
def govern_negotiate(
    contract_id: str = typer.Argument(..., help="Contract ID to negotiate"),
    versions: str = typer.Option(..., "--versions", "-v", help="Comma-separated supported versions"),
) -> None:
    """Negotiate a contract version."""
    from thegent.mcp.server.tools_runtime import negotiate_contract_impl

    version_list = [v.strip() for v in versions.split(",")]
    result = negotiate_contract_impl(
        contract_id=contract_id,
        supported_versions=version_list,
    )

    import json
    if result.get("success"):
        console.print(json.dumps(result.get("result", {}), indent=2))
    else:
        console.print(f"[red]Error:[/red] {result.get('error', 'Unknown')}")
