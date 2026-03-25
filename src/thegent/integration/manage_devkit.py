"""Integration with manage devkit system."""

from pathlib import Path

from thegent.infra import yaml_load
from thegent.platform_paths import get_bin_dir, get_config_dir
from thegent.thg_platform import detect_platform

__all__ = ["ManageDevkitIntegration"]


class ManageDevkitIntegration:
    """Integrate with manage devkit system.

    This class handles integration with external "manage" devkit systems,
    including path sharing, tool registration, and configuration harmonization.

    Examples:
        >>> integration = ManageDevkitIntegration()
        >>> integration.integrate_paths()
        >>> integration.integrate_tools()
        >>> integration.register_with_manage()
    """

    def __init__(self) -> None:
        """Initialize manage devkit integration."""
        self.manage_config_path = self._find_manage_config()
        self.manage_config: dict = {}
        self._load_manage_config()

    def _find_manage_config(self) -> Path | None:
        """Find manage devkit configuration.

        Checks common locations for manage devkit configuration:
        - ~/.manage/config.yaml
        - ~/.config/manage/config.yaml
        - /etc/manage/config.yaml

        Returns:
            Path to manage config file, or None if not found
        """
        possible_paths = [
            Path.home() / ".manage" / "config.yaml",
            Path.home() / ".config" / "manage" / "config.yaml",
            Path("/etc/manage/config.yaml"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _load_manage_config(self) -> None:
        """Load manage devkit configuration."""
        if not self.manage_config_path:
            return

        try:
            self.manage_config = yaml_load(self.manage_config_path) or {}
        except OSError, Exception:
            self.manage_config = {}

    def integrate_paths(self) -> None:
        """Integrate thegent paths with manage devkit.

        Creates shared configuration structure if manage devkit uses
        similar directory structure. Creates symlinks to share config.
        """
        if not self.manage_config_path:
            return

        if "paths" not in self.manage_config:
            self.manage_config["paths"] = {}

        # Share config directory if manage uses similar structure
        if "config_dir" in self.manage_config.get("paths", {}):
            manage_config_dir = Path(self.manage_config["paths"]["config_dir"]).expanduser()
            thegent_config_dir = get_config_dir()

            # Create symlink or merge
            if manage_config_dir.exists():
                # Create shared config structure
                shared_config = manage_config_dir / "thegent"
                shared_config.mkdir(parents=True, exist_ok=True)

                # Symlink thegent config
                thegent_config_file = shared_config / "config.yaml"
                if not thegent_config_file.exists():
                    source_config = thegent_config_dir / "config.yaml"
                    if source_config.exists():
                        try:
                            thegent_config_file.symlink_to(source_config)
                        except OSError:
                            # Symlink failed, copy instead
                            import shutil

                            shutil.copy2(source_config, thegent_config_file)

    def integrate_tools(self) -> None:
        """Integrate thegent tools with manage devkit.

        Creates symlink to thegent binary in manage devkit bin directory.
        """
        if not self.manage_config_path:
            return

        manage_bin_dir_str = self.manage_config.get("bin_dir", "~/.manage/bin")
        manage_bin_dir = Path(manage_bin_dir_str).expanduser()
        manage_bin_dir.mkdir(parents=True, exist_ok=True)

        # Create thegent symlink in manage bin
        thegent_bin = get_bin_dir() / "thegent"
        manage_thegent = manage_bin_dir / "thegent"

        if thegent_bin.exists() and not manage_thegent.exists():
            try:
                manage_thegent.symlink_to(thegent_bin)
            except OSError:
                # Symlink failed, skip
                pass

    def register_with_manage(self) -> None:
        """Register thegent with manage devkit.

        Adds thegent to the list of tools in manage devkit configuration.
        """
        if not self.manage_config_path:
            return

        if "tools" not in self.manage_config:
            self.manage_config["tools"] = []

        # Import version from thegent
        try:
            from thegent import __version__
        except ImportError:
            __version__ = "0.1.0"

        thegent_entry = {
            "name": "thegent",
            "version": __version__,
            "bin_path": str(get_bin_dir() / "thegent"),
            "config_path": str(get_config_dir()),
            "platform": detect_platform().value,
        }

        # Check if already registered
        existing = [t for t in self.manage_config["tools"] if t.get("name") == "thegent"]

        if not existing:
            self.manage_config["tools"].append(thegent_entry)
            self._save_manage_config()

    def _save_manage_config(self) -> None:
        """Save manage devkit configuration."""
        if not self.manage_config_path:
            return

        try:
            import yaml

            with open(self.manage_config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.manage_config, f, default_flow_style=False)
        except OSError:
            # Save failed, skip
            pass
