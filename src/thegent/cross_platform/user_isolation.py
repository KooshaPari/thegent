"""System User abstraction for cross-platform agent execution.

This module provides SystemUser and AgentUser classes that abstract
the distinction between system-level and agent-level user contexts
for secure cross-platform operation.
"""

from __future__ import annotations

import logging
import os
import platform
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


_LOG = logging.getLogger(__name__)


class UserContext(ABC):
    """Abstract base class for user contexts."""

    @property
    @abstractmethod
    def user_id(self) -> int:
        """Return the user ID."""

    @property
    @abstractmethod
    def user_name(self) -> str:
        """Return the username."""

    @property
    @abstractmethod
    def home_dir(self) -> Path:
        """Return the home directory."""

    @property
    @abstractmethod
    def is_privileged(self) -> bool:
        """Check if running with elevated privileges."""

    @abstractmethod
    def can_access_path(self, path: Path) -> bool:
        """Check if user can access a given path."""

    @abstractmethod
    def get_environment_vars(self) -> dict[str, str]:
        """Get environment variables visible to this user."""


class SystemUser(UserContext):
    """System-level user context (root/sudo on Unix, Administrator on Windows).

    Used for system-wide installations, global configuration, and
    administrative tasks that require elevated privileges.
    """

    def __init__(self) -> None:
        """Initialize system user context."""
        self._system = platform.system()
        self._uid = 0 if self._system != "Windows" else 0  # 0 = root on Unix, not used on Windows
        self._check_privileged()

    def _check_privileged(self) -> bool:
        """Check if running with elevated privileges."""
        if self._system == "Windows":
            try:
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            return os.geteuid() == 0

    @property
    def user_id(self) -> int:
        """Return the user ID (0 for root)."""
        return 0

    @property
    def user_name(self) -> str:
        """Return the username (root or SYSTEM on Windows)."""
        if self._system == "Windows":
            return "SYSTEM"
        return "root"

    @property
    def home_dir(self) -> Path:
        """Return system directories."""
        if self._system == "Windows":
            return Path(os.environ.get("SYSTEMROOT", "C:\\Windows"))
        return Path("/")

    @property
    def is_privileged(self) -> bool:
        """Check if running with elevated privileges."""
        return self._check_privileged()

    def can_access_path(self, path: Path) -> bool:
        """System user can access any path (if permissions allow)."""
        try:
            return path.exists() or self.is_privileged
        except (OSError, PermissionError):
            return self.is_privileged

    def get_environment_vars(self) -> dict[str, str]:
        """Get system environment variables."""
        return dict(os.environ)


class AgentUser(UserContext):
    """Agent-level user context for isolated agent execution.

    Represents the user context under which agents operate, providing
    isolation from the host system user and ensuring secure, controlled
    execution environment.
    """

    def __init__(
        self,
        agent_id: str | None = None,
        agent_home: Path | None = None,
    ) -> None:
        """Initialize agent user context.

        Args:
            agent_id: Unique identifier for the agent
            agent_home: Custom home directory for the agent (defaults to temp)
        """
        self._system = platform.system()
        self._agent_id = agent_id or f"agent-{os.getpid()}"
        self._agent_home = agent_home or self._get_default_agent_home()
        self._uid = os.getuid() if self._system != "Windows" else 1000
        self._create_agent_home()

    def _get_default_agent_home(self) -> Path:
        """Get default agent home directory."""
        if self._system == "Windows":
            base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        else:
            base = Path.home() / ".thegent" / "agents"
        return base / self._agent_id

    def _create_agent_home(self) -> None:
        """Create agent home directory if it doesn't exist."""
        try:
            self._agent_home.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback to temp directory
            import tempfile

            self._agent_home = Path(tempfile.gettempdir()) / "thegent" / self._agent_id
            self._agent_home.mkdir(parents=True, exist_ok=True)

    @property
    def user_id(self) -> int:
        """Return the agent's user ID (same as host user)."""
        return self._uid

    @property
    def user_name(self) -> str:
        """Return the agent username."""
        return f"agent:{self._agent_id}"

    @property
    def home_dir(self) -> Path:
        """Return the agent's home directory."""
        return self._agent_home

    @property
    def is_privileged(self) -> bool:
        """Check if agent has elevated privileges (typically false)."""
        if self._system == "Windows":
            try:
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                return False
        else:
            return os.geteuid() == 0

    def can_access_path(self, path: Path) -> bool:
        """Check if agent can access a given path.

        Agents are typically restricted to their home directory and
        any explicitly granted paths.
        """
        try:
            # Check if path exists and is readable
            if not path.exists():
                return False

            # Check parent directory traversal for agent home
            try:
                resolved = path.resolve()
                agent_home_resolved = self._agent_home.resolve()

                # Allow if within agent home or explicitly readable
                if str(resolved).startswith(str(agent_home_resolved)):
                    return True

            except (OSError, ValueError):
                pass

            # Check read permission
            return os.access(path, os.R_OK)

        except (OSError, PermissionError):
            return False

    def get_environment_vars(self) -> dict[str, str]:
        """Get filtered environment variables for agent.

        Returns a sanitized set of environment variables suitable
        for agent execution.
        """
        # Filter out sensitive variables
        sensitive_keys = {
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AZURE_CLIENT_SECRET",
            "GITHUB_TOKEN",
            "GITLAB_TOKEN",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "DATABASE_PASSWORD",
            "PASSWORD",
            "SECRET",
            "TOKEN",
        }

        env = {}
        for key, value in os.environ.items():
            # Skip sensitive keys
            if any(s in key.upper() for s in sensitive_keys):
                env[key] = "***REDACTED***"
            else:
                env[key] = value

        # Add agent-specific variables
        env["THEGENT_AGENT_ID"] = self._agent_id
        env["THEGENT_AGENT_HOME"] = str(self._agent_home)

        return env


def get_user_context(
    context_type: str = "agent",
    **kwargs: Any,
) -> UserContext:
    """Factory function to get a user context.

    Args:
        context_type: Type of context ('system' or 'agent')
        **kwargs: Additional arguments passed to context constructor

    Returns:
        UserContext instance

    Raises:
        ValueError: If context_type is invalid
    """
    if context_type == "system":
        return SystemUser()
    if context_type == "agent":
        return AgentUser(**kwargs)
    raise ValueError(f"Unknown context type: {context_type}")
