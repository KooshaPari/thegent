"""
Shell optimization utilities.

Ensures all shell invocations use the fastest available shell (zsh > bash > sh).
"""

import os
import shutil
import subprocess
from pathlib import Path

_FASTEST_SHELL: str | None = None
_SHELL_CACHE_ENABLED = True


def get_fastest_shell() -> str:
    """
    Get fastest available shell.
    Priority: zsh > bash > sh

    Returns:
        Path to fastest available shell executable
    """
    global _FASTEST_SHELL

    if _FASTEST_SHELL and _SHELL_CACHE_ENABLED:
        return _FASTEST_SHELL

    # Check zsh first (fastest, ~2x faster than bash)
    zsh_paths = ["/bin/zsh", "/usr/bin/zsh"]
    for zsh_path in zsh_paths:
        if Path(zsh_path).exists() and os.access(zsh_path, os.X_OK):
            _FASTEST_SHELL = zsh_path
            return _FASTEST_SHELL

    # Check zsh via which
    zsh = shutil.which("zsh")
    if zsh:
        _FASTEST_SHELL = zsh
        return _FASTEST_SHELL

    # Fallback to bash
    bash_paths = ["/bin/bash", "/usr/bin/bash", "/opt/homebrew/bin/bash"]
    for bash_path in bash_paths:
        if Path(bash_path).exists() and os.access(bash_path, os.X_OK):
            _FASTEST_SHELL = bash_path
            return _FASTEST_SHELL

    bash = shutil.which("bash")
    if bash:
        _FASTEST_SHELL = bash
        return _FASTEST_SHELL

    # Final fallback
    _FASTEST_SHELL = "/bin/sh"
    return _FASTEST_SHELL


def get_shell_env(optimize_startup: bool = True) -> dict:
    """
    Get optimized environment for shell execution.

    Args:
        optimize_startup: If True, skip heavy .zshrc loading for non-interactive shells

    Returns:
        Environment dict with optimizations
    """
    env = os.environ.copy()

    if optimize_startup:
        shell = get_fastest_shell()
        # Skip .zshrc for non-interactive shells (faster startup)
        if "zsh" in shell:
            # Use empty ZDOTDIR to skip .zshrc
            env["ZDOTDIR"] = "/dev/null"
            # Or use -c flag which already skips .zshrc

    return env


def run_shell_command(
    cmd: str | list[str],
    shell: str | None = None,
    optimize_startup: bool = True,
    capture_output: bool = True,
    **kwargs,
) -> subprocess.CompletedProcess:
    """
    Run shell command using fastest available shell.

    Args:
        cmd: Command string or list to execute
        shell: Shell executable path (defaults to fastest available)
        optimize_startup: Skip heavy .zshrc loading for non-interactive
        capture_output: Capture stdout/stderr (default: True)
        **kwargs: Additional subprocess.run arguments

    Returns:
        CompletedProcess result
    """
    if shell is None:
        shell = get_fastest_shell()

    # Get optimized environment
    env = kwargs.pop("env", None)
    if env is None and optimize_startup:
        env = get_shell_env(optimize_startup=optimize_startup)

    # Set default capture_output if not specified
    if "capture_output" not in kwargs:
        kwargs["capture_output"] = capture_output
    if capture_output and "text" not in kwargs:
        kwargs["text"] = True

    # If cmd is a string, use shell=True with explicit executable
    if isinstance(cmd, str):
        return subprocess.run(cmd, shell=True, executable=shell, env=env, **kwargs)
    # If cmd is a list, prepend shell
    return subprocess.run([shell, "-c", " ".join(cmd)], env=env, **kwargs)


def popen_shell_command(
    cmd: str | list[str], shell: str | None = None, optimize_startup: bool = True, **kwargs
) -> subprocess.Popen:
    """
    Open shell process using fastest available shell.

    Args:
        cmd: Command string or list to execute
        shell: Shell executable path (defaults to fastest available)
        optimize_startup: Skip heavy .zshrc loading for non-interactive
        **kwargs: Additional subprocess.Popen arguments

    Returns:
        Popen process object
    """
    if shell is None:
        shell = get_fastest_shell()

    # Get optimized environment
    env = kwargs.pop("env", None)
    if env is None and optimize_startup:
        env = get_shell_env(optimize_startup=optimize_startup)

    # If cmd is a string, use shell=True with explicit executable
    if isinstance(cmd, str):
        return subprocess.Popen(cmd, shell=True, executable=shell, env=env, **kwargs)
    # If cmd is a list, prepend shell
    return subprocess.Popen([shell, "-c", " ".join(cmd)], env=env, **kwargs)


def reset_shell_cache():
    """Reset shell cache (useful for testing or config changes)."""
    global _FASTEST_SHELL
    _FASTEST_SHELL = None
