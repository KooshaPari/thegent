"""Claude config isolation helpers for clode."""

import contextlib
import json
import logging
import shutil
from pathlib import Path

_LOG = logging.getLogger(__name__)
_WARNING_LIMIT = 3
_isolation_diagnostics: dict[str, object] = {
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


def get_isolation_diagnostics() -> dict[str, object]:
    """Return diagnostics for config isolation setup."""
    settings_copy = dict(_isolation_diagnostics["settings_copy"])  # type: ignore[arg-type]
    cleanup = dict(_isolation_diagnostics["cleanup"])  # type: ignore[arg-type]
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
            cleanup = _isolation_diagnostics["cleanup"]  # type: ignore[assignment]
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
