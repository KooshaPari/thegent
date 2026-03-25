"""Platform-specific path resolution following OS conventions."""

import os
from pathlib import Path

from thegent_platform.thg_platform import Platform, detect_platform

__all__ = [
    "get_bin_dir",
    "get_config_dir",
]


def get_bin_dir() -> Path:
    """Get platform-specific binary directory.

    Follows OS conventions:
    - macOS/Linux: ~/.local/bin
    - Windows: %LOCALAPPDATA%/thegent/bin

    Returns:
        Path to binary directory (created if needed)
    """
    plat = detect_platform()
    home = Path.home()

    if plat == Platform.WINDOWS:
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            bin_dir = Path(localappdata) / "thegent" / "bin"
        else:
            bin_dir = home / "AppData" / "Local" / "thegent" / "bin"
    else:
        # macOS and Linux follow XDG / POSIX convention
        bin_dir = home / ".local" / "bin"

    bin_dir.mkdir(parents=True, exist_ok=True)
    return bin_dir


def get_config_dir() -> Path:
    """Get platform-specific configuration directory.

    Follows OS conventions:
    - macOS: ~/Library/Application Support/thegent
    - Linux: ~/.config/thegent
    - Windows: %APPDATA%/thegent

    Returns:
        Path to configuration directory (created if needed)
    """
    plat = detect_platform()
    home = Path.home()

    if plat == Platform.MACOS:
        config_dir = home / "Library" / "Application Support" / "thegent"
    elif plat == Platform.WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_dir = Path(appdata) / "thegent"
        else:
            # Fallback to user profile
            config_dir = home / "AppData" / "Roaming" / "thegent"
    else:
        # Linux/Other
        config_dir = home / ".config" / "thegent"

    # Allow override via ThegentSettings
    from thegent_core.config import ThegentSettings

    settings = ThegentSettings()
    if settings.config_dir_override is not None:
        config_dir = settings.config_dir_override.expanduser()

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir
