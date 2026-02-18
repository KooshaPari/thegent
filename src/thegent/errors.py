"""Production error handling framework for thegent."""

from typing import Optional

from thegent.thegent_platform import Platform, detect_platform


class ThegentError(Exception):
    """Base class for all errors in thegent.

    Attributes:
        message: The error message.
        remediation_hint: A human-readable hint on how to fix the error.
    """

    def __init__(self, message: str, remediation_hint: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.remediation_hint = remediation_hint

    def __str__(self) -> str:
        if self.remediation_hint:
            return f"{self.message}\n\nHint: {self.remediation_hint}"
        return self.message


def get_install_hint(tool: str) -> str:
    """Get platform-specific installation hint for a missing tool."""
    plat = detect_platform()
    if plat == Platform.MACOS:
        return f"Install via: brew install {tool}"
    if plat in (Platform.LINUX, Platform.WSL2):
        return f"Install via: sudo apt install {tool} (or your distro's equivalent)"
    if plat == Platform.WINDOWS:
        return f"Install via: winget install {tool} (or download from official source)"
    return f"Please install '{tool}' using your system package manager."


class ConfigError(ThegentError):
    """Raised when there is a configuration-related failure."""

    def __init__(self, message: str, remediation_hint: Optional[str] = "Check your config.yaml or environment variables."):
        super().__init__(message, remediation_hint)


class ProviderError(ThegentError):
    """Raised when an AI provider (Anthropic, Google, etc.) returns an error."""

    def __init__(self, message: str, remediation_hint: Optional[str] = "Check your API keys and provider status."):
        super().__init__(message, remediation_hint)


class MCPError(ThegentError):
    """Raised when an MCP-related failure occurs."""

    def __init__(self, message: str, remediation_hint: Optional[str] = "Ensure the MCP server is running and reachable."):
        super().__init__(message, remediation_hint)
