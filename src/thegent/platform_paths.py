"""Platform-specific path resolution following OS conventions."""

import os
from pathlib import Path

from thegent.thg_platform import Platform, detect_platform

__all__ = [
    "get_config_dir",
]


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
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    if settings.config_dir_override is not None:
        config_dir = settings.config_dir_override.expanduser()

    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir
