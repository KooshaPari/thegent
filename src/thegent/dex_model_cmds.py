"""Model commands for dex CLI.

These commands provide shortcuts to specific models via Codex.
Extracted from dex_main.py for maintainability.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import typer



def create_dex_model_command(
    app: typer.Typer,
    name: str,
    model_alias: str,
    help_text: str,
):
    """Create a dex model command and register it with the app.
    
    Args:
        app: Typer app to register command with
        name: Command name
        model_alias: Model alias to pass to runner
        help_text: Help text for command
    """
    
    @app.command(name)
    def model_cmd(
        resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
        cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
        print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
        full: bool = typer.Option(False, "--full", "-f", help="Full auto mode (YOLO)"),
        debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
        add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
        native: bool = typer.Option(False, "--native", help="Use native codex binary"),
        prompt: str | None = typer.Argument(None, help="Startup prompt"),
    ) -> None:
        """Model shortcut command."""
        from thegent.dex_main import _run_model_cmd
        
        _run_model_cmd(
            model_alias,
            resume=resume,
            prompt=prompt,
            cd=cd,
            print_mode=print_mode,
            full=full,
            debug=debug,
            add_dir=add_dir or None,
            native=native,
        )
    
    model_cmd.__doc__ = help_text
    return model_cmd


# Model definitions: (command_name, model_alias, help_text)
DEX_MODEL_COMMANDS = [
    ("composer", "composer", "Composer 1.5 (via Cursor/Codex)."),
    ("max", "max", "Claude Max (extended) via Codex proxy."),
    ("glm", "glm", "GLM-4 (Zhipu) via Codex proxy API."),
    ("haiku", "haiku", "Claude Haiku 4.5 via Codex proxy."),
    ("opus", "opus", "Claude Opus 4.5 via Codex proxy."),
    ("sonnet", "sonnet", "Claude Sonnet 4 via Codex proxy."),
    ("ultra", "ultra", "Claude Ultra via Codex proxy."),
    ("flash", "flash", "Gemini 2.0 Flash via Codex proxy."),
    ("high", "high", "Claude 3.5/4 Sonnet high via Codex."),
    ("xhigh", "xhigh", "Claude 3.5/4 Opus via Codex."),
    ("mini", "mini", "GPT-4o-mini via Codex proxy API."),
    ("free", "free", "Free models: gemini-2.0-flash, etc."),
]


def register_dex_model_commands(app: typer.Typer) -> None:
    """Register all dex model commands with the app.
    
    Args:
        app: Typer app to register commands with
    """
    for cmd_name, model_alias, help_text in DEX_MODEL_COMMANDS:
        create_dex_model_command(app, cmd_name, model_alias, help_text)


__all__ = [
    "DEX_MODEL_COMMANDS",
    "create_dex_model_command",
    "register_dex_model_commands",
]
