"""Logical stream: System Integrity and Health Audit."""

import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

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
    from thegent.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=types, fix=fix, severity=severity, format=format))


@app.command("doctor", help="Check system health, environment, and dependencies.")
def audit_doctor(fix: bool = typer.Option(False, "--fix", help="Attempt to fix detected issues")):
    from thegent.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=["doctor"], fix=fix))


@app.command("plan", help="Audit planning continuity, roadmap progress, and PERT risk.")
def audit_plan():
    """Heavy audit of the plan: PLAN.md, WORK_STREAM.md, and DAG consistency."""
    from thegent.cli.commands.cli_sync import audit_cmd_impl

    asyncio.run(audit_cmd_impl(audit_types=["initiative", "plan", "dag"]))


@app.command("security", help="Audit data protection, privacy, and compliance.")
def audit_security(format: str = typer.Option("rich", "--format", "-F")):
    from thegent.cli.commands.cli import compliance_report_cmd, data_protection_cmd

    data_protection_cmd(format=format)
    compliance_report_cmd(format=format)


@app.command("sweep", help="Run policy drift sweep (WP-3005).")
def audit_sweep(format: str = typer.Option("rich", "--format", "-F")):
    from thegent.cli.commands.cli import sweep_cmd

    sweep_cmd(format=format)


@app.command("registry", help="Verify integrity of the execution run registry.")
def audit_registry(format: str = typer.Option("rich", "--format", "-F")):
    from thegent.cli.commands.cli import audit_verify_cmd

    audit_verify_cmd(format=format)


@app.command("fatigue", help="Check for interruption fatigue and alert levels.")
def audit_fatigue():
    from thegent.cli.commands.cli import interruption_list_cmd

    interruption_list_cmd()


@app.command("costs", help="Audit usage costs and resource allocation.")
def audit_costs(format: str = typer.Option("rich", "--format", "-F")):
    from thegent.cli.commands.cli import cost_status_cmd

    cost_status_cmd(format=format)
