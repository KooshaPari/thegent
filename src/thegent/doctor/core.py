"""Doctor module for comprehensive health and preflight checks of thegent environment."""

# Backward compatibility - import from new submodule
from thegent.doctor.checks_env import check_environment as _check_environment_impl
from thegent.doctor.checks_env import check_shim_binaries as _check_shim_binaries_impl

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.doctor_dependencies import check_dependencies as _check_dependencies_impl
from thegent.doctor_models import CheckResult
from thegent.doctor_project_root import detect_project_root
from thegent.doctor_setup_checks import (
    check_configuration as _check_configuration_impl,
    check_connectivity as _check_connectivity_impl,
    check_isolation as _check_isolation_impl,
)
from thegent.doctor_shell_nix import (
    check_nix as _check_nix_impl,
    check_shell as _check_shell_impl,
)
from thegent.infra import run_subprocess_optimized

import psutil


@dataclass
class ProcessInfo:
    """Lightweight process information."""

    pid: int
    name: str
    cmdline: str
    create_time: float
    status: str = "unknown"


console = Console()
_project_root_cache: Path | None = None


def run_doctor(
    fix: bool = False,
    dry_run: bool = False,
    runtime: bool = False,
    network: bool = False,
    processes: bool = False,
    memory: bool = False,
    deps: bool = False,
) -> bool:
    """Run all health checks and report results.

    Args:
        fix: Attempt to fix detected issues
        dry_run: Show what fixes would be applied without making changes
        runtime: Show multi-runtime diagnostics
        network: Check network connectivity
        processes: Check process health
        memory: Check memory usage
        deps: Check dependencies
    """
    console.print(Panel("[bold cyan]Thegent Doctor[/bold cyan]\n[dim]Comprehensive environment health check[/dim]"))

    # Project Root Detection
    project_root = detect_project_root(Path.cwd())

    if project_root != Path.cwd():
        console.print(f"[yellow]Note: Running from sub-directory. Detected project root at: {project_root}[/yellow]\n")
        os.chdir(project_root)

    # Store project_root for use in other functions
    global _project_root_cache
    _project_root_cache = project_root

    results: list[CheckResult] = []

    # @trace WL-040 WP-4005 — spinner wraps the check collection phase
    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as _prog:
        _task = _prog.add_task("Running health checks...", total=None)

        # Category: Dependencies
        results.extend(_check_dependencies(deps=deps))
        _prog.update(_task, description="Checking configuration...")
        results.extend(_check_configuration())
        _prog.update(_task, description="Checking isolation...")
        results.extend(_check_isolation())
        _prog.update(_task, description="Checking connectivity...")
        results.extend(_check_connectivity())
        _prog.update(_task, description="Checking environment...")
        results.extend(_check_environment())
        _prog.update(_task, description="Checking shim binaries...")
        results.extend(_check_shim_binaries())
        _prog.update(_task, description="Checking shell...")
        results.extend(_check_shell())
        _prog.update(_task, description="Checking Nix support...")
        results.extend(_check_nix())
        _prog.update(_task, description="Checking providers & headless...")
        results.extend(_check_providers())
        results.extend(_check_ollama())
        results.extend(_check_headless())
        _prog.update(_task, description="Checking runtime infrastructure...")
        results.extend(_check_runtime_infrastructure())
        _prog.update(_task, description="Checking processes...")
        results.extend(_check_process_leaks())
        _prog.update(_task, description="Checking MCP tools & sessions...")
        results.extend(_check_mcp_tools())
        results.extend(_check_sessions())
        _prog.update(_task, description="Checking project hints...")
        results.extend(_check_project_hints())
        _prog.update(_task, description="Checking performance...")
        results.extend(_check_performance())

    # Apply fixes if requested
    if fix:
        fix_report = _apply_fixes(results, dry_run=dry_run)
        # Display fix report
        if fix_report:
            _display_fix_report(fix_report, dry_run=dry_run)

    # Display results
    success = _display_results(results)

    # Show multi-runtime diagnostics if requested
    if runtime:
        try:
            from thegent.infra.multi_runtime_diagnostics import check_all_runtimes, display_runtime_status

            console.print("\n")
            statuses = check_all_runtimes()
            display_runtime_status(statuses)
        except Exception as e:
            console.print(f"[yellow]Could not run multi-runtime diagnostics: {e}[/yellow]")

    # Show network diagnostics if requested
    if network:
        console.print("\n[bold cyan]Network Diagnostics[/bold cyan]")
        # Network checks are already in _check_connectivity, but we can add more here
        console.print("[dim]Network diagnostics integrated into connectivity checks above[/dim]")

    # Show process diagnostics if requested
    if processes:
        console.print("\n[bold cyan]Process Diagnostics[/bold cyan]")
        # Process checks are already in _check_process_leaks, but we can add more here
        console.print("[dim]Process diagnostics integrated into process leak checks above[/dim]")

    # Show memory diagnostics if requested
    if memory:
        console.print("\n[bold cyan]Memory Diagnostics[/bold cyan]")
        try:
            mem = psutil.virtual_memory()
            console.print(f"Total Memory: {mem.total / (1024**3):.2f} GB")
            console.print(f"Available Memory: {mem.available / (1024**3):.2f} GB")
            console.print(f"Used Memory: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
        except Exception as e:
            console.print(f"[yellow]Could not get memory info: {e}[/yellow]")

    # Show dependency diagnostics if requested
    if deps:
        console.print("\n[bold cyan]Dependency Diagnostics[/bold cyan]")
        # Dependency checks are already in _check_dependencies, but we can add more here
        console.print("[dim]Dependency diagnostics integrated into dependency checks above[/dim]")

    if not success:
        if fix:
            console.print("\n[bold yellow]⚠ Some checks failed. Fixes were attempted where possible.[/bold yellow]")
        else:
            console.print("\n[bold red]✗ Some checks failed. See hints above to fix them.[/bold red]")
            console.print("[dim]Run with --fix to attempt automatic fixes[/dim]")
        console.print("[dim]See docs/guides/TROUBLESHOOTING.md for more help[/dim]")
    else:
        console.print("\n[bold green]✓ All essential checks passed![/bold green]")

    return success


