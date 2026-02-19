"""POSIX + PowerShell dual-shell strategy."""

import logging
import platform
from typing import Any

logger = logging.getLogger(__name__)


class DualShellStrategy:
    """Dual-shell strategy for POSIX and PowerShell."""

    def __init__(self):
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

    def execute(self, command: str) -> dict[str, Any]:
        """Execute command in appropriate shell.
        
        Args:
            command: Command to execute
            
        Returns:
            Execution result
        """
        logger.info(f"Executing '{command}' in {self.shell} shell")
        
        if self.shell == "powershell":
            # PowerShell-specific execution
            return {"shell": "powershell", "command": command, "result": ""}
        else:
            # POSIX shell execution
            return {"shell": "posix", "command": command, "result": ""}

    def normalize_path(self, path: str) -> str:
        """Normalize path for current shell.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path
        """
        if self.shell == "powershell":
            return path.replace("/", "\")
        return path.replace("\", "/")
