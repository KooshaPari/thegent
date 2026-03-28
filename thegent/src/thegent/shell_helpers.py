"""Shell helpers for thegent.

Common shell utilities.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path


Command = str | Sequence[str]


def run(cmd: Command, shell: bool = True, cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and capture its exit code, stdout, and stderr."""
    if isinstance(cmd, Sequence) and not isinstance(cmd, str):
        command: str | list[str] = [str(part) for part in cmd]
        use_shell = False
    elif shell:
        command = cmd
        use_shell = True
    else:
        command = shlex.split(cmd)
        use_shell = False

    result = subprocess.run(
        command,
        shell=use_shell,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def exists(cmd: str) -> bool:
    """Check if command exists without spawning a shell."""
    return shutil.which(cmd) is not None


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """Check if file exists."""
    return path.exists()

