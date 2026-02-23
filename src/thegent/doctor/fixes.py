"""Doctor module for comprehensive health and preflight checks of thegent environment."""

# Backward compatibility - import from new submodule
from thegent.doctor.checks_env import check_environment as _check_environment_impl
from thegent.doctor.checks_env import check_shim_binaries as _check_shim_binaries_impl

import os
import re
import shutil
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
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


def _apply_fixes(results: list[CheckResult], dry_run: bool = False) -> list[dict]:
    """Attempt to automatically fix issues based on fix_hint strings.

    Args:
        results: List of CheckResult objects from health checks
        dry_run: If True, only show what would be fixed without making changes

    Returns:
        List of dicts containing fix report entries with: check_name, status, action, result
    """
    fix_report: list[dict] = []
    fixes_applied = 0
    fixes_failed = 0

    mode_text = "Would apply (dry-run)" if dry_run else "Attempting automatic fixes"
    console.print(f"\n[bold cyan]{mode_text}...[/bold cyan]\n")

    fixable = [r for r in results if r.status in ("fail", "warn") and r.fix_hint]
    if not fixable:
        console.print("[dim]No fixable issues found.[/dim]")
        return fix_report

    for r in results:
        if r.status in ("fail", "warn") and r.fix_hint:
            # Parse fix hints and attempt fixes
            hint = r.fix_hint.strip()
            fix_action = ""
            fix_result = ""

            # Handle mkdir -p (e.g. "Create manually: mkdir -p /path")
            if "mkdir" in hint and "-p" in hint:
                m = re.search(r"mkdir\s+-p\s+(\S+)", hint)
                if m:
                    path = Path(m.group(1)).expanduser()
                    fix_action = f"mkdir -p {path}"
                    if not dry_run:
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            fixes_applied += 1
                            console.print(f"[green]  ✓ Fixed: {r.name} (created {path})[/green]")
                            r.status = "ok"
                            r.message = f"Created: {path}"
                            fix_result = "success"
                        except Exception as e:
                            fixes_failed += 1
                            console.print(f"[red]  ✗ Failed: {r.name} - {e}[/red]")
                            fix_result = f"failed: {e}"
                    else:
                        console.print(f"[cyan]  ↪ Dry-run: {r.name} would create {path}[/cyan]")
                        fix_result = "dry-run: would create"
                    fix_report.append(
                        {
                            "check_name": r.name,
                            "category": r.category,
                            "status": "success" if fix_result == "success" or "dry-run" in fix_result else "failed",
                            "action": fix_action,
                            "result": fix_result,
                        }
                    )
                    continue

            # Skip hints that require manual intervention
            if any(
                skip in hint.lower()
                for skip in ["install", "download", "check", "ensure", "create manually", "move", "add"]
            ):
                if "run:" in hint.lower() or "thegent" in hint.lower():
                    # These are actionable commands
                    pass
                else:
                    fix_report.append(
                        {
                            "check_name": r.name,
                            "category": r.category,
                            "status": "skipped",
                            "action": hint,
                            "result": "manual intervention required",
                        }
                    )
                    continue

            # Extract command from fix hints
            if "run:" in hint.lower() or (
                ":" in hint and any(cmd in hint.lower() for cmd in ["thegent", "mkdir", "chmod"])
            ):
                # Extract command after "Run:" or "run:" or direct commands
                if "run:" in hint.lower():
                    parts = hint.split(":", 1)
                    cmd_str = parts[1].strip() if len(parts) > 1 else hint
                # Handle direct commands like "Fix permissions: chmod 755 ..."
                elif ":" in hint:
                    cmd_str = hint.split(":", 1)[1].strip()
                else:
                    cmd_str = hint

                # Handle multiple commands separated by semicolons
                commands = [c.strip() for c in cmd_str.split(";")]

                for cmd in commands:
                    if not cmd:
                        continue

                    # Parse command into parts
                    cmd_parts = cmd.split()
                    if not cmd_parts:
                        continue

                    # Skip dangerous commands, except for specific safe removals
                    dangerous = ["rm", "delete", "remove", "uninstall", "kill"]
                    is_safe_removal = False
                    if cmd_parts[0].lower() == "rm" and len(cmd_parts) == 2:
                        target_file = Path(cmd_parts[1]).expanduser()
                        safe_targets = [Path.home() / ".local" / "bin" / "ps"]
                        if any(target_file == safe for safe in safe_targets):
                            is_safe_removal = True

                    if any(d in cmd_parts[0].lower() for d in dangerous) and not is_safe_removal:
                        fix_report.append(
                            {
                                "check_name": r.name,
                                "category": r.category,
                                "status": "skipped",
                                "action": cmd,
                                "result": "dangerous - skipped",
                            }
                        )
                        continue

                    fix_action = cmd
                    # Execute safe commands  # @trace WL-040 WP-4005
                    try:
                        if dry_run:
                            console.print(f"[cyan]  ↪ Dry-run: {r.name} would run: {cmd}[/cyan]")
                            fix_result = "dry-run: would execute"
                        else:
                            console.print(f"[dim]  Fixing {r.name}: {cmd}[/dim]")

                            # Handle thegent commands specially
                            if cmd_parts[0] == "thegent":
                                result = run_subprocess_optimized(
                                    cmd_parts,
                                    capture_output=True,
                                    timeout=30,
                                    cwd=_project_root_cache or None,
                                )
                                if result.returncode == 0:
                                    fixes_applied += 1
                                    console.print(f"[green]  ✓ Fixed: {r.name}[/green]")
                                    fix_result = "success"
                                else:
                                    fixes_failed += 1
                                    stderr_text = (
                                        result.stderr
                                        if isinstance(result.stderr, str)
                                        else (result.stderr.decode("utf-8", errors="replace") if result.stderr else "")
                                    )
                                    console.print(f"[red]  ✗ Failed: {r.name} - {stderr_text[:100]}[/red]")
                                    fix_result = f"failed: {stderr_text[:100]}"
                            else:
                                # For other commands, check if they're safe to run
                                safe_commands = ["mkdir", "chmod", "touch"]
                                if cmd_parts[0] in safe_commands:
                                    result = run_subprocess_optimized(
                                        cmd_parts,
                                        capture_output=True,
                                        timeout=10,
                                    )
                                    if result.returncode == 0:
                                        fixes_applied += 1
                                        console.print(f"[green]  ✓ Fixed: {r.name}[/green]")
                                        fix_result = "success"
                                    else:
                                        fixes_failed += 1
                                        console.print(f"[red]  ✗ Failed: {r.name}[/red]")
                                        fix_result = "failed"
                                else:
                                    # For unknown commands, just log as skipped
                                    console.print(f"[yellow]  ⚠ Manual fix required: {cmd}[/yellow]")
                                    fix_result = "manual intervention required"

                    except subprocess.TimeoutExpired:
                        fixes_failed += 1
                        console.print(f"[red]  ✗ Timeout fixing: {r.name}[/red]")
                        fix_result = "timeout"
                    except Exception as e:
                        fixes_failed += 1
                        console.print(f"[red]  ✗ Error fixing {r.name}: {e}[/red]")
                        fix_result = f"error: {e}"

                    fix_report.append(
                        {
                            "check_name": r.name,
                            "category": r.category,
                            "status": "success"
                            if fix_result == "success" or "dry-run" in fix_result
                            else fix_result.split(":")[0]
                            if ":" in fix_result
                            else "failed",
                            "action": fix_action,
                            "result": fix_result,
                        }
                    )

    if fixes_applied > 0 or fixes_failed > 0:
        console.print(f"\n[bold]Fix Summary:[/bold] {fixes_applied} applied, {fixes_failed} failed\n")

    return fix_report


