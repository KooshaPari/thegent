"""Router command: `thegent router status` and related subcommands.

Exposes Phase 3 routing state as CLI output.  The `status` subcommand reads:
1. The routing_audit.jsonl log for recent decisions
2. The in-process RoutingOrchestratorBridge state (if running inside the CLI)
3. ThegentSettings for current hysteresis configuration

WL-012 Phase 3.2
"""

from __future__ import annotations

import orjson as json
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

if TYPE_CHECKING:
    from thegent.config import ThegentSettings
    from thegent.utils.routing_impl.route_executor import RouterStatus

app = typer.Typer(help="Pareto router management commands (Phase 3, WL-012).")


# ---------------------------------------------------------------------------
# `thegent router status`
# ---------------------------------------------------------------------------


@app.command("status")
def router_status(
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output status as JSON."),
    ] = False,
    audit_lines: Annotated[
        int,
        typer.Option(
            "--lines",
            "-n",
            help="Number of recent audit log entries to show.",
        ),
    ] = 10,
    audit_path: Annotated[
        Path | None,
        typer.Option(
            "--audit",
            "-a",
            help="Path to routing_audit.jsonl. Defaults to <session_dir>/routing_audit.jsonl.",
        ),
    ] = None,
) -> None:
    """Show current routing state: hysteresis config, recent decisions, agent quorum."""
    from thegent.config import ThegentSettings
    from thegent.utils.routing_impl.route_executor import read_routing_audit

    settings = ThegentSettings()

    # Resolve audit log path.
    if audit_path is None:
        if settings.router_audit_path:
            resolved_audit = Path(settings.router_audit_path)
        else:
            resolved_audit = Path(settings.session_dir) / "routing_audit.jsonl"
    else:
        resolved_audit = audit_path

    # Read recent audit records.
    audit_records = read_routing_audit(resolved_audit, limit=audit_lines)

    # Build status from audit records.
    status = _build_status_from_audit(audit_records, settings)

    if output_json:
        typer.echo(status.to_json())
    else:
        typer.echo(status.display())
        typer.echo()
        _echo_config(settings)
        typer.echo()
        if audit_records:
            typer.echo(f"Recent decisions (from {resolved_audit}):")
            _echo_audit_table(audit_records)
        else:
            typer.echo(f"No audit records found at: {resolved_audit}")


# ---------------------------------------------------------------------------
# `thegent router config`
# ---------------------------------------------------------------------------


