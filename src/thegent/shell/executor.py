"""
Shell Executor

Executes shell commands with timeout, retry, and error handling.
"""

from dataclasses import dataclass
from typing import Optional
from .config import ShellConfig
import subprocess
import time
import signal
import os


@dataclass
class ShellResult:
    """Result of shell command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool = False
    attempts: int = 1
    error_message: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


class ShellExecutor:
    """Shell command executor with retry and timeout."""

    def __init__(self, config: Optional[ShellConfig] = None):
        self.config = config or ShellConfig()
        self._process = None

    def run(
        self,
        command: str,
        timeout: Optional[float] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None
    ) -> ShellResult:
        """Execute command with retry logic."""
        actual_timeout = self.config.get_timeout(timeout)
        last_result = None

        for attempt in range(self.config.max_retries):
            result = self._execute_once(command, actual_timeout, cwd, env)
            result.attempts = attempt + 1

            if result.success:
                return result

            # Don't retry on success or certain errors
            if result.exit_code != 0 and result.exit_code != 124:  # 124 = timeout
                # Non-timeout error, no retry
                return result

            last_result = result

            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries - 1:
                delay = self.config.get_retry_delay(attempt)
                time.sleep(delay)

        # All retries exhausted
        if last_result:
            last_result.error_message = self._generate_error_message(last_result)
        return last_result

    def _execute_once(
        self,
        command: str,
        timeout: float,
        cwd: Optional[str],
        env: Optional[dict]
    ) -> ShellResult:
        """Execute command once."""
        start_time = time.time()
        timed_out = False
        exit_code = -1
        stdout = ""
        stderr = ""

        try:
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)

            self._process = subprocess.Popen(
                command,
                shell=True,
                executable=self.config.shell,
                cwd=cwd,
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create process group for cleanup
            )

            try:
                stdout_bytes, stderr_bytes = self._process.communicate(
                    timeout=timeout
                )
                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")
                exit_code = self._process.returncode

            except subprocess.TimeoutExpired:
                timed_out = True
                self._kill_process_group()
                stderr = f"Command timed out after {timeout}s"

        except Exception as e:
            stderr = str(e)
            exit_code = -1

        finally:
            self._process = None

        duration = time.time() - start_time

        return ShellResult(
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            timed_out=timed_out
        )

    def _kill_process_group(self) -> None:
        """Kill process group on timeout."""
        if self._process:
            try:
                pgid = os.getpgid(self._process.pid)
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(0.5)
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            except ProcessLookupError:
                pass

    def _generate_error_message(self, result: ShellResult) -> str:
        """Generate detailed error message."""
        parts = []

        if result.timed_out:
            parts.append(f"Command timed out after {result.duration:.1f}s")
        elif result.exit_code != 0:
            parts.append(f"Command failed with exit code {result.exit_code}")

        if result.attempts > 1:
            parts.append(f"after {result.attempts} attempts")

        if result.stderr:
            parts.append(f"stderr: {result.stderr[:500]}")

        return " | ".join(parts) if parts else "Unknown error"

    def cancel(self) -> bool:
        """Cancel running command."""
        if self._process:
            self._kill_process_group()
            return True
        return False
