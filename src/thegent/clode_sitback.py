"""Sitback commands for clode CLI.

Provides human-interactive AI sessions with optional tmux support.
Extracted from clode_main.py for maintainability.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING



# Flag for bypassing restrictions
_CLODE_BYPASS_FLAG = "--bypass"


def _is_triggered_by_agent_process() -> bool:
    """Check if this was triggered by an agent process."""
    return bool(os.environ.get("THEGENT_AGENT_RUN") or os.environ.get("CLAUDE_CODE_AGENT"))


def wrap_with_caffeinate(cmd: list[str], label: str) -> list[str]:
    """Wrap command with caffeinate on macOS to prevent sleep.
    
    Args:
        cmd: Command to wrap
        label: Label for debugging
        
    Returns:
        Wrapped command or original if not macOS
    """
    if sys.platform != "darwin":
        return cmd
    
    if not shutil.which("caffeinate"):
        return cmd
    
    return ["caffeinate", "-i", *cmd]


def _run_sitback_claude(
    claude_path: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run Claude with startup prompt in current terminal or tmux."""
    from thegent.infra.shim_subprocess import run as shim_run
    
    model = env.get("ANTHROPIC_MODEL", "MiniMax-M2.5")
    cmd = [claude_path, "--model", model]
    
    if not _is_triggered_by_agent_process():
        cmd.insert(1, _CLODE_BYPASS_FLAG)
    
    if startup_path:
        prompt = Path(startup_path).read_text()
        cmd.append(prompt)

    if tmux:
        session_name = f"sitback-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        run_args = wrap_with_caffeinate(run_args, "claude")

        with contextlib.suppress(KeyboardInterrupt):
            shim_run(
                run_args,
                check=False,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
    else:
        cmd = wrap_with_caffeinate(cmd, "claude")
        os.execvpe(cmd[0], cmd, env)


def _run_sitback_codex(
    codex_path: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run Codex with startup prompt in current terminal or tmux."""
    from thegent.infra.shim_subprocess import run as shim_run
    
    model = env.get("OPENAI_MODEL", "gpt-4o")
    cmd = [codex_path, "--model", model]
    
    if startup_path:
        prompt = Path(startup_path).read_text()
        cmd.extend(["--prompt", prompt])

    if tmux:
        session_name = f"sitback-codex-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        run_args = wrap_with_caffeinate(run_args, "codex")

        with contextlib.suppress(KeyboardInterrupt):
            shim_run(
                run_args,
                check=False,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
    else:
        cmd = wrap_with_caffeinate(cmd, "codex")
        os.execvpe(cmd[0], cmd, env)


def _run_sitback_droid(
    droid_path: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run droid (Gemini) with startup prompt."""
    from thegent.infra.shim_subprocess import run as shim_run
    
    model = env.get("GEMINI_MODEL", "gemini-2.0-flash")
    cmd = [droid_path, "--model", model]
    
    if startup_path:
        prompt = Path(startup_path).read_text()
        cmd.append(prompt)

    if tmux:
        session_name = f"sitback-droid-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        run_args = wrap_with_caffeinate(run_args, "droid")

        with contextlib.suppress(KeyboardInterrupt):
            shim_run(run_args, check=False, env=env)
    else:
        cmd = wrap_with_caffeinate(cmd, "droid")
        os.execvpe(cmd[0], cmd, env)


# Model aliases for sitback --model
SITBACK_MODEL_ALIASES: dict[str, str] = {
    "dex": "gpt-5.3-codex",
    "codex": "gpt-5.3-codex",
    "comp": "composer-1",
    "composer": "composer-1.5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "glm": "glm-5",
    "glm5": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "opus1m": "claude-opus-4.6-1m",
    "sonnet": "claude-sonnet-4",
    "step": "step-3.5-flash",
    "flash": "gemini-3-flash",
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
}


def resolve_sitback_model(model_alias: str) -> str:
    """Resolve a model alias to its full model name."""
    return SITBACK_MODEL_ALIASES.get(model_alias.lower(), model_alias)


__all__ = [
    "SITBACK_MODEL_ALIASES",
    "_run_sitback_claude",
    "_run_sitback_codex",
    "_run_sitback_droid",
    "resolve_sitback_model",
    "wrap_with_caffeinate",
]
