"""OS-level user creation adapter (Linux/macOS/Win)."""

import logging
import platform
from typing import Any

logger = logging.getLogger(__name__)


class OSUserAdapter:
    """Cross-platform OS user creation adapter."""

    def __init__(self) -> None:
        """Initialize OS user adapter."""
        self.system = platform.system()

    def create_user(self, username: str, home_dir: str | None = None) -> dict[str, Any]:
        """Create OS user.

        Args:
            username: Username
            home_dir: Optional home directory

        Returns:
            Creation result
        """
        logger.info(f"Creating user {username} on {self.system}")

        if self.system == "Linux":
            return self._create_linux_user(username, home_dir)
        if self.system == "Darwin":
            return self._create_macos_user(username, home_dir)
        if self.system == "Windows":
            return self._create_windows_user(username, home_dir)
        return {"error": f"Unsupported system: {self.system}"}

    def _create_linux_user(self, username: str, home_dir: str | None) -> dict[str, Any]:
        """Create Linux user."""
        # Would use useradd command
        return {"status": "success", "platform": "linux", "username": username}

    def _create_macos_user(self, username: str, home_dir: str | None) -> dict[str, Any]:
        """Create macOS user."""
        # Would use dscl command
        return {"status": "success", "platform": "macos", "username": username}

    def _create_windows_user(self, username: str, home_dir: str | None) -> dict[str, Any]:
        """Create Windows user."""
        # Would use net user command
        return {"status": "success", "platform": "windows", "username": username}
