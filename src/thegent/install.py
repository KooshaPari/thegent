"""Install module for syncing thegent components to user home directory."""

import os
from pathlib import Path

# Source (thegent) -> Destination mapping
# Note: Only syncing skills/agent-orchestra (unified skill - no redundancy)
CLAUDE_MAPPING = {
    "skills/agent-orchestra": "skills/agent-orchestra",
    "hooks": "hooks",
    "templates": "templates",
    "agents": "agents",
    "commands": "commands",
    "contracts": "contracts",
}

FACTORY_MAPPING = {
    ".factory/hooks": "hooks",
    ".factory/skills": "skills",
    ".factory/commands": "commands",
    ".factory/droids": "droids",
    ".factory/plugins": "plugins",
    ".factory/mcp.json": "mcp.json",
    ".factory/config.json": "config.json",
    ".factory/settings.json": "settings.json",
}

ROOT_FILES = ["CLAUDE.md", "mcp_servers.json", "qa-config.json"]

EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "history.jsonl",
    "session-env",
    "debug",
    "todos",
    "tasks",
    "teams",
    "shell-snapshots",
    "file-history",
    "paste-cache",
}

# Valid targets and modes
VALID_TARGETS = {"claude", "factory", "both"}
VALID_MODES = {"smart", "editable", "force"}


def get_home_dir() -> Path:
    """Get user's home directory.

    Returns:
        Path: The user's home directory.
    """
    return Path.home()


def get_source_dest_mapping(thegent_root: Path, target: str) -> dict[Path, Path]:
    """Get source->dest mapping for target.

    Args:
        thegent_root: Path to the thegent root directory.
        target: Target to install to ("claude", "factory", "both").

    Returns:
        Dict mapping source paths to destination paths.

    Raises:
        ValueError: If target is invalid.
    """
    if target not in VALID_TARGETS:
        raise ValueError(f"Invalid target: {target}. Must be one of: {VALID_TARGETS}")

    mapping: dict[Path, Path] = {}
    home = get_home_dir()

    if target in ("claude", "both"):
        # Add CLAUDE_MAPPING entries
        for src_rel, dest_rel in CLAUDE_MAPPING.items():
            src_path = thegent_root / src_rel
            dest_path = home / ".claude" / dest_rel
            mapping[src_path] = dest_path

        # Add root files for claude
        for filename in ROOT_FILES:
            src_path = thegent_root / filename
            dest_path = home / ".claude" / filename
            mapping[src_path] = dest_path

    if target in ("factory", "both"):
        # Add FACTORY_MAPPING entries
        for src_rel, dest_rel in FACTORY_MAPPING.items():
            src_path = thegent_root / src_rel
            dest_path = home / ".factory" / dest_rel
            mapping[src_path] = dest_path

    return mapping


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded.

    Args:
        path: Path to check.

    Returns:
        bool: True if path should be excluded.
    """
    # Get the name of the path (either file/dir name or the full path)
    path_name = path.name

    # Also check if any part of the path matches exclude patterns
    parts = path.parts

    return path_name in EXCLUDE_DIRS or any(part in EXCLUDE_DIRS for part in parts)


def smart_copy_file(src: Path, dst: Path, verbose: bool = False) -> str:
    """Smart copy (compare mtime).

    Args:
        src: Source file path.
        dst: Destination file path.
        verbose: Whether to print verbose output.

    Returns:
        str: "copied" if file was copied, "skipped" if skipped.
    """
    # Create parent directories if they don't exist
    dst.parent.mkdir(parents=True, exist_ok=True)

    # If destination doesn't exist, copy
    if not dst.exists():
        dst.write_text(src.read_text())
        if verbose:
            print(f"  Copied: {dst}")
        return "copied"

    # Compare modification times
    src_mtime = src.stat().st_mtime
    dst_mtime = dst.stat().st_mtime

    # If source is newer, copy
    if src_mtime > dst_mtime:
        dst.write_text(src.read_text())
        if verbose:
            print(f"  Copied (updated): {dst}")
        return "copied"

    # Otherwise skip
    if verbose:
        print(f"  Skipped: {dst}")
    return "skipped"


def create_symlink(src: Path, dst: Path, verbose: bool = False) -> str:
    """Create symlink.

    Args:
        src: Source file/directory path.
        dst: Destination symlink path.
        verbose: Whether to print verbose output.

    Returns:
        str: "created" if symlink was created, "existed" if already exists.
    """
    # Create parent directories if they don't exist
    dst.parent.mkdir(parents=True, exist_ok=True)

    # If destination already exists, don't recreate
    if dst.exists() or dst.is_symlink():
        return "existed"

    # Create symlink
    dst.symlink_to(src)
    return "created"


def backup_source(src: Path, backup_dir: Path, verbose: bool = False) -> Path:
    """Backup source file to timestamped backup directory.

    Args:
        src: Source file to backup.
        backup_dir: Base directory for backups.
        verbose: Whether to print verbose output.

    Returns:
        Path: Path to the backup file.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = backup_dir / timestamp
    backup_subdir.mkdir(parents=True, exist_ok=True)

    dst = backup_subdir / src.name
    import shutil

    shutil.copy2(src, dst)

    if verbose:
        print(f"  Backed up: {src} -> {dst}")

    return dst


