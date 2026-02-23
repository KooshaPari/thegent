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
def _is_process_actively_working(pid: int, min_cpu_percent: float = 0.1, min_io_bytes: int = 1024) -> tuple[bool, str]:
    """
    Check if a process is actively working (not stuck) by monitoring CPU and I/O activity.

    Returns (is_active, reason) where is_active=True means process is working.
    A process is considered active if:
    - CPU usage > min_cpu_percent over a short interval, OR
    - I/O activity detected (read/write bytes), OR
    - Process has network connections, OR
    - Process is long-running (>1 hour) - assumed active (user's chats run for hours)
    """
    try:
        proc = psutil.Process(pid)

        # Check process status
        status = proc.status()
        if status == psutil.STATUS_ZOMBIE:
            return False, "zombie process"

        # Check if it's been running for a while - long-running sessions are OK
        create_time = proc.create_time()
        runtime = time.time() - create_time
        if runtime > 3600:  # Running for > 1 hour
            # For long-running processes, be more lenient - assume active unless clearly stuck
            # Check for network connections as a sign of activity
            try:
                connections = proc.net_connections()
                if connections:
                    return (
                        True,
                        f"long-running session ({runtime / 3600:.1f}h) with {len(connections)} network connections",
                    )
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            # Long-running with no obvious activity - still assume active (user's chats run for hours)
            return True, f"long-running session ({runtime / 3600:.1f}h, assumed active)"

        # For shorter runs, check for actual activity
        # Sample CPU usage over short interval (0.5s)
        try:
            cpu_percent = proc.cpu_percent(interval=0.5)
            if cpu_percent > min_cpu_percent:
                return True, f"CPU active ({cpu_percent:.1f}%)"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # Check I/O counters (io_counters is Linux/Windows only; not available on macOS)
        try:
            io_getter = getattr(proc, "io_counters", None)
            if io_getter is not None:
                io_counters = io_getter()
                if io_counters:
                    read_bytes = io_counters.read_bytes
                    write_bytes = io_counters.write_bytes
                    if read_bytes > min_io_bytes or write_bytes > min_io_bytes:
                        return True, f"I/O active (R:{read_bytes} W:{write_bytes})"
        except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
            pass

        # Check if process has network connections (indicates activity)
        try:
            connections = proc.net_connections()
            if connections:
                return True, f"network active ({len(connections)} connections)"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # If process is running/sleeping but no activity detected and runtime < 1 hour
        # Only flag as stuck if runtime > 5 minutes AND no activity
        if runtime > 300:  # > 5 minutes
            return False, "no recent activity detected (may be stuck)"

        # Very short runtime - assume active
        return True, f"recently started ({runtime:.0f}s, assumed active)"
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return False, f"cannot access process: {e}"
    except Exception as e:
        return False, f"error checking process: {e}"


def _find_stuck_processes(command_patterns: list[str], max_age_seconds: int = 300) -> list[tuple[int, str, str]]:
    """
    Find processes matching command patterns that appear to be stuck (not actively working).

    Uses fast process monitor for better performance.

    Returns list of (pid, command, reason) for stuck processes.
    Only flags processes that:
    - Match the command pattern
    - Have been running > max_age_seconds
    - Show no recent activity (CPU, I/O, network)
    """
    stuck = []
    now = time.time()

    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            if not any(pattern in cmdline for pattern in command_patterns):
                continue

            pid = proc.info["pid"]
            runtime = now - proc.info["create_time"]

            if runtime < max_age_seconds:
                continue

            is_active, reason = _is_process_actively_working(pid)
            if not is_active:
                stuck.append((pid, cmdline[:100], reason))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return stuck