@app.command("config")
def router_config(
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output config as JSON."),
    ] = False,
) -> None:
    """Show current hysteresis and routing configuration (from ThegentSettings)."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cfg = {
        "router_band_width": settings.router_band_width,
        "router_dwell_time": settings.router_dwell_time,
        "router_max_dwell": settings.router_max_dwell,
        "router_override_threshold": settings.router_override_threshold,
        "router_audit_path": settings.router_audit_path or "<session_dir>/routing_audit.jsonl",
        "env_vars": {
            "THGENT_ROUTER_BAND_WIDTH": settings.router_band_width,
            "THGENT_ROUTER_DWELL_TIME": settings.router_dwell_time,
            "THGENT_ROUTER_MAX_DWELL": settings.router_max_dwell,
            "THGENT_ROUTER_OVERRIDE_THRESHOLD": settings.router_override_threshold,
        },
    }
    if output_json:
        typer.echo(json.dumps(cfg, indent=2).decode().decode())
    else:
        typer.echo("Pareto Router Configuration (Phase 3)")
        typer.echo("--------------------------------------")
        for key, val in cfg["env_vars"].items():
            typer.echo(f"  {key}={val}")
        typer.echo()
        typer.echo("Audit log path:")
        typer.echo(f"  {cfg['router_audit_path']}")


# ---------------------------------------------------------------------------
# `thegent router verify`
# ---------------------------------------------------------------------------


@app.command("verify")
def router_verify(
    audit_path: Annotated[
        Path | None,
        typer.Option(
            "--audit",
            "-a",
            help="Path to routing_audit.jsonl to verify.",
        ),
    ] = None,
) -> None:
    """Verify the hash chain integrity of the routing audit log."""
    from thegent.config import ThegentSettings
    from thegent.utils.routing_impl.route_executor import read_routing_audit

    settings = ThegentSettings()

    if audit_path is None:
        if settings.router_audit_path:
            resolved_audit = Path(settings.router_audit_path)
        else:
            resolved_audit = Path(settings.session_dir) / "routing_audit.jsonl"
    else:
        resolved_audit = audit_path

    if not resolved_audit.exists():
        typer.echo(f"Audit log not found: {resolved_audit}", err=True)
        raise typer.Exit(1)

    records = read_routing_audit(resolved_audit, limit=10_000)
    if not records:
        typer.echo("Audit log is empty.")
        raise typer.Exit(0)

    # Verify hash chain.
    import hashlib

    prev_hash = ""
    for i, record in enumerate(records):
        # Recompute hash (ADR-015 pattern: sort_keys, exclude hash field).
        d = {k: v for k, v in record.items() if k != "hash"}
        canonical = json.dumps(d, sort_keys=True, separators=(",", ":").decode().decode())
        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()

        if record.get("hash") != expected_hash:
            typer.echo(
                f"FAIL: Hash mismatch at record {i} "
                f"(decision_id={record.get('decision_id')}): "
                f"expected {expected_hash}, got {record.get('hash')}",
                err=True,
            )
            raise typer.Exit(1)
        if record.get("prev_hash", "") != prev_hash:
            typer.echo(
                f"FAIL: Chain broken at record {i} "
                f"(decision_id={record.get('decision_id')}): "
                f"expected prev_hash={prev_hash}, got {record.get('prev_hash')}",
                err=True,
            )
            raise typer.Exit(1)
        prev_hash = record["hash"]

    typer.echo(f"OK: Chain verified — {len(records)} records, all hashes valid.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_status_from_audit(
    records: list[dict],
    settings: "ThegentSettings",
) -> "RouterStatus":
    """Build a RouterStatus from audit records."""
    from thegent.utils.routing_impl.route_executor import AgentRoutingState, RouterStatus

    # Aggregate by provider (audit records don't have agent IDs,
    # so we group by provider as a proxy).
    providers: dict[str, AgentRoutingState] = {}
    for rec in records:
        provider = rec.get("provider", "unknown")
        if provider not in providers:
            providers[provider] = AgentRoutingState(
                agent_id=provider,
                current_mode="Lifecycle" if provider == "lifecycle" else "TheGent",
                total_decisions=0,
                lifecycle_decisions=0,
                thegent_decisions=0,
                last_rationale="",
            )
        state = providers[provider]
        state.total_decisions += 1
        if provider == "lifecycle":
            state.lifecycle_decisions += 1
        else:
            state.thegent_decisions += 1
        state.last_rationale = f"model={rec.get('model', '?')}, latency={rec.get('latency_ms', '?')}ms"

    agents = list(providers.values())
    total = sum(a.total_decisions for a in agents)
    lc_total = sum(a.lifecycle_decisions for a in agents)
    tg_total = sum(a.thegent_decisions for a in agents)
    lifecycle_pct = (lc_total / total * 100.0) if total > 0 else 0.0
    thegent_pct = (tg_total / total * 100.0) if total > 0 else 0.0

    quorum: str | None = None
    if providers:
        thegent_votes = sum(1 for a in agents if a.thegent_decisions > a.lifecycle_decisions)
        quorum = "TheGent" if thegent_votes >= len(agents) - thegent_votes else "Lifecycle"

    return RouterStatus(
        agents=agents,
        total_decisions=total,
        policy="MajorityWins",
        quorum_decision=quorum,
        lifecycle_pct=lifecycle_pct,
        thegent_pct=thegent_pct,
    )


def _echo_config(settings: "ThegentSettings") -> None:
    """Print hysteresis config summary."""
    typer.echo("Hysteresis Configuration:")
    typer.echo(f"  Band width:          {settings.router_band_width} (THGENT_ROUTER_BAND_WIDTH)")
    typer.echo(f"  Dwell time:          {settings.router_dwell_time}s (THGENT_ROUTER_DWELL_TIME)")
    typer.echo(f"  Max dwell:           {settings.router_max_dwell}s (THGENT_ROUTER_MAX_DWELL)")
    typer.echo(f"  Override threshold:  {settings.router_override_threshold} (THGENT_ROUTER_OVERRIDE_THRESHOLD)")


def _echo_audit_table(records: list[dict]) -> None:
    """Print last N audit records as a table."""
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="Recent Routing Decisions")
        table.add_column("Timestamp", style="dim")
        table.add_column("Decision ID", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Model")
        table.add_column("Latency ms", justify="right")
        table.add_column("Cost USD", justify="right")

        for rec in records[-10:]:
            table.add_row(
                str(rec.get("timestamp", ""))[:19],
                str(rec.get("decision_id", ""))[:8] + "...",
                str(rec.get("provider", "")),
                str(rec.get("model", "")),
                str(rec.get("latency_ms", "")),
                f"{rec.get('cost', 0):.6f}",
            )
        console.print(table)
    except ImportError:
        # Rich not available: plain text fallback.
        typer.echo(f"{'Timestamp':<22} {'Provider':<12} {'Model':<25} {'ms':>6} {'cost':>10}")
        typer.echo("-" * 80)
        for rec in records[-10:]:
            typer.echo(
                f"{str(rec.get('timestamp', ''))[:19]:<22} "
                f"{rec.get('provider', '')!s:<12} "
                f"{rec.get('model', '')!s:<25} "
                f"{rec.get('latency_ms', '')!s:>6} "
                f"{rec.get('cost', 0):>10.6f}"
            )
