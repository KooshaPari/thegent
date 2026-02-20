"""Hook runner with shell detection and cross-platform support."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from thegent.config import get_settings
from thegent.infra.shell_detection import ShellType, get_preferred_shell, get_shell_executable


def run_hook(hook_path: Path, input_data: str | None = None, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a hook script using the preferred shell."""
    settings = get_settings()

    # 1. Determine shell to use
    if settings.hook_shell:
        shell_type = ShellType(settings.hook_shell.lower())
    else:
        # For hooks, always use high-performance shells (dash/cmd)
        shell_type = get_preferred_shell(performance=True)

    shell_exe = get_shell_executable(shell_type)

    # 2. Build command
    cmd = [shell_exe, str(hook_path)]

    # 3. Handle Windows peculiarities (pwsh/powershell need -File)
    if shell_type in [ShellType.PWSH, ShellType.POWERSHELL]:
        cmd = [shell_exe, "-NoProfile", "-NonInteractive", "-File", str(hook_path)]

    # 4. Execute
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return result
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=124,
            stdout=e.stdout.decode() if e.stdout else "",
            stderr=f"Hook timed out after {timeout}s\n" + (e.stderr.decode() if e.stderr else "")
        )
    except Exception as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr=f"Failed to run hook: {e}"
        )


def main():
    """CLI entry point for running a hook."""
    if len(sys.argv) < 2:
        sys.exit(1)

    hook_path = Path(sys.argv[1])
    input_data = sys.stdin.read() if not sys.stdin.isatty() else None

    result = run_hook(hook_path, input_data)

    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
