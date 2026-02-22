"""Harmonized path strategy across all integrated systems."""

import os
from pathlib import Path

from thegent.platform_paths import get_config_dir
from thegent.thg_platform import Platform, detect_platform

__all__ = ["HarmonizedPathManager"]


class HarmonizedPathManager:
    """Harmonize paths across systems.

    This class creates consistent path mappings across all integrated systems
    (thegent, manage devkit, workstream, plan system) to ensure harmonious
    directory structures.

    Examples:
        >>> paths = HarmonizedPathManager()
        >>> config_path = paths.get_harmonized_path("thegent", "config")
        >>> paths.create_shared_structure()
    """

    def __init__(self) -> None:
        """Initialize harmonized path manager."""
        self.path_mappings: dict[str, dict[str, Path]] = {}
        self._build_path_mappings()

    def _build_path_mappings(self) -> None:
        """Build path mappings for all systems."""
        plat = detect_platform()

        # Base directories
        if plat == Platform.MACOS:
            base_config = Path.home() / "Library" / "Application Support"
            base_cache = Path.home() / "Library" / "Caches"
            base_data = Path.home() / "Library" / "Application Support"
        elif plat in (Platform.LINUX, Platform.WSL2):
            base_config = Path.home() / ".config"
            base_cache = Path.home() / ".cache"
            base_data = Path.home() / ".local" / "share"
        else:  # Windows
            appdata = os.environ.get("APPDATA", "")
            localappdata = os.environ.get("LOCALAPPDATA", "")
            base_config = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
            base_cache = Path(localappdata) / "cache" if localappdata else Path.home() / "AppData" / "Local" / "cache"
            base_data = Path(localappdata) if localappdata else Path.home() / "AppData" / "Local"

        # Harmonized paths
        self.path_mappings = {
            "thegent": {
                "config": get_config_dir(),
                "cache": base_cache / "thegent",
                "data": base_data / "thegent",
                "bin": Path.home() / ".local" / "bin",
                "log": base_data / "thegent" / "logs",
                "temp": Path("/tmp") / "thegent",
            },
            "manage": {
                "config": base_config / "manage",
                "cache": base_cache / "manage",
                "data": base_data / "manage",
            },
            "workstream": {
                "config": base_config / "workstream",
                "cache": base_cache / "workstream",
                "data": base_data / "workstream",
            },
            "plan": {
                "config": base_config / "plan",
                "cache": base_cache / "plan",
                "data": base_data / "plan",
            },
        }

    def get_harmonized_path(self, system: str, path_type: str) -> Path | None:
        """Get harmonized path for system.

        Args:
            system: System name (thegent, manage, workstream, plan)
            path_type: Path type (config, cache, data, bin, log, temp)

        Returns:
            Path object, or None if not found
        """
        system_paths = self.path_mappings.get(system, {})
        return system_paths.get(path_type)

    def create_shared_structure(self) -> None:
        """Create shared directory structure.

        Creates common parent directories and ensures consistent structure
        across all integrated systems.
        """
        # Create all directories
        for system_paths in self.path_mappings.values():
            for path in system_paths.values():
                if path:
                    path.mkdir(parents=True, exist_ok=True)

        # Create shared parent directories if needed
        plat = detect_platform()

        if plat == Platform.MACOS:
            # Ensure Library directories exist
            (Path.home() / "Library" / "Application Support").mkdir(parents=True, exist_ok=True)
            (Path.home() / "Library" / "Caches").mkdir(parents=True, exist_ok=True)
        elif plat in (Platform.LINUX, Platform.WSL2):
            # Ensure XDG directories exist
            (Path.home() / ".config").mkdir(parents=True, exist_ok=True)
            (Path.home() / ".cache").mkdir(parents=True, exist_ok=True)
            (Path.home() / ".local" / "share").mkdir(parents=True, exist_ok=True)
        else:  # Windows
            # Ensure AppData directories exist
            appdata = os.environ.get("APPDATA")
            localappdata = os.environ.get("LOCALAPPDATA")
            if appdata:
                Path(appdata).mkdir(parents=True, exist_ok=True)
            if localappdata:
                Path(localappdata).mkdir(parents=True, exist_ok=True)
