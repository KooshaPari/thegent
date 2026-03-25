"""Thegent 3.0: Unified Agent Orchestration Entry Point.
Consolidates all legacy command sprawl into a clean, logical hierarchy.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from thegent import __version__
from thegent.cli.help_examples import ROOT_HELP_SHORTCUT_BLOCK

console = Console()
app = typer.Typer(
    name="thegent",
    help="Unified Agent Orchestration OS - The Optimal System",
    no_args_is_help=True,
    add_completion=True,
)


def _version_callback(value: bool) -> None:
    if not value:
        return
    console.print(__version__)
    raise typer.Exit()


# Modular Stream Registrations
from thegent.cli.apps.root import register_root_apps

try:
    from thegent.cli.commands.cli_git import app as git_app
except ImportError as exc:
    missing_name = getattr(exc, "name", "")
    if (
        missing_name not in {"thegent_git", "thegent.cli.commands.cli_git"}
        and not missing_name.startswith("thegent.native")
        and "thegent-git" not in str(exc)
    ):
        raise

    git_app = typer.Typer(help="Git Coordination (install thegent-git to enable full git workflows).")

    @git_app.callback(invoke_without_command=True)
    def _git_dependency_missing(ctx: typer.Context) -> None:  # pyright: ignore[reportUnusedFunction] -- typer callback
        """Fail fast when git integration dependency is unavailable."""
        if ctx.invoked_subcommand is not None:
            return
        console.print("[red]Git coordination unavailable: install thegent-git dependency.[/red]")
        raise typer.Exit(1)


register_root_apps(app, git_app)

from thegent.cli.apps.main_shortcuts import register_main_shortcuts

register_main_shortcuts(app, console)


@app.command("session-contract-health-gate", help="Evaluate session contract health gate.")
def session_health_gate_wrapper(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy-ratio", help="Minimum healthy ratio threshold"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    no_worse_than_baseline: bool = typer.Option(False, "--no-worse-than-baseline", help="Check for regression"),
    regression_tolerance: float = typer.Option(0.0, "--regression-tolerance", help="Tolerance for regression"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Evaluate session contract health gate."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_gate_cmd

    output_path = Path(output) if output else None
    session_contract_health_gate_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        min_healthy_ratio=min_healthy_ratio,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-report", help="Generate session contract health report.")
def session_health_report_wrapper(
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    no_worse_than_baseline: bool = typer.Option(False, "--no-worse-than-baseline", help="Check for regression"),
    regression_tolerance: float = typer.Option(0.0, "--regression-tolerance", help="Tolerance for regression"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Generate session contract health report."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_report_cmd

    output_path = Path(output) if output else None
    session_contract_health_report_cmd(
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        format=format,
        policy_profile=policy_profile,
        no_worse_than_baseline=no_worse_than_baseline,
        regression_tolerance=regression_tolerance,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("session-contract-health-trend", help="Session contract health trend analysis.")
def session_health_trend_wrapper(
    payload_type: str = typer.Option(
        "session_contract_health_report",
        "--payload-type",
        help="Payload type to trend (session_contract_health_report, session_contract_health_gate)",
    ),
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Include all sessions (not just current owner)"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag filter"),
    strict: bool = typer.Option(False, "--strict", help="Strict health check mode"),
    policy_profile: str | None = typer.Option(None, "--policy-profile", help="Health policy profile"),
    min_healthy_ratio: float = typer.Option(1.0, "--min-healthy-ratio", help="Minimum healthy ratio threshold"),
    top_blocked: int = typer.Option(25, "--top-blocked", help="Top N blocked rows to include"),
    limit: int = typer.Option(20, "--limit", help="Maximum snapshots to analyze"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json|md"),
    output: str | None = typer.Option(None, "--output", help="Export to file"),
    export_format: str | None = typer.Option(None, "--export-format", help="Export format override"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing export file"),
) -> None:
    """Analyze session contract health trends."""
    from pathlib import Path

    from thegent.cli.commands.session_cmds import session_contract_health_trend_cmd

    output_path = Path(output) if output else None
    session_contract_health_trend_cmd(
        payload_type=payload_type,
        all_sessions=all_sessions,
        owner=owner,
        strict=strict,
        policy_profile=policy_profile,
        min_healthy_ratio=min_healthy_ratio,
        top_blocked=top_blocked,
        limit=limit,
        format=format,
        output=output_path,
        export_format=export_format,
        overwrite=overwrite,
    )


@app.command("domain-map", hidden=True)
def domain_map_compat(
    domain_name: str = typer.Argument(..., help="Domain or subdomain to expose."),
    target: str = typer.Option("http://localhost:3847", "--target", "-t"),
    mode: str = typer.Option("advisor", "--mode"),
    registrar: str = typer.Option("porkbun", "--registrar"),
    dns_provider: str = typer.Option("cloudflare", "--dns-provider"),
    tunnel_name: str = typer.Option("thegent", "--tunnel-name"),
    format: str = typer.Option("rich", "--format", "-F"),
) -> None:
    """Compatibility shim for legacy `thegent domain-map` usage."""
    from thegent.cli.commands.domain_map import domain_map_cmd

    domain_map_cmd(
        domain=domain_name,
        target=target,
        mode=mode,
        registrar=registrar,
        dns_provider=dns_provider,
        tunnel_name=tunnel_name,
        format=format,
    )


@app.command("help", help="Show inline examples for a command.")
def help_cmd(
    command: str = typer.Argument(..., help="Command to show examples for"),
) -> None:
    """Show inline usage examples for COMMAND.

    # @trace WL-040 WP-4004

    Example::

        thegent help run
        thegent help plan
        thegent help doctor
    """
    from thegent.cli.help_examples import show_help_examples

    show_help_examples(command)


@app.command("agent-server", help="Run thegent JSON-RPC agent server over stdio.")
def agent_server_cmd() -> None:
    from thegent.protocols.jsonrpc_agent_server import serve_stdio

    raise typer.Exit(serve_stdio())


@app.callback(invoke_without_command=True)
def main_welcome(
    ctx: typer.Context,
    _version: bool = typer.Option(
        False,
        "--version",
        help="Show thegent version and exit.",
        is_eager=True,
        callback=_version_callback,
    ),
):
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]Thegent 3.0 (Optimal)[/bold cyan]\n"
                "[dim]The Optimized Agent Orchestration System[/dim]\n\n"
                "Key Streams:\n"
                "  [green]thegent run[/green]       Execute agent tasks\n"
                "  [green]thegent sync[/green]      Synchronize system state\n"
                "  [green]thegent audit[/green]     Check system health/risk\n"
                "  [green]thegent plan[/green]      Manage the roadmap\n"
                "  [green]thegent worktree[/green]   Structured worktree governance\n"
                "\n"
                "Team Discovery:\n"
                "  [green]thegent team teammates list[/green] Discover teammate personas\n"
                "\n"
                "Support Commands:\n"
                "  [green]thegent setup[/green]       Run setup wizard\n"
                "  [green]thegent doctor[/green]      Run system doctor checks\n"
                f"{ROOT_HELP_SHORTCUT_BLOCK}\n",
                title="thegent",
                border_style="blue",
            )
        )


if __name__ == "__main__":
    app()
