"""Cross-platform detection and utilities."""

import os
import platform
from enum import Enum


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
            except OSError:
                pass

        # Also check for WSL2-specific environment variables
        if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
            return Platform.WSL2

        return Platform.LINUX

    return Platform.UNKNOWN