def _extract_process_info(proc: "psutil.Process") -> "ProcessInfo | None":
    """Extract ProcessInfo from psutil.Process. WP-P2: Fix PERF203."""
    try:
        info = proc.info
        return ProcessInfo(
            pid=info["pid"],
            name=info.get("name", "unknown"),
            cmdline=" ".join(info.get("cmdline", []) or []),
            create_time=info.get("create_time", 0),
            status=info.get("status", "unknown"),
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _display_results(results: list[CheckResult]) -> bool:
    table = Table(title="Doctor Results", box=None, show_header=True)
    table.add_column("Category", style="dim")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Severity")
    table.add_column("Message")

    # All failures count against success - no features are optional
    all_ok = True
    severity_labels = {
        "info": "[cyan]info[/cyan]",
        "warning": "[yellow]warning[/yellow]",
        "error": "[red]error[/red]",
        "critical": "[bold red]critical[/bold red]",
    }
    for r in results:
        status_str = "[green]ok[/green]"
        if r.status == "warn":
            status_str = "[yellow]warn[/yellow]"
        elif r.status == "fail":
            status_str = "[red]fail[/red]"
            all_ok = False

        severity_str = severity_labels.get(r.severity, r.severity)
        table.add_row(r.category, r.name, status_str, severity_str, r.message)
        if r.fix_hint:
            table.add_row("", "", "", "", f"[dim]Hint: {r.fix_hint}[/dim]")
        if r.details:
            table.add_row("", "", "", "", f"[dim]{r.details}[/dim]")

    console.print(table)

    status_counts = {
        "ok": sum(1 for r in results if r.status == "ok"),
        "warn": sum(1 for r in results if r.status == "warn"),
        "fail": sum(1 for r in results if r.status == "fail"),
    }
    severity_counts = {
        "info": sum(1 for r in results if r.severity == "info"),
        "warning": sum(1 for r in results if r.severity == "warning"),
        "error": sum(1 for r in results if r.severity == "error"),
        "critical": sum(1 for r in results if r.severity == "critical"),
    }
    console.print(
        "[bold]Summary:[/bold] "
        f"{status_counts['ok']} ok, {status_counts['warn']} warn, {status_counts['fail']} fail | "
        "severity "
        f"info={severity_counts['info']}, warning={severity_counts['warning']}, "
        f"error={severity_counts['error']}, critical={severity_counts['critical']}"
    )

    actionable_hints: list[str] = []
    normalized_hints: set[str] = set()
    hint_pairs: list[tuple[str, str]] = []

    def _normalize_hint_for_dedupe(raw_hint: str) -> str:
        collapsed = " ".join(raw_hint.split()).casefold().strip()
        collapsed = re.sub(r"^(?:[-*]\s+|\d+[.)]\s+)", "", collapsed)
        return collapsed.rstrip(" .;:!?")

    for r in results:
        if r.status in {"warn", "fail"} and r.fix_hint:
            normalized_hint = _normalize_hint_for_dedupe(r.fix_hint)
            if normalized_hint not in normalized_hints:
                normalized_hints.add(normalized_hint)
                hint_pairs.append((normalized_hint, r.fix_hint.strip()))
    actionable_hints = [hint for _, hint in sorted(hint_pairs, key=lambda pair: pair[0])]
    if actionable_hints:
        console.print("[bold]Actionable hints:[/bold]")
        shown_hints = actionable_hints[:3]
        for idx, hint in enumerate(shown_hints, start=1):
            console.print(f"[dim]- [{idx}/{len(shown_hints)}] {hint}[/dim]")
        remaining_hints = len(actionable_hints) - len(shown_hints)
        if remaining_hints > 0:
            console.print(f"[dim]- ... and {remaining_hints} more actionable hint(s)[/dim]")

    # Provider Matrix Summary (ROB-016)
    providers = [r for r in results if r.category == "Providers"]
    if providers:
        matrix = Table(title="Provider Success Matrix", box=None, show_header=True)
        matrix.add_column("Provider", style="bold")
        matrix.add_column("Validated", justify="center")
        matrix.add_column("Models", justify="right")

        for p in providers:
            name = p.name.replace("Provider: ", "")
            status = "✅" if p.status == "ok" else "❌" if p.status == "fail" else "⚠️"
            if "(" in p.message and ")" in p.message:
                models_col = p.message.split("(")[-1].replace(")", "").replace(" models", "").strip()
            else:
                models_col = p.message if p.status != "ok" else "—"
            matrix.add_row(name, status, models_col)

        console.print(Panel(matrix, title="Governance Dashboard"))

    return all_ok
