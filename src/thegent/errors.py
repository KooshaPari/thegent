"""Production error handling framework for thegent."""

from thegent.thegent_platform import Platform, detect_platform


class ThegentError(Exception):
    """Base class for all errors in thegent.

    Attributes:
        message: The error message.
        remediation_hint: A human-readable hint on how to fix the error.
    """

    def __init__(self, message: str, remediation_hint: str | None = None) -> None:
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

    def __init__(
        self, message: str, remediation_hint: str | None = "Check your config.yaml or environment variables."
    ) -> None:
        super().__init__(message, remediation_hint)


class ProviderError(ThegentError):
    """Raised when an AI provider (Anthropic, Google, etc.) returns an error."""

    def __init__(self, message: str, remediation_hint: str | None = "Check your API keys and provider status.") -> None:
        super().__init__(message, remediation_hint)


class MCPError(ThegentError):
    """Raised when an MCP-related failure occurs."""

    def __init__(
        self, message: str, remediation_hint: str | None = "Ensure the MCP server is running and reachable."
    ) -> None:
        super().__init__(message, remediation_hint)


def print_error(message: str, hint: str | None = None, console=None) -> None:
    """Print a formatted error message with an optional remediation hint.

    Args:
        message: The error message to display.
        hint: An optional hint on how to fix the error.
        console: A Rich console object (optional).
    """
    if console is None:
        from rich.console import Console

        console = Console()

    # Try to find a hint if none provided
    if hint is None:
        hint = get_hint_for_message(message)

    console.print(f"[bold red]Error:[/bold red] {message}")
    if hint:
        console.print(f"[bold cyan]💡 Hint:[/bold cyan] {hint}")
    elif "not found" in message.lower() or "not installed" in message.lower() or "command not found" in message.lower():
        # Try to extract tool name and provide install hint
        import re

        match = re.search(r"'(.*?)'|tool (.*?)\s|command (.*?)\s|executable (.*?)\s", message)
        if match:
            tool = next(g for g in match.groups() if g)
            if tool:
                console.print(f"[bold cyan]💡 Hint:[/bold cyan] {get_install_hint(tool.strip())}")


REMEDIATION_HINTS = {
    "connection refused": "Ensure the service (MCP, Proxy, etc.) is started and listening on the expected port.",
    "permission denied": "Try running with sudo or check file permissions.",
    "no such file or directory": "Verify the path exists and is correct.",
    "api key": "Run 'thegent cliproxy login' to configure your provider credentials.",
    "rate limit": "The provider is rate-limiting your requests. Wait a moment or check your quota.",
    "unknown command": "Run 'thegent --help' to see available commands or 'thegent doctor' to verify installation.",
    "not configured": "Run 'thegent setup' to configure the system.",
    "mcp not reachable": "Run 'thegent mcp up' to start the MCP server.",
    "proxy not reachable": "Run 'thegent mcp up' to start the CLIProxy server.",
    "authentication failed": "Check your credentials. Run 'thegent cliproxy login' to re-authenticate.",
    "timeout": "The operation timed out. Check your network connection or increase the timeout setting.",
    "git repository": "Ensure you are inside a git repository or initialize one with 'git init'.",
    "dependency missing": "Try running 'pip install -r requirements.txt' or 'uv sync'.",
    "invalid json": "Check the file format for syntax errors.",
    "occ violation": "Concurrency conflict detected. The file was modified by another process. Retry the operation.",
    "concurrency limit": "Too many active sessions. Wait for some to finish or increase limit with 'thegent concurrency set'.",
}


def get_hint_for_message(message: str) -> str | None:
    """Try to find a predefined hint for a given error message."""
    msg_lower = message.lower()
    for key, hint in REMEDIATION_HINTS.items():
        if key in msg_lower:
            return hint
    return None
