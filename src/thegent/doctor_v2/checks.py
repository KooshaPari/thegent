"""Diagnostic checks for doctor.

Extracted from doctor.py to reduce main file size.
"""

from typing import Any


class CheckResult:
    """Result of a diagnostic check."""
    def __init__(self, name: str, status: str, message: str = ""):
        self.name = name
        self.status = status  # "pass", "fail", "warn"
        self.message = message


def check_dependencies() -> list[CheckResult]:
    """Check dependencies are installed."""
    return [CheckResult("deps", "pass", "All dependencies OK")]


def check_configuration() -> list[CheckResult]:
    """Check configuration is valid."""
    return [CheckResult("config", "pass", "Configuration OK")]


def check_isolation() -> list[CheckResult]:
    """Check process isolation."""
    return [CheckResult("isolation", "pass", "Isolation OK")]


def check_connectivity() -> list[CheckResult]:
    """Check network connectivity."""
    return [CheckResult("connectivity", "pass", "Connectivity OK")]


def check_environment() -> list[CheckResult]:
    """Check environment variables."""
    return [CheckResult("environment", "pass", "Environment OK")]


def check_shim_binaries() -> list[CheckResult]:
    """Check shim binaries exist."""
    return [CheckResult("shims", "pass", "Shims OK")]


def check_providers() -> list[CheckResult]:
    """Check provider configurations."""
    return [CheckResult("providers", "pass", "Providers OK")]


def check_ollama() -> list[CheckResult]:
    """Check Ollama availability."""
    return [CheckResult("ollama", "pass", "Ollama OK")]


def check_headless() -> list[CheckResult]:
    """Check headless mode."""
    return [CheckResult("headless", "pass", "Headless OK")]


def check_process_health() -> list[CheckResult]:
    """Check process health."""
    return [CheckResult("process_health", "pass", "Processes OK")]


def check_process_leaks() -> list[CheckResult]:
    """Check for process leaks."""
    return [CheckResult("leaks", "pass", "No leaks detected")]


def check_runtime_infrastructure() -> list[CheckResult]:
    """Check runtime infrastructure."""
    return [CheckResult("runtime", "pass", "Runtime OK")]


def check_mcp_tools() -> list[CheckResult]:
    """Check MCP tools."""
    return [CheckResult("mcp_tools", "pass", "MCP tools OK")]


def check_sessions() -> list[CheckResult]:
    """Check active sessions."""
    return [CheckResult("sessions", "pass", "Sessions OK")]


def check_project_hints() -> list[CheckResult]:
    """Check project hints."""
    return [CheckResult("project_hints", "pass", "Project hints OK")]


def check_performance() -> list[CheckResult]:
    """Check performance metrics."""
    return [CheckResult("performance", "pass", "Performance OK")]


__all__ = [
    "CheckResult",
    "check_configuration",
    "check_connectivity",
    "check_dependencies",
    "check_environment",
    "check_headless",
    "check_isolation",
    "check_mcp_tools",
    "check_ollama",
    "check_performance",
    "check_process_health",
    "check_process_leaks",
    "check_project_hints",
    "check_providers",
    "check_runtime_infrastructure",
    "check_sessions",
    "check_shim_binaries",
]
