"""Install manager for thegent.

Handles file installation, backup, and uninstallation.
Extracted from install.py for maintainability.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from rich.prompt import Prompt

from thegent.infra import copy_file, copy_tree
from thegent.install_models import ConfigManifest, FileManifest, InstallManifest, InstallMode

if TYPE_CHECKING:
    pass


def get_home_dir() -> Path:
    """Get the home directory."""
    return Path.home()


def get_manifest_path() -> Path:
    """Get the path to the install manifest."""
    return get_home_dir() / ".thegent" / "install-manifest.json"


def get_backup_dir() -> Path:
    """Get the path to the backup directory."""
    return get_home_dir() / ".thegent" / "backups"


class InstallManager:
    """Manages installation, backup, and uninstallation of thegent files.
    
    Attributes:
        dry_run: If True, don't make actual changes
        verbose: If True, print detailed output
        manifest_path: Path to the install manifest
        backup_dir: Directory for backups
        manifest: Current install manifest
    """
    
    def __init__(self, dry_run: bool = False, verbose: bool = False) -> None:
        """Initialize the install manager.
        
        Args:
            dry_run: If True, don't make actual changes
            verbose: If True, print detailed output
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.manifest_path = get_manifest_path()
        self.backup_dir = get_backup_dir()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> InstallManifest:
        """Load the install manifest from disk.
        
        Returns:
            InstallManifest object
        """
        if self.manifest_path.exists():
            try:
                return InstallManifest.model_validate_json(
                    self.manifest_path.read_text()
                )
            except (json.JSONDecodeError, ValueError):
                return InstallManifest()
        return InstallManifest()

    def save_manifest(self) -> None:
        """Save the manifest to disk."""
        if not self.dry_run:
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            self.manifest_path.write_text(
                self.manifest.model_dump_json(indent=2)
            )

    def _backup_file(self, target: Path) -> Path | None:
        """Create a backup of a file.
        
        Args:
            target: File to backup
            
        Returns:
            Path to backup or None if file doesn't exist
        """
        if not target.exists():
            return None
        
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        
        if target.is_relative_to(Path.home()):
            rel_path = target.relative_to(Path.home())
        else:
            rel_path = Path(target.name)
        
        backup_path = self.backup_dir / timestamp / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        copy_file(target, backup_path)
        
        return backup_path

    def install_file(
        self,
        source: Path,
        target: Path,
        mode: InstallMode,
    ) -> FileAction:
        """Install a file from source to target.
        
        Args:
            source: Source file path
            target: Target file path
            mode: Installation mode
            
        Returns:
            FileAction indicating what was done
        """
        if not source.exists():
            return FileAction.ERROR

        target.parent.mkdir(parents=True, exist_ok=True)

        # Handle existing target
        if target.exists() or target.is_symlink():
            action = self._handle_conflict(source, target, mode)
            if action is not None:
                return action

        # Perform the installation
        return self._perform_install(source, target, mode)

    def _handle_conflict(
        self,
        source: Path,
        target: Path,
        mode: InstallMode,
    ) -> FileAction | None:
        """Handle a conflict when target already exists.
        
        Args:
            source: Source file path
            target: Target file path
            mode: Installation mode
            
        Returns:
            FileAction if conflict was handled, None to proceed
        """
        if mode == InstallMode.FORCE:
            return None  # Proceed to overwrite
        
        if mode == InstallMode.EDITABLE:
            return None  # Proceed to symlink
        
        if mode == InstallMode.SMART:
            src_mtime = source.stat().st_mtime
            dst_mtime = target.stat().st_mtime
            if dst_mtime >= src_mtime:
                if self.verbose:
                    sys.stdout.write(
                        f"  Skipped (up to date): {target}\n"
                    )
                return FileAction.SKIPPED
        
        if mode == InstallMode.INTERACTIVE:
            return self._interactive_conflict(target)
        
        return None

    def _interactive_conflict(self, target: Path) -> FileAction | None:
        """Handle conflict interactively.
        
        Args:
            target: Target file path
            
        Returns:
            FileAction if conflict was handled, None to proceed
        """
        if not sys.stdin.isatty():
            if self.verbose:
                sys.stderr.write(
                    f"  Non-interactive, skipping: {target}\n"
                )
            return FileAction.CONFLICT

        choice = Prompt.ask(
            f"Conflict for {target}. [o]verwrite, [s]kip, [b]ackup?",
            choices=["o", "s", "b"],
            default="s",
        )
        
        if choice == "s":
            return FileAction.SKIPPED
        
        return None  # Proceed with backup or overwrite

    def _perform_install(
        self,
        source: Path,
        target: Path,
        mode: InstallMode,
    ) -> FileAction:
        """Perform the actual file installation.
        
        Args:
            source: Source file path
            target: Target file path
            mode: Installation mode
            
        Returns:
            FileAction indicating what was done
        """
        backup_path = None
        
        if not self.dry_run:
            # Backup and remove existing
            if target.exists() or target.is_symlink():
                backup_path = self._backup_file(target)
                if target.is_symlink() or target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)

            # Install
            if mode == InstallMode.EDITABLE:
                target.symlink_to(source)
                action = FileAction.SYMLINKED
            else:
                if source.is_dir():
                    copy_tree(source, target)
                else:
                    copy_file(source, target)
                action = FileAction.COPIED

            # Update manifest
            self.manifest.files[str(target)] = FileManifest(
                source=str(source),
                target=str(target),
                mode="symlink" if mode == InstallMode.EDITABLE else "copy",
                mtime=target.stat().st_mtime if target.exists() else 0,
                backup=str(backup_path) if backup_path else None,
            )
        else:
            action = (
                FileAction.SYMLINKED
                if mode == InstallMode.EDITABLE
                else FileAction.COPIED
            )
            if self.verbose:
                mode_str = "symlink" if mode == InstallMode.EDITABLE else "copy"
                sys.stdout.write(f"  Would {mode_str}: {target}\n")

        return cast("FileAction", action)

    def update_config(
        self,
        config_path: Path,
        key_path: str,
        value: Any,
    ) -> bool:
        """Update a JSON config file at a specific key path.
        
        Args:
            config_path: Path to the config file
            key_path: Dot-separated key path (e.g., 'mcpServers.thegent')
            value: Value to set
            
        Returns:
            True if successful
        """
        if self.dry_run:
            if self.verbose:
                sys.stdout.write(
                    f"  Would update {config_path}: {key_path}\n"
                )
            return True

        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
            except Exception:
                config = {}
        else:
            config = {}

        # Navigate to key and set value
        parts = key_path.split(".")
        curr = config
        original_value = None
        
        for part in parts[:-1]:
            if part not in curr:
                curr[part] = {}
            curr = curr[part]

        if parts[-1] in curr:
            original_value = curr[parts[-1]]

        curr[parts[-1]] = value

        # Write config
        config_path.write_text(json.dumps(config, indent=2))

        # Update manifest
        self.manifest.configs.append(
            ConfigManifest(
                file_path=str(config_path),
                key=key_path,
                original_value=original_value,
                new_value=value,
            )
        )
        
        return True

    def uninstall(self) -> dict[str, int]:
        """Uninstall all managed files and revert configs.
        
        Returns:
            Dict with counts: removed, restored, reverted, errors
        """
        counts = {
            "removed": 0,
            "restored": 0,
            "reverted": 0,
            "errors": 0,
        }

        # Revert configs in reverse order
        for cfg in reversed(self.manifest.configs):
            if not self._revert_config(cfg):
                counts["errors"] += 1
            else:
                counts["reverted"] += 1

        # Remove files and restore backups
        for target_str, m in list(self.manifest.files.items()):
            result = self._remove_file(target_str, m)
            counts[result] += 1

        self.save_manifest()
        return counts

    def _revert_config(self, cfg: ConfigManifest) -> bool:
        """Revert a config change.
        
        Args:
            cfg: Config manifest entry
            
        Returns:
            True if successful
        """
        path = Path(cfg.file_path)
        if not path.exists():
            return True
        
        try:
            data = json.loads(path.read_text())
            parts = cfg.key.split(".")
            curr = data
            
            for part in parts[:-1]:
                curr = curr.get(part, {})

            if cfg.original_value is None:
                if parts[-1] in curr:
                    del curr[parts[-1]]
            else:
                curr[parts[-1]] = cfg.original_value

            if not self.dry_run:
                path.write_text(json.dumps(data, indent=2))
            
            return True
        except Exception:
            return False

    def _remove_file(
        self,
        target_str: str,
        m: FileManifest,
    ) -> str:
        """Remove a file and optionally restore backup.
        
        Args:
            target_str: Target file path string
            m: File manifest entry
            
        Returns:
            Result key: 'removed', 'restored', or 'errors'
        """
        target = Path(target_str)
        
        if not target.exists() and not target.is_symlink():
            return "removed"

        try:
            if not self.dry_run:
                if target.is_symlink() or target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)

                # Restore backup if available
                if m.backup and Path(m.backup).exists():
                    backup = Path(m.backup)
                    if backup.is_dir():
                        copy_tree(backup, target)
                    else:
                        copy_file(backup, target)
                    del self.manifest.files[target_str]
                    return "restored"

                del self.manifest.files[target_str]
            
            return "removed"
        except Exception:
            return "errors"


__all__ = [
    "InstallManager",
    "get_home_dir",
    "get_manifest_path",
    "get_backup_dir",
]
