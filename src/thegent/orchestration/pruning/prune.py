"""Pruning and resource management logic."""

import contextlib
import logging
import os
import re
import signal
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.infra import run_subprocess_optimized
from thegent.prune_utils import is_orphan_by_ppid
from thegent.skills.terminal import capture_tmux_pane, list_tmux_panes, send_to_tmux_pane

console = Console()
logger = logging.getLogger(__name__)

_TARGET_PATTERNS: tuple[str, ...] = (
    "pyright-langserver",
    "typescript-language-server",
    "tsserver.js",
    "@playwright/mcp",
    "context7-mcp",
    "octocode-mcp",
    "next-devtools-mcp",
    "sequential-thinking",
    "cc-status",
)


def _is_mcp_candidate(cmd: str) -> bool:
    """True if command line clearly matches known MCP/LSP server processes."""
    low = cmd.lower()
    if any(pat in low for pat in _TARGET_PATTERNS):
        return True
    # Restrict generic runtimes to explicit MCP/LSP contexts.
    if re.search(r"\b(node|npm|bun|deno)\b", low) and re.search(r"\b(mcp|langserver|lsp|tsserver)\b", low):
        return True
    return False


def mcp_prune(
    force: bool = False,
    dry_run: bool = False,
    parent_pid: int | None = None,
    interactive: bool = True,
    caller_info: str | None = None,
    shadow_max_age_hours: int = 24,
    quality_log_max_age_days: int = 7,
) -> None:
    """Kill redundant agent-related Node.js processes (LSPs, MCP servers).

    Args:
        force: If True, skip interactive prompts (but still protects terminal-attached processes)
        dry_run: If True, only show what would be pruned without killing
        parent_pid: If set, only prune direct children of this PID
        interactive: If True, prompt for terminal-attached processes
        caller_info: Optional string identifying what triggered this prune (for logging)
    """
    settings = ThegentSettings()

    # Log what triggered pruning
    trigger_info = caller_info or "unknown"
    logger.info(
        f"THEGENT PRUNE: Triggered by {trigger_info} (force={force}, parent_pid={parent_pid}, interactive={interactive})"
    )
    if not dry_run:
        console.print(f"[dim]Pruning triggered by: {trigger_info}[/dim]")

    try:
        res = run_subprocess_optimized(
            ["ps", "-eo", "pid,ppid,tty,rss,command"],
            capture_output=True,
            check=False,
        )
        stdout_text = (
            res.stdout
            if isinstance(res.stdout, str)
            else (res.stdout.decode("utf-8", errors="replace") if res.stdout else "")
        )
        lines = stdout_text.strip().splitlines()
    except Exception as e:
        console.print(f"[red]Failed to list processes: {e}[/red]")
        return

    # Build maps
    parent_map: dict[int, int] = {}
    cmd_map: dict[int, str] = {}
    tty_map: dict[int, str] = {}
    candidates: list[dict[str, Any]] = []

    for line in lines[1:]:
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        pid_s, ppid_s, tty, rss_s, cmd = parts[0], parts[1], parts[2], parts[3], parts[4]
        try:
            pid_i = int(pid_s)
            ppid_i = int(ppid_s)
            rss_kb = int(rss_s)
        except ValueError:
            continue

        parent_map[pid_i] = ppid_i
        cmd_map[pid_i] = cmd
        tty_map[pid_i] = tty.replace("/dev/", "") if tty != "??" else ""

        cmd_lower = cmd.lower()
        # Never prune core agents
        if any(
            x in cmd_lower
            for x in (
                "cursor-agent",
                "cursor agent",
                "thegent",
                "claude",
                "clode",
                "codex",
                "droid",
                "roid",
                "anen",
                "antigma",
                "fanta",
                "ante",
                "opencode",
                "copilot",
                "gemini",
            )
        ):
            continue

        # Never prune shell processes or terminal emulators (even if they match patterns)
        if any(
            x in cmd_lower
            for x in (
                "bash",
                "zsh",
                "sh",
                "fish",
                "tcsh",
                "csh",
                "dash",
                "ghostty",
                "terminal",
                "iterm",
                "alacritty",
                "kitty",
                "wezterm",
                "warp",
            )
        ):
            continue

        if parent_pid:
            if ppid_i == parent_pid:
                candidates.append({"pid": pid_i, "ppid": ppid_i, "cmd": cmd, "rss_kb": rss_kb, "tty": tty_map[pid_i]})
            continue

        if _is_mcp_candidate(cmd):
            candidates.append({"pid": pid_i, "ppid": ppid_i, "cmd": cmd, "rss_kb": rss_kb, "tty": tty_map[pid_i]})

    # Filter to orphans
    if parent_pid:
        to_kill = candidates
    elif settings.prune_orphan_by_ppid:
        to_kill = [c for c in candidates if is_orphan_by_ppid(c["pid"], parent_map, cmd_map)]
    else:
        to_kill = candidates

    if not to_kill:
        if not dry_run:
            console.print("[green]No redundant agent processes found.[/green]")
        shadow_pruned, logs_pruned = prune_stale_shadow_and_logs(
            dry_run=dry_run,
            shadow_max_age_hours=shadow_max_age_hours,
            quality_log_max_age_days=quality_log_max_age_days,
        )
        if shadow_pruned or logs_pruned:
            action = "would remove" if dry_run else "removed"
            console.print(
                f"[green]Storage prune {action}: {shadow_pruned} shadow dirs, {logs_pruned} quality logs.[/green]"
            )
        return

    # Sort by RSS
    to_kill = sorted(to_kill, key=lambda c: c.get("rss_kb", 0), reverse=True)

    if dry_run:
        t = Table(title="Orphan Processes to Prune")
        t.add_column("PID")
        t.add_column("RSS (KB)")
        t.add_column("TTY")
        t.add_column("Command")
        for item in to_kill:
            t.add_row(str(item["pid"]), str(item["rss_kb"]), item["tty"], item["cmd"][:80])
        console.print(t)
        return

    # Interaction logic - protect terminal-attached processes
    panes = list_tmux_panes()
    killed_count = 0
    skipped_terminal_count = 0

    for item in to_kill:
        pid = item["pid"]
        tty = item["tty"]
        cmd = item["cmd"]

        # CRITICAL: Always protect processes attached to terminals, even with force=True
        # This prevents killing user shells (Ghostty, terminal windows, etc.)
        # Also protect processes that look like shells or terminals
        cmd_lower = cmd.lower()
        is_shell_like = any(
            x in cmd_lower
            for x in ("bash", "zsh", "sh", "fish", "tcsh", "csh", "ghostty", "terminal", "iterm", "alacritty", "kitty")
        )

        if tty and tty != "??":
            pane = next((p for p in panes if p.tty == tty), None)
            if pane:
                # Process is attached to a tmux pane - show interactive menu
                logger.warning(
                    f"THEGENT PRUNE: Skipping terminal-attached process PID {pid} ({cmd[:50]}) on TTY {tty} - protected from auto-kill"
                )
                if interactive:
                    show_interactive_prune_menu(pid, cmd, tty, pane)
                else:
                    console.print(
                        f"[yellow]Skipped terminal-attached process PID {pid} ({cmd[:50]}) - use interactive mode to prune[/yellow]"
                    )
                skipped_terminal_count += 1
                continue
            # TTY exists but no tmux pane - still protect it (could be Ghostty, Terminal.app, etc.)
            logger.warning(
                f"THEGENT PRUNE: Skipping TTY-attached process PID {pid} ({cmd[:50]}) on TTY {tty} - protected from auto-kill"
            )
            console.print(f"[yellow]Skipped TTY-attached process PID {pid} ({cmd[:50]}) - protected[/yellow]")
            skipped_terminal_count += 1
            continue

        # Also protect shell-like processes even without TTY (defensive)
        if is_shell_like:
            logger.warning(
                f"THEGENT PRUNE: Skipping shell-like process PID {pid} ({cmd[:50]}) - protected from auto-kill"
            )
            console.print(f"[yellow]Skipped shell-like process PID {pid} ({cmd[:50]}) - protected[/yellow]")
            skipped_terminal_count += 1
            continue

        # Process has no TTY or TTY is "??" and not shell-like - safe to prune
        if kill_process(pid):
            logger.info(f"THEGENT PRUNE: Killed PID {pid} ({cmd[:50]})")
            killed_count += 1
        else:
            logger.warning(f"THEGENT PRUNE: Failed to kill PID {pid} ({cmd[:50]})")

    if killed_count > 0:
        console.print(f"[green]Successfully pruned {killed_count} processes.[/green]")
    if skipped_terminal_count > 0:
        console.print(f"[yellow]Skipped {skipped_terminal_count} terminal-attached processes (protected).[/yellow]")
        logger.info(f"THEGENT PRUNE: Protected {skipped_terminal_count} terminal-attached processes from pruning")

    shadow_pruned, logs_pruned = prune_stale_shadow_and_logs(
        dry_run=dry_run,
        shadow_max_age_hours=shadow_max_age_hours,
        quality_log_max_age_days=quality_log_max_age_days,
    )
    if shadow_pruned or logs_pruned:
        action = "would remove" if dry_run else "removed"
        console.print(
            f"[green]Storage prune {action}: {shadow_pruned} shadow dirs, {logs_pruned} quality logs.[/green]"
        )