def smart_copy_with_backup(
    src: Path, dst: Path, backup_dir: Path, verbose: bool = False
) -> str:
    """Smart copy with backup on conflict.

    When target is newer (user modified), backup source version and keep target.

    Args:
        src: Source file path.
        dst: Destination file path.
        backup_dir: Directory to store backups.
        verbose: Whether to print verbose output.

    Returns:
        str: "copied" if file was copied, "skipped" if skipped, "conflict" if backed up.
    """
    # Skip directories - we only copy files
    if src.is_dir():
        return "skipped"

    if not src.exists():
        return "skipped"

    dst.parent.mkdir(parents=True, exist_ok=True)

    if not dst.exists():
        dst.write_text(src.read_text())
        return "copied"

    src_mtime = src.stat().st_mtime
    dst_mtime = dst.stat().st_mtime

    if dst_mtime > src_mtime:
        # User modified - backup source, keep target
        backup_source(src, backup_dir, verbose)
        return "conflict"
    else:
        dst.write_text(src.read_text())
        return "copied"


def run_install(
    target: str = "both",
    mode: str = "smart",
    dry_run: bool = False,
    verbose: bool = False,
    backup_dir: Path | None = None,
) -> dict:
    """Main install function.

    Args:
        target: Target to install to ("claude", "factory", "both").
        mode: Install mode ("smart", "editable", "force").
        dry_run: If True, don't make actual changes.
        verbose: If True, print verbose output.
        backup_dir: Directory to store backups on conflicts (smart mode only).

    Returns:
        dict: Dict with counts of copied, skipped, conflicts, errors.
    """
    if target not in VALID_TARGETS:
        raise ValueError(f"Invalid target: {target}. Must be one of: {VALID_TARGETS}")

    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode}. Must be one of: {VALID_MODES}")

    # Default backup directory
    if backup_dir is None:
        backup_dir = get_home_dir() / ".claude" / ".thegent-backup"

    # Get thegent root - use environment variable or detect from project structure
    # First check for THEGENT_ROOT env var
    env_root = os.environ.get("THEGENT_ROOT")
    if env_root:
        thegent_root = Path(env_root).resolve()
    else:
        # Fall back to __file__ path - parent of src/thegent
        thegent_root = Path(__file__).parent.parent.resolve()
        # If we're in a package (editable install), go up further
        # Check if skills/agent-orchestra exists (true thegent root indicator)
        if not (thegent_root / "skills" / "agent-orchestra").exists():
            # Try parent
            potential_root = thegent_root.parent
            if (potential_root / "skills" / "agent-orchestra").exists():
                thegent_root = potential_root

    # Get mapping
    mapping = get_source_dest_mapping(thegent_root, target)

    # Initialize counters
    result = {
        "copied": 0,
        "skipped": 0,
        "conflicts": 0,
        "errors": 0,
    }

    # Process each source->dest pair
    for src, dst in mapping.items():
        try:
            if src.is_dir():
                # Process directory contents recursively
                for src_file in src.rglob("*"):
                    if should_exclude(src_file):
                        continue

                    rel_path = src_file.relative_to(src)
                    dst_file = dst / rel_path

                    if dry_run:
                        if verbose:
                            print(f"Would process: {dst_file}")
                        result["skipped"] += 1  # Count as skipped for dry run
                        continue

                    if mode == "editable":
                        status = create_symlink(src_file, dst_file, verbose=verbose)
                    elif mode == "force":
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        import shutil

                        shutil.copy2(src_file, dst_file)
                        status = "copied"
                        if verbose:
                            print(f"  Copied: {dst_file}")
                    else:  # smart
                        status = smart_copy_with_backup(src_file, dst_file, backup_dir, verbose=verbose)

                    if status == "copied":
                        result["copied"] += 1
                    elif status == "skipped":
                        result["skipped"] += 1
                    elif status == "conflict":
                        result["conflicts"] += 1
                    elif status == "existed" or status == "created":
                        result["copied"] += 1  # Symlink was created/exists
            else:
                # Single file
                if dry_run:
                    if verbose:
                        print(f"Would process: {dst}")
                    result["skipped"] += 1  # Count as skipped for dry run
                    continue

                if mode == "editable":
                    status = create_symlink(src, dst, verbose=verbose)
                elif mode == "force":
                    import shutil

                    shutil.copy2(src, dst)
                    status = "copied"
                    if verbose:
                        print(f"  Copied: {dst}")
                else:  # smart
                    status = smart_copy_with_backup(src, dst, backup_dir, verbose=verbose)

                if status == "copied":
                    result["copied"] += 1
                elif status == "skipped":
                    result["skipped"] += 1
                elif status == "conflict":
                    result["conflicts"] += 1
                elif status == "existed" or status == "created":
                    result["copied"] += 1  # Symlink was created/exists

        except Exception as e:
            if verbose:
                print(f"Error processing {src} -> {dst}: {e}")
            result["errors"] += 1

    return result
