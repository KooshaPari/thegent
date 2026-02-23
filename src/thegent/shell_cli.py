"""Shell environment management CLI commands."""

import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

shell_app = typer.Typer(name="shell", help="Shell environment management commands")
console = Console()


def _classify_subprocess_probe_error(exc: BaseException) -> str:
    if isinstance(exc, subprocess.TimeoutExpired):
        timeout_s = getattr(exc, "timeout", None)
        if isinstance(timeout_s, int | float):
            return f"timeout after {timeout_s}s"
        return "timeout"
    if isinstance(exc, FileNotFoundError):
        return "zsh executable not found"
    if isinstance(exc, subprocess.SubprocessError):
        return f"subprocess error ({type(exc).__name__}): {exc}"
    if isinstance(exc, OSError):
        return f"os error ({type(exc).__name__}): {exc}"
    return f"unexpected error ({type(exc).__name__}): {exc}"


def _classify_subprocess_probe_execution(
    result: subprocess.CompletedProcess[str]
) -> str:
    reason = f"execution failed (exit {result.returncode})"
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    if stderr and stdout:
        return f"{reason}: stderr='{stderr}', stdout='{stdout}'"
    if stderr:
        return f"{reason}: {stderr}"
    if stdout:
        return f"{reason}: {stdout}"
    return reason


@shell_app.command("status")
def shell_status() -> None:
    """Show shell environment status and configuration."""
    home = Path.home()

    table = Table(title="Shell Environment Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Path", style="dim")

    # Check installed files
    files = {
        ".zshenv": home / ".zshenv",
        ".zsh_bundle.zsh": home / ".zsh_bundle.zsh",
        ".zsh_optimization.zsh": home / ".zsh_optimization.zsh",
        ".zsh_safeguards.zsh": home / ".zsh_safeguards.zsh",
        ".zsh_advanced.zsh": home / ".zsh_advanced.zsh",
        ".zshrc": home / ".zshrc",
    }

    for name, path in files.items():
        status = "✓ Installed" if path.exists() else "✗ Missing"
        table.add_row(name, status, str(path))

    # Check loaded status
    console.print(table)
    console.print()

    # Check environment variables
    env_table = Table(title="Environment Status")
    env_table.add_column("Variable", style="cyan")
    env_table.add_column("Value", style="green")

    from thegent.config import ThegentSettings

    settings = ThegentSettings()

    # Map env var names to settings attributes
    env_mapping = {
        "THEGENT_CACHE_DIR": str(settings.cache_dir),
        # Runtime/state vars that aren't settings - keep as env check
        "THEGENT_BUNDLE_LOADED": os.environ.get("THEGENT_BUNDLE_LOADED", "Not set"),
        "THEGENT_SHELL_OPTIMIZATION_LOADED": os.environ.get("THEGENT_SHELL_OPTIMIZATION_LOADED", "Not set"),
        "THEGENT_SHELL_SAFEGUARDS_LOADED": os.environ.get("THEGENT_SHELL_SAFEGUARDS_LOADED", "Not set"),
        "THEGENT_ADVANCED_LOADED": os.environ.get("THEGENT_ADVANCED_LOADED", "Not set"),
        "THEGENT_PLATFORM": os.environ.get("THEGENT_PLATFORM", "Not set"),
        "THEGENT_INSTANT_PROMPT_ENABLED": os.environ.get("THEGENT_INSTANT_PROMPT_ENABLED", "Not set"),
        "THEGENT_ASYNC_LOADING_ENABLED": os.environ.get("THEGENT_ASYNC_LOADING_ENABLED", "Not set"),
        "THEGENT_METRICS_ENABLED": os.environ.get("THEGENT_METRICS_ENABLED", "Not set"),
    }

    for var, value in env_mapping.items():
        env_table.add_row(var, str(value))

    console.print(env_table)


@shell_app.command("stat")
def shell_status_alias() -> None:
    """Alias for shell status."""
    shell_status()


