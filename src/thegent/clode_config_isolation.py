"""Claude config isolation helpers for clode."""

import contextlib
import json
import logging
import shutil
from pathlib import Path
from typing import TypedDict

_LOG = logging.getLogger(__name__)
_WARNING_LIMIT = 3


class SettingsCopyDiagnostics(TypedDict):
    status: str
    error_type: str | None
    error_message: str | None


class CleanupFailure(TypedDict):
    target: str
    failure_type: str
    error_type: str
    error_message: str


class CleanupDiagnostics(TypedDict):
    missing_targets: int
    permission_denied: int
    failure_count: int
    last_failure: CleanupFailure | None


class IsolationDiagnostics(TypedDict):
    settings_copy: SettingsCopyDiagnostics
    cleanup: CleanupDiagnostics


_isolation_diagnostics: IsolationDiagnostics = {
    "settings_copy": {
        "status": "not_attempted",
        "error_type": None,
        "error_message": None,
    },
    "cleanup": {
        "missing_targets": 0,
        "permission_denied": 0,
        "failure_count": 0,
        "last_failure": None,
    },
}
_warning_count = 0


def get_isolation_diagnostics() -> IsolationDiagnostics:
    """Return diagnostics for config isolation setup."""
    raw_settings = _isolation_diagnostics["settings_copy"]
    settings_copy: SettingsCopyDiagnostics = {
        "status": raw_settings["status"],
        "error_type": raw_settings["error_type"],
        "error_message": raw_settings["error_message"],
    }
    raw_cleanup = _isolation_diagnostics["cleanup"]
    cleanup: CleanupDiagnostics = {
        "missing_targets": raw_cleanup["missing_targets"],
        "permission_denied": raw_cleanup["permission_denied"],
        "failure_count": raw_cleanup["failure_count"],
        "last_failure": raw_cleanup["last_failure"],
    }
    return {"settings_copy": settings_copy, "cleanup": cleanup}


def reset_isolation_diagnostics() -> None:
    """Reset diagnostics (test helper)."""
    global _warning_count
    _warning_count = 0
    _isolation_diagnostics["settings_copy"] = {
        "status": "not_attempted",
        "error_type": None,
        "error_message": None,
    }
    _isolation_diagnostics["cleanup"] = {
        "missing_targets": 0,
        "permission_denied": 0,
        "failure_count": 0,
        "last_failure": None,
    }


def _warn_bounded(message: str, *args: object) -> None:
    global _warning_count
    _warning_count += 1
    if _warning_count <= _WARNING_LIMIT:
        _LOG.warning(message, *args)


def ensure_claude_config_isolation(config_dir: Path) -> None:
    """Ensure isolated config dir links to global state and onboarding/session data."""
    global_dir = Path.home() / ".claude"
    global_json = Path.home() / ".claude.json"

    target_json = config_dir / ".claude.json"
    if global_json.exists() and not target_json.exists():
        with contextlib.suppress(OSError):
            target_json.symlink_to(global_json)

    if global_dir.exists():
        target_settings = config_dir / "settings.json"
        if not target_settings.exists():
            global_settings = global_dir / "settings.json"
            if global_settings.exists():
                try:
                    data = json.loads(global_settings.read_text())
                    target_settings.write_text(json.dumps(data, indent=2))
                    _isolation_diagnostics["settings_copy"] = {
                        "status": "copied",
                        "error_type": None,
                        "error_message": None,
                    }
                except json.JSONDecodeError as exc:
                    _isolation_diagnostics["settings_copy"] = {
                        "status": "parse_error",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                    _warn_bounded(
                        "ensure_claude_config_isolation: malformed global settings.json; skipping copy (%s)",
                        type(exc).__name__,
                    )
                except OSError as exc:
                    _isolation_diagnostics["settings_copy"] = {
                        "status": "write_error",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                    _warn_bounded(
                        "ensure_claude_config_isolation: failed writing isolated settings.json (%s)",
                        type(exc).__name__,
                    )

        for item in global_dir.iterdir():
            if item.name == "settings.json":
                continue
            target = config_dir / item.name
            cleanup = _isolation_diagnostics["cleanup"]
            if not target.exists():
                cleanup["missing_targets"] = int(cleanup["missing_targets"]) + 1
            if target.exists() and not target.is_symlink():
                try:
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                except FileNotFoundError:
                    cleanup["missing_targets"] = int(cleanup["missing_targets"]) + 1
                except PermissionError as exc:
                    cleanup["permission_denied"] = int(cleanup["permission_denied"]) + 1
                    cleanup["failure_count"] = int(cleanup["failure_count"]) + 1
                    cleanup["last_failure"] = {
                        "target": str(target),
                        "failure_type": "permission_denied",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                    _warn_bounded(
                        "ensure_claude_config_isolation: cleanup permission denied for %s",
                        target,
                    )
                except OSError as exc:
                    cleanup["failure_count"] = int(cleanup["failure_count"]) + 1
                    cleanup["last_failure"] = {
                        "target": str(target),
                        "failure_type": "cleanup_os_error",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                    }
                    _warn_bounded(
                        "ensure_claude_config_isolation: cleanup failed for %s (%s)",
                        target,
                        type(exc).__name__,
                    )

            if not target.exists():
                with contextlib.suppress(OSError):
                    target.symlink_to(item, target_is_directory=item.is_dir())
