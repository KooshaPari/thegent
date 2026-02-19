"""Cross-platform detection and utilities."""

import os
import platform
from enum import Enum

__all__ = [
    "Platform",
    "detect_platform",
    "get_architecture",
    "get_platform_name",
    "is_linux",
    "is_macos",
    "is_unix",
    "is_windows",
]


class Platform(Enum):
    """Supported platforms."""

    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    WSL2 = "wsl2"
    UNKNOWN = "unknown"


# Cache platform detection result
_platform_cache: Platform | None = None


def detect_platform() -> Platform:
    """Detect current platform.

    Returns:
        Platform enum value (MACOS, LINUX, WINDOWS, WSL2, or UNKNOWN)

    Examples:
        >>> plat = detect_platform()
        >>> plat == Platform.MACOS
        True
    """
    global _platform_cache

    # Return cached result if available
    if _platform_cache is not None:
        return _platform_cache

    system = platform.system().lower()

    # WSL2 detection (must check before generic Linux)
    if system == "linux":
        if os.path.exists("/proc/version"):
            try:
                with open("/proc/version", encoding="utf-8") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        _platform_cache = Platform.WSL2
                        return _platform_cache
            except OSError:
                pass

        # Also check for WSL2-specific environment variables
        if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
            _platform_cache = Platform.WSL2
            return _platform_cache

        _platform_cache = Platform.LINUX
        return _platform_cache

    if system == "darwin":
        _platform_cache = Platform.MACOS
        return _platform_cache

    if system == "windows":
        _platform_cache = Platform.WINDOWS
        return _platform_cache

    _platform_cache = Platform.UNKNOWN
    return _platform_cache


def get_platform_name() -> str:
    """Get platform name as string.

    Returns:
        Platform name: "macos", "linux", "windows", "wsl2", or "unknown"

    Examples:
        >>> get_platform_name()
        'macos'
    """
    return detect_platform().value


def is_windows() -> bool:
    """Check if running on Windows (including WSL2).

    Returns:
        True if Windows or WSL2, False otherwise

    Examples:
        >>> is_windows()
        False  # on macOS/Linux
    """
    plat = detect_platform()
    return plat in (Platform.WINDOWS, Platform.WSL2)


def is_unix() -> bool:
    """Check if running on Unix-like system (macOS, Linux, WSL2).

    Returns:
        True if macOS, Linux, or WSL2, False otherwise

    Examples:
        >>> is_unix()
        True  # on macOS/Linux
    """
    plat = detect_platform()
    return plat in (Platform.MACOS, Platform.LINUX, Platform.WSL2)


def is_macos() -> bool:
    """Check if running on macOS.

    Returns:
        True if macOS, False otherwise

    Examples:
        >>> is_macos()
        True  # on macOS
    """
    return detect_platform() == Platform.MACOS


def is_linux() -> bool:
    """Check if running on Linux (not WSL2).

    Returns:
        True if Linux (not WSL2), False otherwise

    Examples:
        >>> is_linux()
        True  # on Linux (not WSL2)
    """
    return detect_platform() == Platform.LINUX


def get_architecture() -> str:
    """Get system architecture.

    Returns:
        Architecture string: "x86_64", "arm64", "aarch64", "i386", etc.

    Examples:
        >>> get_architecture()
        'arm64'  # on Apple Silicon Mac
    """
    machine = platform.machine().lower()

    # Normalize architecture names
    arch_map = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv7l": "armv7",
        "i386": "i386",
        "i686": "i386",
    }

    return arch_map.get(machine, machine)
