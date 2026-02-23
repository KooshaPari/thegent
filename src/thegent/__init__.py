"""Thegent - Unified agent orchestration CLI."""

import os
import re
import shutil
import subprocess
import sys

# Python version requirements: CPython 3.14+ or PyPy 3.11+
if sys.implementation.name == "cpython" and sys.version_info < (3, 14):
    raise RuntimeError("thegent requires CPython 3.14+. For PyPy, use PyPy 3.11+")
if sys.implementation.name == "pypy" and sys.version_info < (3, 11):
    raise RuntimeError("thegent requires PyPy 3.11+. For CPython, use 3.14+")


def _get_tool_version(cmd: str) -> tuple[int, ...] | None:
    """Get tool version as tuple of ints, or None if unavailable."""
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Extract version from output like "zig v0.14.0" or "go version go1.24rc1"
        match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", result.stdout + result.stderr)
        if match:
            return tuple(int(x) for x in match.groups() if x)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


# Tool version requirements (beta/rc/canary friendly)
_TOOL_REQUIREMENTS = {
    "rustc": (1, 85),   # Nightly as of Feb 2026
    "zig": (0, 14),     # 0.14.x
    "mojo": (25, 2),    # 25.2.x (nightly)
    "go": (1, 24),      # 1.24rc1+
}


def _check_tool_versions() -> None:
    """Check for required tool versions. Logs warnings but doesn't fail."""
    for tool, required in _TOOL_REQUIREMENTS.items():
        path = shutil.which(tool)
        if not path:
            continue
        version = _get_tool_version(tool)
        if version and version < required:
            os.environ.setdefault("THEGENT_TOOL_WARNINGS", "")
            warn = f"{tool} { '.'.join(map(str, version)) } is old; { '.'.join(map(str, required)) }+ recommended"
            existing = os.environ.get("THEGENT_TOOL_WARNINGS", "")
            os.environ["THEGENT_TOOL_WARNINGS"] = f"{existing}\n{warn}" if existing else warn


# Check tool versions on import (non-blocking)
_check_tool_versions()

__version__ = "0.1.0"