def _display_fix_report(fix_report: list[dict], dry_run: bool = False) -> None:
    """Display a formatted fix report.

    Args:
        fix_report: List of dicts containing fix entries
        dry_run: Whether this was a dry-run
    """
    if not fix_report:
        return

    from rich.table import Table

    mode = "[dim](DRY-RUN)[/dim] " if dry_run else ""
    table = Table(title=f"{mode}Fix Report", box=None, show_header=True)
    table.add_column("Category", style="dim")
    table.add_column("Check", style="bold")
    table.add_column("Action")
    table.add_column("Status")

    for entry in fix_report:
        status_str = (
            "[green]✓[/green]"
            if entry["status"] == "success"
            else "[yellow]↪[/yellow]"
            if "dry-run" in entry["status"]
            else "[red]✗[/red]"
        )
        if entry["status"] == "skipped":
            status_str = "[dim]⊘[/dim]"

        table.add_row(
            entry.get("category", ""),
            entry["check_name"],
            entry["action"][:50] + "..." if len(entry["action"]) > 50 else entry["action"],
            status_str,
        )

    console.print("\n")
    console.print(table)

    # Summary
    success_count = sum(1 for e in fix_report if e["status"] == "success")
    failed_count = sum(1 for e in fix_report if e["status"] in ("failed", "error", "timeout"))
    skipped_count = sum(1 for e in fix_report if e["status"] in ("skipped", "manual"))
    dry_run_count = sum(1 for e in fix_report if "dry-run" in e["status"])

    summary_parts = []
    if dry_run:
        summary_parts.append(f"[cyan]{dry_run_count} would be fixed[/cyan]")
    else:
        if success_count:
            summary_parts.append(f"[green]{success_count} fixed[/green]")
        if failed_count:
            summary_parts.append(f"[red]{failed_count} failed[/red]")
    if skipped_count:
        summary_parts.append(f"[dim]{skipped_count} skipped[/dim]")

    if summary_parts:
        console.print(f"[bold]Summary:[/bold] {', '.join(summary_parts)}")


