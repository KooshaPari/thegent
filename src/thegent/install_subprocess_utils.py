"""Shared subprocess helpers for install workflows."""

import shutil
import subprocess

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from thegent.infra import run_subprocess_optimized


def command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def run_command(
    cmd: list[str],
    check: bool = False,
    capture_output: bool = True,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> tuple[int, str, str]:
    """Run a shell command with retry logic using tenacity.

    Returns (returncode, stdout, stderr).
    """

    @retry(
        stop=stop_after_attempt(retries),
        wait=wait_random_exponential(multiplier=retry_delay, min=retry_delay, max=10),
        retry=retry_if_exception_type((subprocess.TimeoutExpired, Exception)),
        reraise=True,
    )
    def _run_with_tenacity() -> tuple[int, str, str]:
        result = run_subprocess_optimized(cmd, check=check, capture_output=capture_output, timeout=300)
        stdout_text = (
            result.stdout.strip()
            if isinstance(result.stdout, str)
            else (result.stdout.decode("utf-8", errors="replace").strip() if result.stdout else "")
        )
        stderr_text = (
            result.stderr.strip()
            if isinstance(result.stderr, str)
            else (result.stderr.decode("utf-8", errors="replace").strip() if result.stderr else "")
        )
        return result.returncode, stdout_text, stderr_text

    try:
        return _run_with_tenacity()
    except Exception as e:
        return 1, "", str(e) or "Command failed after retries"
