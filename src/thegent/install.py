"""Install module for managed installation and synchronization of thegent components.

This module re-exports functions from focused submodules for backwards compatibility.
"""

# Re-export from install_hooks
from thegent.install_hooks import (
    setup_hooks,
    setup_rust_dispatcher,
    setup_harness,
    setup_skills,
    _setup_git_hook,
    _sync_base_dir_skills,
    _sync_cursor_rules,
)

# Re-export from install_system
from thegent.install_system import (
    install_homebrew,
    install_mise,
    verify_mise_installation,
    uninstall_mise_hooks,
    uninstall_system_dependencies,
    clone_git_repo,
    install_system_dependencies,
)

# Re-export from install_wizard
from thegent.install_wizard import (
    run_wizard,
    run_install_project,
    run_install_system,
    run_install,
)

# Re-export from install_mcp
from thegent.install_mcp import (
    _get_mcp_config,
    _update_compatible_mcp_servers,
    configure_mcp_for_client,
)

# Re-export from install_bundles
from thegent.install_bundles import (
    coerce_path as _coerce_path,
    coerce_bundle_items as _coerce_bundle_items,
    get_bundle_manifest_path,
    get_default_bundle_manifest_path,
    list_bundle_names,
    load_bundle_manifest,
    resolve_bundle_mode as _resolve_bundle_mode,
    resolve_bundle_source as _resolve_bundle_source,
    resolve_bundle_target as _resolve_bundle_target,
    source_requires_pin_and_checksum as _source_requires_pin_and_checksum,
    validate_bundle_manifest,
)

# Re-export from install_constants
from thegent.install_constants import (
    CLAUDE_CODE_FILES,
    CLAUDE_MAPPING,
    CURSOR_FILES,
    EXCLUDE_DIRS,
    FACTORY_FILES,
    FACTORY_MAPPING,
    ROOT_FILES,
    SHELL_FILES,
    SHELL_LOCAL_TEMPLATE,
    THEGENT_TOOLS,
    VALID_TARGETS,
    get_targets_for_install,
)

# Re-export from install_models
from thegent.install_models import (
    BundleItem,
    BundleManifest,
    ConfigManifest,
    FileAction,
    FileManifest,
    InstallManifest,
    InstallMode,
)

# Re-export from install_backups
from thegent.install_backups import (
    backup_shell_config as _backup_shell_config,
    cleanup_old_backups,
    list_backups,
    restore_shell_config,
)

# Re-export from install_powershell
from thegent.install_powershell import (
    POWERSHELL_HOOK_SENTINEL as _POWERSHELL_HOOK_SENTINEL,
    POWERSHELL_MISE_HOOK,
    detect_powershell_profile,
    is_powershell_environment as _is_powershell_environment,
    write_powershell_mise_hook,
)

from pathlib import Path


def _get_thegent_root() -> Path:
    """Get the thegent repository root."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def resolve_bundles(thegent_root: Path, target: str = "home", bundle: str = "default", mode: str = "smart") -> list[dict]:
    """Resolve bundles for installation."""
    from thegent.install_bundles import load_bundle_manifest, get_default_bundle_manifest_path
    manifest_path = get_default_bundle_manifest_path(thegent_root)
    manifest = load_bundle_manifest(manifest_path)
    items = []
    for item in manifest.items:
        items.append({"source": str(thegent_root / item.source), "target": item.target, "mode": item.mode or mode})
    return items


def should_exclude(path: Path | str) -> bool:
    """Check if path should be excluded."""
    from thegent.install_constants import EXCLUDE_DIRS
    return any(exc in str(path) for exc in EXCLUDE_DIRS)


def create_symlink(source: Path, target: Path, dry_run: bool = False) -> str:
    """Create a symlink."""
    if dry_run:
        return f"Would link {source} -> {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    target.symlink_to(source)
    return f"Linked {source} -> {target}"


def smart_copy_file(source: Path, target: Path, dry_run: bool = False) -> str:
    """Smart copy a file."""
    import shutil
    if dry_run:
        return f"Would copy {source} -> {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"Copied {source} -> {target}"


def get_source_dest_mapping(thegent_root: Path, bundle: str) -> dict[Path, Path]:
    """Get source to destination mapping."""
    mapping = {}
    for item in resolve_bundles(thegent_root, "home", bundle):
        mapping[Path(item["source"])] = Path.home() / item["target"]
    return mapping


def get_home_dir() -> Path:
    """Get home directory."""
    return Path.home()


def get_manifest_path() -> Path:
    """Get install manifest path."""
    return Path.home() / ".config" / "thegent" / "install_manifest.json"


def get_backup_dir() -> Path:
    """Get backup directory path."""
    return Path.home() / ".config" / "thegent" / "backups"


__all__ = [
    "setup_hooks", "setup_rust_dispatcher", "setup_harness", "setup_skills",
    "install_homebrew", "install_mise", "verify_mise_installation",
    "uninstall_mise_hooks", "uninstall_system_dependencies", "install_system_dependencies",
    "run_wizard", "run_install_project", "run_install_system", "run_install",
    "configure_mcp_for_client",
    "CLAUDE_MAPPING", "FACTORY_MAPPING", "ROOT_FILES", "POWERSHELL_MISE_HOOK",
    "BundleItem", "BundleManifest", "InstallMode",
    "_get_thegent_root", "resolve_bundles", "should_exclude",
    "create_symlink", "smart_copy_file", "get_source_dest_mapping",
    "get_home_dir", "get_manifest_path", "get_backup_dir",
]
