"""POSIX + PowerShell dual-shell strategy."""

import logging
import platform
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class DualShellStrategy:
    """Dual-shell strategy for POSIX and PowerShell."""

    def __init__(self) -> None:
        """Initialize shell strategy."""
        self.system = platform.system()
        self.shell = self._detect_shell()

    def _detect_shell(self) -> str:
        """Detect shell type.

        Returns:
            Shell type (posix or powershell)
        """
        if self.system == "Windows":
            return "powershell"
        return "posix"

    def execute(self, command: str, capture_output: bool = True) -> dict[str, Any]:
        """Execute command in appropriate shell.

        Args:
            command: Command to execute
            capture_output: Whether to capture stdout/stderr

        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing '{command}' in {self.shell} shell")

        try:
            if self.shell == "powershell":
                # PowerShell-specific execution
                result = subprocess.run(
                    ["powershell", "-Command", command], capture_output=capture_output, text=True, check=False
                )
            else:
                # POSIX shell execution (bash/zsh)
                result = subprocess.run(command, shell=True, capture_output=capture_output, text=True, check=False)

            return {
                "shell": self.shell,
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "success": result.returncode == 0,
            }
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "shell": self.shell,
                "command": command,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }

    def normalize_path(self, path: str) -> str:
        """Normalize path for current shell.

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        if self.shell == "powershell":
            return path.replace("/", "\\")
        return path.replace("\\", "/")
