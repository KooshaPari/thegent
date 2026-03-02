"""Compatibility wrapper for git lock cleanup domain module."""

from thegent_gitops.lock_cleanup import (  # noqa: F401
    DEFAULT_SCAN_PATHS,
    _find_lock_files,
    _get_lock_mtime_seconds,
    _has_open_holder,
    _lock_cleanup_install_launchd,
    _lock_cleanup_install_systemd,
    _lock_cleanup_plist_path,
    _lock_cleanup_thegent_cmd,
    lock_cleanup_install,
    lock_cleanup_start,
    lock_cleanup_status,
    lock_cleanup_stop,
    lock_cleanup_uninstall,
    run_lock_cleanup,
)

__all__ = [
    "DEFAULT_SCAN_PATHS",
    "_find_lock_files",
    "_get_lock_mtime_seconds",
    "_has_open_holder",
    "_lock_cleanup_install_launchd",
    "_lock_cleanup_install_systemd",
    "_lock_cleanup_plist_path",
    "_lock_cleanup_thegent_cmd",
    "lock_cleanup_install",
    "lock_cleanup_start",
    "lock_cleanup_status",
    "lock_cleanup_stop",
    "lock_cleanup_uninstall",
    "run_lock_cleanup",
]
