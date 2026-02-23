"""Binary discovery helpers for clode."""

import logging
import os
import shutil
from pathlib import Path

_log = logging.getLogger(__name__)


def is_thegent_shim(path: str) -> bool:
    p = Path(path)
    if "thegent-shims" in p.name:
        return True
    try:
        if p.is_symlink() and "thegent-shims" in str(p.readlink()):
            return True
    except OSError as exc:
        _log.warning(
            "shim_resolution_failed",
            extra={
                "path": path,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
    return False


def find_claude(*, require_native: bool = False) -> str | None:
    """Return path to claude CLI, or None. Checks PATH and common install dirs."""
    override = os.environ.get("THGENT_NATIVE_CLAUDE_BIN") if require_native else None
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override).expanduser())
    p = shutil.which("claude")
    if p:
        candidates.append(Path(p))
    for d in (Path("/opt/homebrew/bin"), Path("/usr/local/bin"), Path("~/.bun/bin").expanduser()):
        candidates.append(d / "claude")
    for cand in candidates:
        if cand.is_file() and os.access(cand, os.X_OK):
            if require_native and is_thegent_shim(str(cand)):
                continue
            return str(cand)
    return None