def kill_process(pid: int) -> bool:
    """Kill process with SIGTERM then SIGKILL if needed."""
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        return True
    except Exception:
        return False


def prompt_tty_kill(pid: int, cmd: str, tty: str) -> bool:
    """Prompt user on a raw TTY if possible."""
    try:
        tty_path = f"/dev/{tty}" if not tty.startswith("/") else tty
        with open(tty_path, "w") as f:
            f.write(f"\n*** THEGENT: High resource process detected: {cmd[:50]} (PID {pid})\n")
            f.write("Kill this process to reclaim memory? (y/N): ")

        # We can't easily read from the TTY in a background process without taking it over
        # So we default to keeping it alive or using a timeout
        return False
    except:
        return False


def prune_stale_shadow_and_logs(
    dry_run: bool,
    shadow_max_age_hours: int,
    quality_log_max_age_days: int,
    root: Path | None = None,
) -> tuple[int, int]:
    """Prune stale .shadow-* dirs and aged .quality/logs files.

    Returns:
        Tuple of (shadow_dirs_pruned, quality_logs_pruned).
    """
    project_root = root.resolve() if root else Path.cwd().resolve()
    parent = project_root.parent
    now = time.time()
    shadow_cutoff = now - (shadow_max_age_hours * 3600)
    log_cutoff = now - (quality_log_max_age_days * 86400)

    shadow_removed = 0
    for p in parent.glob(".shadow-*"):
        if not p.is_dir():
            continue
        try:
            if p.stat().st_mtime >= shadow_cutoff:
                continue
        except OSError:
            continue
        if dry_run:
            logger.info("DRY-RUN stale shadow prune candidate: %s", p)
        else:
            with contextlib.suppress(Exception):
                shutil.rmtree(p)
        shadow_removed += 1

    logs_removed = 0
    logs_dir = project_root / ".quality" / "logs"
    if logs_dir.exists():
        for f in logs_dir.rglob("*"):
            if not f.is_file():
                continue
            try:
                if f.stat().st_mtime >= log_cutoff:
                    continue
            except OSError:
                continue
            if dry_run:
                logger.info("DRY-RUN stale quality log prune candidate: %s", f)
            else:
                with contextlib.suppress(Exception):
                    f.unlink()
            logs_removed += 1

    return shadow_removed, logs_removed


