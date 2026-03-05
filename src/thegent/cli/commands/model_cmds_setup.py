"""Thegent CLI setup and provider configuration - extracted from model_cmds_config.py.

Handles unified setup: configure providers (same flow as cliproxy login), install shortcuts,
hooks, skills, harness, and services.
"""

# @trace WL-124
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, cast

import typer

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _bootstrap_metric_contracts,
    _get_run_subprocess_optimized,
    console,
)
from thegent.cli.commands.model_cmds_list import (
    _assert_str,
    _run_cliproxyctl_machine_command,
)
from thegent.cli.commands.model_cmds_setup_helpers import (
    build_provider_list,
    configure_providers,
    set_env_line,
)

def setup_cmd(
    api_key: str = typer.Option(None, "--api-key", "-k", help="NVIDIA NIM API key"),
    model: str = typer.Option(None, "--model", "-m", help="NVIDIA NIM model (default: z-ai/glm-5)"),
    openrouter_key: str = typer.Option(None, "--openrouter-key", help="OpenRouter API key"),
    kilo_key: str = typer.Option(None, "--kilo-key", help="Kilo.ai API key"),
    zai_key: str = typer.Option(None, "--zai-key", help="Z.AI (Zhipu) API key"),
    minimax_key: str = typer.Option(None, "--minimax-key", help="MiniMax API key"),
    wizard: bool = typer.Option(True, "--wizard/--no-wizard", help="Run interactive setup wizard"),
    links: bool = typer.Option(True, "--links/--no-links", help="Install claudeglm/claudemax shortcuts"),
    hooks: bool = typer.Option(
        False, "--hooks/--no-hooks", help="Install git hooks (pre-commit, pre-push) into .git/hooks"
    ),
    skills: bool = typer.Option(
        False, "--skills/--no-skills", help="Sync thegent-skills template to ~/.claude, ~/.cursor, project"
    ),
    harness: bool = typer.Option(False, "--harness/--no-harness", help="Install/update heliosShield harness"),
    full: bool = typer.Option(
        False,
        "--full",
        "-f",
        help="Full setup: install -t all, install-shims, lock-cleanup service, MCP service, and harness",
    ),
    agents: str = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated agents to configure (e.g. claude,codex,cursor). Skips others in wizard.",
    ),
) -> None:
    """Unified setup: configure providers (same flow as cliproxy login) and install shortcuts.

    Examples:
      thegent setup                    # Interactive wizard
      thegent setup --full             # Full setup: install, shims, services, harness
      thegent setup --harness          # Install/update heliosShield harness only
      thegent setup --hooks --skills   # Project: git hooks + skills
    """
    import platform
    from pathlib import Path

    from thegent.agents.cliproxy_manager import (
        _LOGIN_FLAGS,
        PROVIDER_LOGIN_CONFIG,
        _ensure_config,
        _inject_api_key_into_cliproxy,
        run_login,
    )
    from thegent.infra import yaml_dump, yaml_load

    settings = ThegentSettings()
    env_path = Path(".env")

    # Harness setup
    if harness or full:
        console.print("\n[bold cyan]Setting up heliosShield Harness...[/bold cyan]")
        try:
            from thegent.install import setup_harness

            if setup_harness(verbose=True):
                console.print("[green]✓[/green] heliosShield Harness setup complete.")
            else:
                console.print("[yellow]! heliosShield Harness setup skipped or failed.[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Harness setup error: {e}[/yellow]")

    # Full setup: install, shims, lock-cleanup, MCP service
    if full:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        from rich.prompt import Confirm

        console.print("\n[bold cyan]Full setup: installing to all targets...[/bold cyan]")
        try:
            from thegent.install import run_install

            run_install(target="all", install_service=True, verbose=True)
        except Exception as e:
            console.print(f"[yellow]Install: {e}[/yellow]")

        console.print("\n[bold cyan]Installing tool accelerators (shims)...[/bold cyan]")
        try:
            run_subprocess_optimized([sys.executable, "-m", "thegent", "install-shims"], check=False)
        except Exception as e:
            console.print(f"[yellow]Install-shims: {e}[/yellow]")

        if platform.system() in ("Darwin", "Linux"):
            if Confirm.ask("Install git wrapper to system path (requires sudo)?", default=False):
                try:
                    run_subprocess_optimized(
                        [sys.executable, "-m", "thegent", "install-shims", "--system"],
                        check=False,
                    )
                except Exception as e:
                    console.print(f"[yellow]Install-shims --system: {e}[/yellow]")

        console.print("\n[bold cyan]Installing lock-cleanup service...[/bold cyan]")
        try:
            from thegent_gitops import lock_cleanup_install, lock_cleanup_start

            ok, msg = lock_cleanup_install()
            if ok:
                console.print(f"[green]{msg}[/green]")
                ok, msg = lock_cleanup_start()
                if ok:
                    console.print(f"[green]{msg}[/green]")
                else:
                    console.print(f"[yellow]{msg}[/yellow]")
            else:
                console.print(f"[yellow]{msg}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Lock-cleanup: {e}[/yellow]")

        console.print("\n[bold cyan]Installing and starting MCP service...[/bold cyan]")
        try:
            from thegent.mcp.manage import service_install, service_start

            ok, msg = service_install()
            if ok:
                console.print(f"[green]{msg}[/green]")
            else:
                console.print(f"[yellow]{msg}[/yellow]")

            ok, msg = service_start()
            if ok:
                console.print(f"[green]{msg}[/green]")
            else:
                console.print(f"[yellow]{msg}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]MCP service: {e}[/yellow]")

        console.print("\n[bold green]Full setup complete.[/bold green]")
        if not wizard:
            console.print("[dim]Run thegent setup (without --full) to configure providers.[/dim]")
            return
    lines = env_path.read_text().splitlines() if env_path.exists() else []

    def prompt_key(msg: str) -> str:
        from rich.prompt import Prompt

        return Prompt.ask(msg, default="", show_default=False).strip()

    # CLI overrides: if user passed --api-key etc., inject into config directly
    overrides = {
        "nim": api_key,
        "kilo": kilo_key,
        "glm": zai_key,
        "minimax": minimax_key,
    }

    all_providers = build_provider_list(
        provider_login_config=PROVIDER_LOGIN_CONFIG,
        login_flags=_LOGIN_FLAGS,
        agents=agents,
        console=console,
    )
    should_delegate_setup = (
        wizard
        and os.environ.get("THGENT_SETUP_USE_CLIPROXY", "1") == "1"
        and not any(v for v in overrides.values())
    )
    if should_delegate_setup:
        delegation_args: list[str] = []
        selected_agents = (agents or "").strip()
        if selected_agents:
            delegation_args.extend(["--providers", selected_agents])
        try:
            console.print("\n[bold cyan]Delegating provider setup to cliproxyctl...[/bold cyan]")
            envelope = _run_cliproxyctl_machine_command("setup", args=delegation_args)
        except (ValueError, RuntimeError, FileNotFoundError) as exc:
            console.print(f"[red]Delegated setup failed: {exc}[/red]")
            raise typer.Exit(1)
        any_configured = bool(envelope.get("ok"))
    else:
        any_configured = configure_providers(
            providers=all_providers,
            overrides=cast("dict[str, str | None]", overrides),
            wizard=wizard,
            settings=settings,
            provider_login_config=PROVIDER_LOGIN_CONFIG,
            ensure_config=_ensure_config,
            inject_api_key=_inject_api_key_into_cliproxy,
            run_login=run_login,
            yaml_load=yaml_load,
            yaml_dump=lambda data, **kw: _assert_str(yaml_dump(data, **kw)),
            prompt_key=prompt_key,
            console=console,
        )

    env_updated = False
    if model:
        set_env_line(lines, key="THGENT_NIM_MODEL", value=model)
        env_updated = True

    if any_configured:
        console.print("\n[green]Provider credentials saved to cliproxy config.[/green]")
        console.print("[dim]The proxy has been restarted automatically to apply changes.[/dim]")

    # Ensure cliproxy config exists (cursor block, etc.)
    try:
        from thegent.agents.cliproxy_manager import _ensure_config

        _ensure_config(settings)
    except Exception as e:
        console.print(f"[yellow]Cliproxy config: {e}[/yellow]")
    if env_updated:
        env_path.write_text("\n".join(lines) + "\n")
        console.print(f"[green]Updated {env_path}[/green]")

    if links:
        console.print("\n[bold cyan]Installing interactive shortcuts...[/bold cyan]")
        bin_dir = Path.home() / ".local" / "bin"
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True, exist_ok=True)
        try:
            from thegent.clode_main import install_links as clode_install_links

            clode_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Clode links: {e}[/red]")
        try:
            from thegent.dex_main import install_links as dex_install_links

            dex_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Dex links: {e}[/red]")

    if hooks:
        console.print("\n[bold cyan]Installing git hooks...[/bold cyan]")
        try:
            from thegent.install import setup_hooks

            counts = setup_hooks(cwd=Path.cwd(), verbose=True)
            if counts.get("installed", 0) > 0:
                console.print(f"[green]✓[/green] Installed {counts['installed']} hook(s) into .git/hooks")
            elif counts.get("skipped", 0) > 0:
                console.print("[dim]Not a git repo; skipped hooks.[/dim]")
        except Exception as e:
            console.print(f"[yellow]Hooks: {e}[/yellow]")

    if skills:
        console.print("\n[bold cyan]Syncing skills template...[/bold cyan]")
        try:
            from thegent.install import setup_skills

            counts = setup_skills(cwd=Path.cwd(), verbose=True)
            if counts.get("copied", 0) > 0:
                console.print(f"[green]✓[/green] Synced {counts['copied']} file(s) to ~/.claude, ~/.cursor")
        except Exception as e:
            console.print(f"[yellow]Skills: {e}[/yellow]")

    # Bootstrap hard metric contracts and quality gate config for governance.
    try:
        created_contract, updated_quality = _bootstrap_metric_contracts(Path.cwd())
        if created_contract:
            console.print("[green]✓[/green] Bootstrapped contracts/metric-contracts.json")
        if updated_quality:
            console.print("[green]✓[/green] Enabled governance.metric_contracts.enforce_gate in .claude/quality.json")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if wizard:
        from rich.prompt import Confirm

        if Confirm.ask(
            "\nWould you like to integrate thegent with your AI agents (Cursor, Claude Code, Codex, etc.)?",
            default=True,
        ):
            from thegent.install import run_wizard

            run_wizard()

        if Confirm.ask(
            "\nRemove manual playwright from MCP configs (use thegent-bundled browser tools)?", default=True
        ):
            try:
                from thegent.mcp.manage import remove_playwright_from_client

                for c in ["cursor", "claude-code", "codex", "claude-desktop"]:
                    ok, msg = remove_playwright_from_client(c)
                    if ok and "Removed" in msg:
                        console.print(f"[dim]{msg}[/dim]")
                console.print("[dim]Start MCP: thegent mcp up[/dim]")
            except Exception as e:
                console.print(f"[yellow]Playwright removal: {e}[/yellow]")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("Try: [blue]claudeglm[/blue] | [blue]claudemax[/blue] | [blue]dex[/blue] | [blue]dexmax[/blue]")


def rules_sync_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite even if identical"),
    check: bool = typer.Option(False, "--check", help="Check for drift without syncing"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex)."""
    from thegent.cli.commands.impl import rules_sync_impl

    result = rules_sync_impl(cd=cd, force=force, check=check)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)

    if check:
        if result["in_sync"]:
            console.print("[green]Rules are in sync.[/green]")
            raise typer.Exit(0)
        console.print("[red]Drift detected in rule files:[/red]")
        for target in result["drift"]:
            console.print(f"  - {target}")
        raise typer.Exit(1)

    if not result["synced"]:
        console.print("[yellow]Rules are already in sync.[/yellow]")
    else:
        for target in result["synced"]:
            console.print(f"[green]Synced: {target}[/green]")



__all__ = [
    "rules_sync_cmd",
    "setup_cmd",
]
