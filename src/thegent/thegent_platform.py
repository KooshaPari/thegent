"""Cross-platform detection and utilities."""

import logging
import os
import platform
from enum import Enum
from typing import TypedDict

_LOG = logging.getLogger(__name__)
_PROC_VERSION_WARNING_LIMIT = 3


class PlatformDiagnostics(TypedDict):
    proc_version_read_failures: int
    last_proc_version_error_type: str | None
    last_proc_version_error_message: str | None


_platform_diagnostics: PlatformDiagnostics = {
    "proc_version_read_failures": 0,
    "last_proc_version_error_type": None,
    "last_proc_version_error_message": None,
}


def get_platform_detection_diagnostics() -> PlatformDiagnostics:
    """Return diagnostics for platform detection edge cases."""
    return {
        "proc_version_read_failures": _platform_diagnostics["proc_version_read_failures"],
        "last_proc_version_error_type": _platform_diagnostics["last_proc_version_error_type"],
        "last_proc_version_error_message": _platform_diagnostics["last_proc_version_error_message"],
    }


def reset_platform_detection_diagnostics() -> None:
    """Reset platform detection diagnostics (test helper)."""
    _platform_diagnostics["proc_version_read_failures"] = 0
    _platform_diagnostics["last_proc_version_error_type"] = None
    _platform_diagnostics["last_proc_version_error_message"] = None


class Platform(Enum):
    """Supported platforms."""

    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    WSL2 = "wsl2"
    UNKNOWN = "unknown"


def detect_platform() -> Platform:
    """Detect current platform.

    Returns:
        Platform enum value (MACOS, LINUX, WINDOWS, WSL2, or UNKNOWN)
    """
    system = platform.system().lower()

    if system == "darwin":
        return Platform.MACOS

    if system == "windows":
        return Platform.WINDOWS

    if system == "linux":
        # Check for WSL2
        if os.path.exists("/proc/version"):
            try:
                with open("/proc/version", encoding="utf-8") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        return Platform.WSL2
            except OSError as exc:
                failures = _platform_diagnostics["proc_version_read_failures"] + 1
                _platform_diagnostics["proc_version_read_failures"] = failures
                _platform_diagnostics["last_proc_version_error_type"] = type(exc).__name__
                _platform_diagnostics["last_proc_version_error_message"] = str(exc)
                if failures <= _PROC_VERSION_WARNING_LIMIT:
                    _LOG.warning(
                        "detect_platform: failed to read /proc/version (%s); continuing with env-based detection",
                        type(exc).__name__,
                    )

        # Also check for WSL2-specific environment variables
        if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
            return Platform.WSL2

        return Platform.LINUX

    return Platform.UNKNOWN