def show_interactive_prune_menu(pid: int, cmd: str, tty: str, pane: Any):
    """Show a tmux menu for interactive pruning with context."""
    # Capture last 50 lines for context as requested
    last_output = capture_tmux_pane(pane.pane_id, last_lines=50)

    context_header = f"\n\n{'=' * 20} THEGENT CONTEXT SNAPSHOT {'=' * 20}\n"
    context_footer = f"\n{'=' * 66}\n"
    banner = f"{context_header}{last_output}{context_footer}\n*** THEGENT: High resource process detected: {cmd[:50]} (PID {pid}) ***\n(Showing menu for Kill/Pause/Bypass)\n"

    # Send banner to the pane so user sees context
    send_to_tmux_pane(pane.pane_id, banner, enter=False)

    title = f"THEGENT: Resource Guard (PID {pid})"
    menu_cmd = [
        "tmux",
        "display-menu",
        "-t",
        pane.pane_id,
        "-T",
        title,
        "Pause Process (P)",
        "p",
        f"run-shell 'kill -STOP {pid}; tmux display-message -t {pane.pane_id} \"PAUSED: process {pid}. Use kill -CONT {pid} to resume.\"'",
        "Kill & Reclaim (K)",
        "k",
        f"run-shell 'kill -9 {pid}; tmux display-message -t {pane.pane_id} \"KILLED: process {pid}.\"'",
        "Bypass - Keep Alive (B)",
        "b",
        "display-message 'Prune bypassed.'",
        "",
        "",
        "",
        "Exit Menu (Esc)",
        "Escape",
        "",
    ]

    with contextlib.suppress(BaseException):
        subprocess.run(menu_cmd, check=False)