@shell_app.command("profile")
def shell_profile(
    enable: bool = typer.Option(False, "--enable", help="Enable profiling"),
    disable: bool = typer.Option(False, "--disable", help="Disable profiling"),
) -> None:
    """Enable or disable shell startup profiling."""
    zshrc = Path.home() / ".zshrc"

    if not zshrc.exists():
        from thegent.errors import print_error

        print_error(".zshrc not found.", hint="Run 'thegent install --target user' first.")
        raise typer.Exit(1)

    content = zshrc.read_text()

    if enable:
        # Add profiling enable
        if "THEGENT_PROFILE_ENABLED=1" not in content:
            content += "\n# Enable thegent shell profiling\nexport THEGENT_PROFILE_ENABLED=1\n"
            zshrc.write_text(content)
            console.print("[green]✓ Profiling enabled. Restart your shell and run 'zprof' to see results.[/green]")
        else:
            console.print("[yellow]Profiling already enabled.[/yellow]")
    elif disable:
        # Remove profiling
        content = content.replace("export THEGENT_PROFILE_ENABLED=1\n", "")
        content = content.replace("# Enable thegent shell profiling\n", "")
        zshrc.write_text(content)
        console.print("[green]✓ Profiling disabled.[/green]")
    # Show current status
    elif "THEGENT_PROFILE_ENABLED=1" in content:
        console.print("[green]Profiling is enabled.[/green]")
    else:
        console.print("[yellow]Profiling is disabled.[/yellow]")


@shell_app.command("prof")
def shell_profile_alias(
    enable: bool = typer.Option(False, "--enable", help="Enable profiling"),
    disable: bool = typer.Option(False, "--disable", help="Disable profiling"),
) -> None:
    """Alias for shell profile."""
    shell_profile(enable=enable, disable=disable)


@shell_app.command("clear-cache")
def shell_clear_cache() -> None:
    """Clear shell optimization cache (eval cache, tool cache, etc.)."""
    import shutil

    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cache_dir = settings.cache_dir
    eval_cache_dir = cache_dir / "eval-cache"

    if eval_cache_dir.exists():
        shutil.rmtree(eval_cache_dir)
        eval_cache_dir.mkdir(parents=True)
        console.print(f"[green]✓ Cleared eval cache: {eval_cache_dir}[/green]")
    else:
        console.print("[yellow]No cache to clear.[/yellow]")


