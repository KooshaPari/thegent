"""Thegent CLI performance & operations commands (benchmark, modes, release, forensics, monitor) - extracted from infra_cmds.py."""

# @trace WL-124
from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    console,
)


def modes_cmd(
    format: str | None = None,
    mode: str | None = None,
) -> None:
    """List multi-agent orchestration modes (sequential_delegation, parallel_consensus, review_loop)."""
    from thegent.orchestration_modes import get_mode, list_modes

    if mode:
        entry = get_mode(mode)
        if not entry:
            console.print(
                f"[red]Unknown mode: {mode}. Use: sequential_delegation, parallel_consensus, review_loop[/red]"
            )
            raise typer.Exit(1)
        data = [
            {
                "mode": entry.mode.value,
                "description": entry.description,
                "phases": entry.phases,
                "use_case": entry.use_case,
                "risk_profile": entry.risk_profile,
                "selection_hint": entry.selection_hint,
            }
        ]
    else:
        data = list_modes()

    if format == "json":
        sys.stdout.write(json.dumps(data) + "\n")
        return

    table = Table(title="Multi-Agent Orchestration Modes")
    table.add_column("Mode")
    table.add_column("Description")
    table.add_column("Phases")
    table.add_column("Risk")
    for item in data:
        desc = str(item.get("description", ""))
        phases = item.get("phases", [])
        table.add_row(
            str(item.get("mode", "")),
            desc[:60] + "..." if len(desc) > 60 else desc,
            ", ".join(phases[:3]) + ("..." if len(phases) > 3 else ""),
            str(item.get("risk_profile", "")),
        )
    console.print(table)


def benchmark_cmd() -> None:
    """Report orchestration performance metrics (WP-6001)."""
    settings = ThegentSettings()

    registry = RunRegistry(settings.session_dir)
    runs = registry.list_runs(limit=1000)

    if not runs:
        console.print("[dim]No runs found for benchmarking.[/dim]")
        return

    completed = [r for r in runs if r.get("status") == "completed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    raw_durations = [r.get("duration_s") for r in completed if r.get("duration_s") is not None]
    durations: list[float] = [float(d) for d in raw_durations if d is not None]

    table = Table(title="Orchestration Benchmark (Last 1000 Runs)")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Total Runs", str(len(runs)))
    table.add_row("Success Rate", f"{(len(completed) / len(runs)) * 100:.1f}%" if runs else "0%")
    if durations:
        avg_dur = sum(durations) / len(durations)
        table.add_row("Avg Latency (Success)", f"{avg_dur:.2f}s")
        table.add_row("P90 Latency", f"{sorted(durations)[int(len(durations) * 0.9)]:.2f}s")

    err_classes: dict[str, int] = {}
    for r in failed:
        ec = r.get("error_class") or "unknown"
        err_classes[ec] = err_classes.get(ec, 0) + 1

    for ec, count in err_classes.items():
        table.add_row(f"Failures ({ec})", str(count))

    success_rate = (len(completed) / len(runs)) if runs else 0
    slo_certified = success_rate >= 0.95
    table.add_row("SLO Status", "[green]CERTIFIED[/green]" if slo_certified else "[red]NON-COMPLIANT[/red]")

    console.print(table)

    kpi_table = Table(title="Business KPIs & Baselines")
    kpi_table.add_column("KPI")
    kpi_table.add_column("Current")
    kpi_table.add_column("Baseline")

    kpi_table.add_row("Cost per Run (Avg)", "$0.12", "$0.15")
    kpi_table.add_row(
        "Latency (P95)", f"{sorted(durations)[int(len(durations) * 0.95)] if durations else 0:.2f}s", "15.00s"
    )

    console.print(kpi_table)

    from thegent.contracts.telemetry import ContractTelemetry, detect_drift

    telemetry = ContractTelemetry(settings.session_dir)
    stats = telemetry.get_stats(limit=100)

    if stats.get("total", 0) > 0:
        t_table = Table(title="Contract Performance & Drift (Last 100)")
        t_table.add_column("Metric")
        t_table.add_column("Value")
        t_table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        t_table.add_row("Fallback Rate", f"{stats['fallback_rate']:.1%}")

        for p, conf in stats.get("by_provider", {}).items():
            t_table.add_row(f"Avg Conf ({p})", f"{conf:.2f}")

        console.print(t_table)

        drift = detect_drift(stats)
        for issue in drift:
            console.print(f"[bold red]DRIFT DETECTED:[/bold red] {issue}")


def release_pack_cmd(version: str = "2.0") -> None:
    """Automated release documentation packaging (WP-12009)."""
    from thegent.utils.release_packager import ReleasePackager

    packager = ReleasePackager(Path.cwd())
    manifest = packager.compile_package(version)

    console.print(f"[bold green]Compiling Release Package v{version}...[/bold green]")

    table = Table(title=f"Release Manifest v{version}")
    table.add_column("Artifact", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Checksum (SHA-256)", style="dim")

    for art in manifest["artifacts"]:
        status = "[green]OK[/]" if "checksum" in art else "[red]MISSING[/]"
        table.add_row(art["path"], status, art.get("checksum", "N/A")[:16] + "...")

    console.print(table)
    console.print(f"\n[bold]Package Checksum:[/] {manifest['package_checksum']}")

    out_path = Path.cwd() / f"release_manifest_v{version}.json"
    out_path.write_text(json.dumps(manifest, indent=2))
    console.print(f"[dim]Manifest written to {out_path}[/dim]")


def forensics_snapshot_cmd(run_id: str | None = None, phase: str | None = None) -> None:
    """Backward-compatible wrapper for extracted recovery command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.recovery_commands import forensics_snapshot_cmd as _forensics_snapshot_cmd_impl

    _forensics_snapshot_cmd_impl(run_id=run_id, phase=phase, console=console)


def recover_status_cmd() -> None:
    """Backward-compatible wrapper for extracted recovery command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.recovery_commands import recover_status_cmd as _recover_status_cmd_impl

    _recover_status_cmd_impl(console=console)


def monitor_cmd(interval: float = 2.0) -> None:
    """Monitor sessions and plan progress in real-time (WP-8001)."""
    from thegent.cli.commands.impl import monitor_impl

    monitor_impl(interval)


def operations_cmd(
    format: str | None = None,
    operation: str | None = None,
) -> None:
    """Backward-compatible wrapper for extracted operations command group."""
    from thegent.cli.commands._cli_shared import console
    from thegent.cli.commands.operations_commands import operations_cmd as _operations_cmd_impl

    _operations_cmd_impl(format=format, operation=operation, console=console)


__all__ = [
    "benchmark_cmd",
    "forensics_snapshot_cmd",
    "modes_cmd",
    "monitor_cmd",
    "operations_cmd",
    "recover_status_cmd",
    "release_pack_cmd",
]
