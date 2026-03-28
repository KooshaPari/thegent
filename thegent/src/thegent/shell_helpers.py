"""Shell helpers for thegent.

Common shell utilities.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

_SHELL_METACHARS = set("|&;<>()$`\n*?[]{}~")


def _normalize_command(cmd: str | Sequence[str], shell: bool) -> tuple[str | list[str], bool]:
    """Normalize commands to avoid unnecessary shell processes."""
    if isinstance(cmd, Sequence) and not isinstance(cmd, str):
        return list(cmd), False

    if not shell:
        return shlex.split(cmd), False

    # Preserve shell=True only for strings that actually need shell parsing.
    if any(char in cmd for char in _SHELL_METACHARS):
        return cmd, True

    try:
        return shlex.split(cmd), False
    except ValueError:
        return cmd, True


def run(
    cmd: str | Sequence[str], shell: bool = True, cwd: Path | None = None
) -> tuple[int, str, str]:
    """Run shell command."""
    normalized_cmd, use_shell = _normalize_command(cmd, shell)
    result = subprocess.run(
        normalized_cmd,
        shell=use_shell,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def exists(cmd: str) -> bool:
    """Check if command exists."""
    return shutil.which(cmd) is not None


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """Check if file exists."""
    return path.exists()