@shell_app.command("reload")
def shell_reload() -> None:
    """Reload shell configuration (sources .zshrc)."""
    console.print("[yellow]Reloading shell configuration...[/yellow]")
    console.print("[dim]Note: This only works if run from within zsh.[/dim]")

    # Try to source .zshrc
    try:
        result = subprocess.run(
            ["zsh", "-c", "source ~/.zshrc"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            console.print("[green]✓ Shell configuration reloaded.[/green]")
            return

        console.print(f"[red]Shell reload failed (exit code {result.returncode}).[/red]")
        stdout_snippet = result.stdout.strip()
        stderr_snippet = result.stderr.strip()
        if stdout_snippet:
            console.print(f"[yellow]stdout:[/yellow] {stdout_snippet[:500]}")
        if stderr_snippet:
            console.print(f"[yellow]stderr:[/yellow] {stderr_snippet[:500]}")
        console.print("[yellow]Try running: source ~/.zshrc[/yellow]")
        raise typer.Exit(1)
    except (subprocess.SubprocessError, OSError) as e:
        console.print(f"[red]Error reloading: {e}[/red]")
        console.print("[yellow]Try running: exec zsh[/yellow]")
        raise typer.Exit(1)


@shell_app.command("doctor")
def shell_doctor(fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues")) -> None:
    """Diagnose shell environment issues."""
    home = Path.home()
    issues = []
    fixes = []
    warnings = []

    # Check for missing files
    required_files = {
        ".zshenv": home / ".zshenv",
        ".zsh_bundle.zsh": home / ".zsh_bundle.zsh",
    }

    for name, path in required_files.items():
        if not path.exists():
            issues.append(f"Missing required file: {name}")
            if fix:
                fixes.append("Run: thegent install --target system")

    # Check for problematic aliases
    try:
        result = subprocess.run(
            ["zsh", "-c", "alias ls 2>/dev/null | command grep -E '(tree|recursive|-R)' || true"],
            capture_output=True,
            text=True,
            timeout=2,
            env={**os.environ, "RIPGREP_CONFIG_PATH": "", "GREP_OPTIONS": ""},
            check=False,
        )
        if result.returncode != 0:
            reason = _classify_subprocess_probe_execution(result)
            warnings.append(f"Alias probe execution failed ({reason}). Check zsh startup and rerun: thegent shell doctor.")
            if fix:
                fixes.append("Fix zsh startup errors or rerun with a clean PATH.")
        elif result.stdout.strip():
            issues.append("ls is aliased to tree/recursive output")
            if fix:
                fixes.append("Safeguards should fix this automatically")
    except subprocess.TimeoutExpired as exc:
        reason = _classify_subprocess_probe_error(exc)
        warnings.append(
            f"Alias probe timed out: {reason}. Check zsh startup time and rerun: thegent shell doctor --fix"
        )
        if fix:
            fixes.append("Increase shell probe timeout or skip alias checks temporarily.")
    except FileNotFoundError as exc:
        reason = _classify_subprocess_probe_error(exc)
        warnings.append(
            f"Alias probe unavailable ({reason}). Verify zsh is installed and runnable, "
            "then rerun: thegent shell doctor."
        )
        if fix:
            fixes.append("Install or fix zsh in PATH, then rerun: thegent shell doctor.")
    except subprocess.SubprocessError as exc:
        reason = _classify_subprocess_probe_error(exc)
        warnings.append(
            f"Alias probe unavailable ({reason}). Verify zsh is installed and runnable, "
            "then rerun: thegent shell doctor."
        )
        if fix:
            fixes.append("Install or fix zsh in PATH, then rerun: thegent shell doctor.")
    except OSError as exc:
        reason = _classify_subprocess_probe_error(exc)
        warnings.append(
            f"Alias probe unavailable ({reason}). Verify zsh is installed and runnable, "
            "then rerun: thegent shell doctor."
        )
        if fix:
            fixes.append("Install or fix zsh in PATH, then rerun: thegent shell doctor.")

    # Check cache directory permissions
    cache_dir = Path.home() / ".cache" / "thegent"
    if cache_dir.exists() and not os.access(cache_dir, os.W_OK):
        issues.append(f"Cache directory not writable: {cache_dir}")
        if fix:
            fixes.append(f"Run: chmod 755 {cache_dir}")

    # Report results
    if issues:
        console.print("[red]Issues found:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")
        if fixes:
            console.print("\n[yellow]Suggested fixes:[/yellow]")
            for fix_cmd in fixes:
                console.print(f"  • {fix_cmd}")
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")
    if not issues and not warnings:
        console.print("[green]✓ No issues found. Shell environment is healthy.[/green]")


@shell_app.command("doc")
def shell_doctor_alias(fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues")) -> None:
    """Alias for shell doctor."""
    shell_doctor(fix=fix)


@shell_app.command("benchmark")
def shell_benchmark(iterations: int = typer.Option(10, "--iterations", "-n", help="Number of iterations")) -> None:
    """Benchmark shell startup time."""
    console.print(f"[cyan]Benchmarking shell startup ({iterations} iterations)...[/cyan]")

    times = []
    for i in range(iterations):
        try:
            result = subprocess.run(
                ["/usr/bin/time", "-p", "zsh", "-i", "-c", "exit"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            # Parse time output
            for line in result.stderr.split("\n"):
                if line.startswith("real"):
                    time_str = line.split()[1]
                    times.append(float(time_str))
                    break
        except Exception as e:
            console.print(f"[red]Error in iteration {i + 1}: {e}[/red]")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        table = Table(title="Shell Startup Benchmark Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Time", style="green")
        table.add_row("Average", f"{avg_time:.3f}s")
        table.add_row("Minimum", f"{min_time:.3f}s")
        table.add_row("Maximum", f"{max_time:.3f}s")
        table.add_row("Iterations", str(len(times)))

        console.print(table)

        if avg_time > 0.5:
            console.print("[yellow]⚠ Startup time is > 500ms. Consider enabling lazy loading.[/yellow]")
        elif avg_time > 0.2:
            console.print("[yellow]⚠ Startup time is > 200ms. Consider optimization.[/yellow]")
        else:
            console.print("[green]✓ Startup time is excellent (< 200ms)[/green]")
    else:
        console.print("[red]Failed to collect benchmark data.[/red]")


@shell_app.command("optimize")
def shell_optimize() -> None:
    """Optimize shell configuration for performance."""
    console.print("[cyan]Optimizing shell configuration...[/cyan]")

    # Enable lazy loading
    zshrc = Path.home() / ".zshrc"
    if zshrc.exists():
        content = zshrc.read_text()

        # Ensure optimization is loaded
        if "zsh_optimization.zsh" not in content:
            content += (
                "\n# Load shell optimization\n[[ -f ~/.zsh_optimization.zsh ]] && source ~/.zsh_optimization.zsh\n"
            )

        # Enable profiling temporarily for measurement
        if "THEGENT_PROFILE_ENABLED" not in content:
            content += "\n# Enable profiling for optimization measurement\nexport THEGENT_PROFILE_ENABLED=0\n"

        zshrc.write_text(content)
        console.print("[green]✓ Shell configuration optimized.[/green]")
        console.print("[yellow]Restart your shell to apply changes.[/yellow]")
    else:
        console.print("[red]Error: .zshrc not found. Run 'thegent install --target user' first.[/red]")


@shell_app.command("metrics")
def shell_metrics() -> None:
    """Show shell performance metrics and statistics."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cache_dir = settings.cache_dir
    metrics_file = cache_dir / "advanced" / "metrics" / "stats"

    if not metrics_file.exists():
        console.print("[yellow]No metrics collected yet. Enable metrics with:[/yellow]")
        console.print("[cyan]  export THEGENT_METRICS_ENABLED=1[/cyan]")
        console.print("[dim]Then restart your shell and use it normally.[/dim]")
        return

    # Parse metrics
    metrics = {}
    try:
        with open(metrics_file) as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    metrics[key] = metrics.get(key, 0) + int(value)
    except Exception as e:
        console.print(f"[red]Error reading metrics: {e}[/red]")
        return

    if not metrics:
        console.print("[yellow]No metrics data available.[/yellow]")
        return

    table = Table(title="Shell Performance Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    for metric, value in sorted(metrics.items()):
        table.add_row(metric, str(value))

    console.print(table)


@shell_app.command("jobs")
def shell_jobs() -> None:
    """Show background job status."""
    import os

    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cache_dir = settings.cache_dir
    registry_file = cache_dir / "advanced" / "jobs" / "registry"

    if not registry_file.exists():
        console.print("[yellow]No background jobs registered.[/yellow]")
        return

    jobs = []
    try:
        with open(registry_file) as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    name, pid = line.split(":", 1)
                    # Check if process is still running
                    try:
                        os.kill(int(pid), 0)
                        status = "Running"
                    except (OSError, ValueError):
                        status = "Completed"
                    jobs.append((name, pid, status))
    except Exception as e:
        console.print(f"[red]Error reading job registry: {e}[/red]")
        return

    if not jobs:
        console.print("[yellow]No active background jobs.[/yellow]")
        return

    table = Table(title="Background Jobs")
    table.add_column("Job Name", style="cyan")
    table.add_column("PID", style="green")
    table.add_column("Status", style="yellow")

    for name, pid, status in jobs:
        table.add_row(name, pid, status)

    console.print(table)


@shell_app.command("cache-stats")
def shell_cache_stats() -> None:
    """Show cache statistics (hit/miss rates, sizes)."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cache_dir = settings.cache_dir
    l2_dir = cache_dir / "advanced" / "cache-l2"
    eval_cache_dir = cache_dir / "eval-cache"

    table = Table(title="Cache Statistics")
    table.add_column("Cache Level", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Size", style="yellow")

    # L1 cache (in-memory, can't measure directly)
    table.add_row("L1 (Memory)", "Active", "N/A (session-scoped)")

    # L2 cache
    if l2_dir.exists():
        l2_size = sum(f.stat().st_size for f in l2_dir.rglob("*") if f.is_file())
        l2_count = len(list(l2_dir.glob("*.cache")))
        table.add_row("L2 (File)", "Active", f"{l2_count} files, {l2_size / 1024:.1f} KB")
    else:
        table.add_row("L2 (File)", "Empty", "0 files")

    # Eval cache
    if eval_cache_dir.exists():
        eval_size = sum(f.stat().st_size for f in eval_cache_dir.rglob("*") if f.is_file())
        eval_count = len(list(eval_cache_dir.glob("*.zsh")))
        table.add_row("Eval Cache", "Active", f"{eval_count} files, {eval_size / 1024:.1f} KB")
    else:
        table.add_row("Eval Cache", "Empty", "0 files")

    console.print(table)


@shell_app.command("circuit-breaker")
def shell_circuit_breaker(
    reset: str | None = typer.Option(None, "--reset", help="Reset circuit breaker for service"),
    list_all: bool = typer.Option(False, "--list", help="List all circuit breakers"),
) -> None:
    """Manage circuit breakers for error recovery."""
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    cache_dir = settings.cache_dir
    cb_dir = cache_dir / "advanced" / "circuit-breakers"

    if reset:
        # Reset specific circuit breaker
        state_file = cb_dir / f"{reset}.state"
        failure_file = cb_dir / f"{reset}.failures"
        if state_file.exists() or failure_file.exists():
            state_file.unlink(missing_ok=True)
            failure_file.unlink(missing_ok=True)
            console.print(f"[green]✓ Reset circuit breaker for: {reset}[/green]")
        else:
            console.print(f"[yellow]No circuit breaker found for: {reset}[/yellow]")
        return

    if list_all:
        # List all circuit breakers
        if not cb_dir.exists():
            console.print("[yellow]No circuit breakers configured.[/yellow]")
            return

        table = Table(title="Circuit Breakers")
        table.add_column("Service", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Failures", style="yellow")

        for state_file in cb_dir.glob("*.state"):
            service = state_file.stem
            failures_file = cb_dir / f"{service}.failures"

            state_content = state_file.read_text().strip()
            if state_content.startswith("open:"):
                state = "Open"
                failures = failures_file.read_text().strip() if failures_file.exists() else "N/A"
            else:
                state = "Closed"
                failures = failures_file.read_text().strip() if failures_file.exists() else "0"

            table.add_row(service, state, failures)

        console.print(table)
        return

    # Show status
    console.print("[cyan]Circuit Breaker Management[/cyan]")
    console.print("[dim]Use --list to see all circuit breakers[/dim]")
    console.print("[dim]Use --reset SERVICE to reset a circuit breaker[/dim]")


@shell_app.command("platform")
def shell_platform() -> None:
    """Show platform detection and compatibility information."""
    import platform

    table = Table(title="Platform Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("System", platform.system())
    table.add_row("Platform", platform.platform())
    table.add_row("Architecture", platform.machine())
    table.add_row("Python Version", platform.python_version())

    # Check shell
    try:
        result = subprocess.run(["zsh", "--version"], capture_output=True, text=True, timeout=2, check=False)
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) > 1:
                table.add_row("Zsh Status", "Available")
                table.add_row("Zsh Version", parts[1])
            else:
                table.add_row("Zsh Status", "Malformed version output")
                table.add_row("Zsh Version", result.stdout.strip() or "Unknown")
        else:
            reason = _classify_subprocess_probe_execution(result)
            table.add_row("Zsh Status", f"Execution failed ({reason})")
            table.add_row("Zsh Version", "Unknown")
    except FileNotFoundError as exc:
        reason = _classify_subprocess_probe_error(exc)
        table.add_row("Zsh Status", f"Probe failed ({reason})")
        table.add_row("Zsh Version", "Unknown")
    except subprocess.TimeoutExpired as exc:
        reason = _classify_subprocess_probe_error(exc)
        table.add_row("Zsh Status", f"Probe failed ({reason})")
        table.add_row("Zsh Version", "Unknown")
    except subprocess.SubprocessError as exc:
        reason = _classify_subprocess_probe_error(exc)
        table.add_row("Zsh Status", f"Probe failed ({reason})")
        table.add_row("Zsh Version", "Unknown")
    except OSError as exc:
        reason = _classify_subprocess_probe_error(exc)
        table.add_row("Zsh Status", f"Probe failed ({reason})")
        table.add_row("Zsh Version", "Unknown")

    console.print(table)
