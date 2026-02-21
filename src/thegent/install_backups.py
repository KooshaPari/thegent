"""Backup and restore helpers for shell configuration files."""

from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console


def backup_shell_config(hook_file: Path, console: Console | None = None) -> Path | None:
    """Backup shell config file before modification.

    Returns backup path or None.
    """
    if not hook_file.exists():
        return None

    backup_dir = Path.home() / ".thegent" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{hook_file.name}.{timestamp}.bak"

    try:
        import shutil

        shutil.copy2(hook_file, backup_file)
        if console:
            console.print(f"[dim]Backed up {hook_file.name} to {backup_file}[/dim]")
        return backup_file
    except Exception as e:
        if console:
            console.print(f"[yellow]Could not backup {hook_file.name}: {e}[/yellow]")
        return None


def restore_shell_config(backup_path: Path, console: Console | None = None) -> tuple[bool, str]:
    """Restore shell config from backup.

    Returns (success, message).
    """
    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    backup_name = backup_path.name
    if ".bak" not in backup_name:
        return False, "Invalid backup file format"

    original_name = backup_name.rsplit(".", 2)[0]
    original_path = Path.home() / original_name

    try:
        import shutil

        shutil.copy2(backup_path, original_path)
        if console:
            console.print(f"[green]✓[/green] Restored {original_name} from backup")
        return True, f"Restored {original_name} from {backup_path.name}"
    except Exception as e:
        return False, f"Restore failed: {e}"


def list_backups(console: Console | None = None) -> list[Path]:
    """List all available backups.

    Returns list of backup paths.
    """
    backup_dir = Path.home() / ".thegent" / "backups"
    if not backup_dir.exists():
        return []

    return sorted(backup_dir.glob("*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)


def cleanup_old_backups(keep_count: int = 10, console: Console | None = None) -> tuple[int, list[str]]:
    """Remove old backups, keeping only the most recent ones.

    Returns (removed_count, removed_files).
    """
    backups = list_backups(console)
    if len(backups) <= keep_count:
        return 0, []

    to_remove = backups[keep_count:]
    removed_files: list[str] = []

    def _remove_backup(backup: Path) -> str | None:
        try:
            backup.unlink()
            return backup.name
        except Exception as e:
            if console:
                console.print(f"[yellow]Could not remove {backup.name}: {e}[/yellow]")
            return None

    for backup in to_remove:
        name = _remove_backup(backup)
        if name is not None:
            removed_files.append(name)
            if console:
                console.print(f"[dim]Removed old backup: {name}[/dim]")

    return len(removed_files), removed_files
