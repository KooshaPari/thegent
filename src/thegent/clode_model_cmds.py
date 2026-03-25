"""Model commands for clode CLI.

These commands provide shortcuts to specific models.
Extracted from clode_main.py for maintainability.
"""

from __future__ import annotations

from pathlib import Path

import typer


def _provider_opt() -> str | None:
    """Default provider option."""
    return typer.Option(
        None,
        "--provider",
        "-x",
        help="Provider override (claude, codex, kiro, cursor)",
    )


def create_model_command(
    app: typer.Typer,
    name: str,
    model_alias: str,
    help_text: str,
):
    """Create a model command and register it with the app.

    Args:
        app: Typer app to register command with
        name: Command name
        model_alias: Model alias to pass to runner
        help_text: Help text for command
    """

    @app.command(name)
    def model_cmd(
        provider: str | None = _provider_opt(),
        resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
        cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
        print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
        debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
        add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
        output_format: str | None = typer.Option(
            None, "--output-format", help="Output format when --print: text, json, stream-json"
        ),
        continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
        prompt: str | None = typer.Argument(None, help="Startup prompt"),
    ) -> None:
        """Model shortcut command."""
        from thegent.clode_main import _run_model_interactive

        _run_model_interactive(
            model_alias,
            provider=provider,
            resume=resume,
            prompt=prompt,
            cd=cd,
            print_mode=print_mode,
            debug=debug,
            add_dir=add_dir or None,
            output_format=output_format,
            continue_session=continue_session,
        )

    model_cmd.__doc__ = help_text
    return model_cmd


# Model definitions: (command_name, model_alias, help_text)
MODEL_COMMANDS = [
    ("comp", "comp", "Composer 1 (via Cursor). Use -x cursor to lock."),
    ("composer", "composer", "Composer 1.5 (via Cursor). Use -x cursor to lock."),
    ("haiku", "haiku", "Claude Haiku 4.5 balanced across claude, antigravity, codex, kiro."),
    ("opus", "opus", "Claude Opus 4.5 via claude, codex (proxy), kiro."),
    ("opus1m", "opus1m", "Claude Opus 4.5 with 1M context via claude."),
    ("sonnet", "sonnet", "Claude Sonnet 4 balanced across claude, antigravity, codex, kiro."),
    ("step", "step", "Step reasoning model via OpenAI (o1) or Anthropic."),
    ("flash", "flash", "Gemini 2.0 Flash via gemini-cli or codex (proxy)."),
    ("mini", "mini", "GPT-4o-mini via codex (proxy API)."),
    ("high", "high", "Claude 3.5/4 Sonnet high via claude, codex, kiro."),
    ("xhigh", "xhigh", "Claude 3.5/4 Opus via claude, codex, kiro."),
    ("free", "free", "Free models: gemini-2.0-flash, cursor-flash."),
    ("glm", "glm", "GLM-4 (Zhipu) via codex proxy API."),
    ("max", "max", "Claude Max (extended) via claude, kiro."),
]


def register_model_commands(app: typer.Typer) -> None:
    """Register all model commands with the app.

    Args:
        app: Typer app to register commands with
    """
    for cmd_name, model_alias, help_text in MODEL_COMMANDS:
        create_model_command(app, cmd_name, model_alias, help_text)


__all__ = [
    "MODEL_COMMANDS",
    "create_model_command",
    "register_model_commands",
]
