"""Thegent - Unified agent orchestration CLI."""

import os
import re
import shutil
import subprocess
import sys

# Python version requirements: CPython 3.10+ or PyPy 3.10+
_min_cpython = (3, 10)
_min_pypy = (3, 10)

if sys.implementation.name == "cpython" and sys.version_info < _min_cpython:
    raise RuntimeError(f"thegent requires CPython {'.'.join(map(str, _min_cpython))}+. For PyPy, use {'.'.join(map(str, _min_pypy))}+")
if sys.implementation.name == "pypy" and sys.version_info < _min_pypy:
    raise RuntimeError(f"thegent requires PyPy {'.'.join(map(str, _min_pypy))}+. For CPython, use {'.'.join(map(str, _min_cpython))}+")


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

# ---------------------------------------------------------------------------
# Compatibility shim — re-exports from uv workspace packages
#
# This allows code that still does `from thegent import X` to continue
# working while internal modules migrate to direct workspace-package imports.
# Remove each export once all callsites have been updated.
# ---------------------------------------------------------------------------

def __getattr__(name: str):  # noqa: ANN001, ANN202
    """Lazy re-export from workspace sub-packages (PEP 562)."""
    _workspace_map = {
        # thegent-core
        "models": "thegent_core.models",
        "config": "thegent_core.config",
        "exceptions": "thegent_core.exceptions",
        # thegent-execution
        "executor": "thegent_execution.executor",
        # thegent-agents
        "agents": "thegent_agents",
        # thegent-routing
        "routing": "thegent_routing",
        # thegent-planning
        "planning": "thegent_planning",
        # thegent-observability (formerly src/thegent/observability, trace, telemetry,
        #                         metrics, monitoring, logging_utils)
        "observability": "thegent_observability",
        "trace": "thegent_observability.trace",
        "telemetry": "thegent_observability.telemetry",
        "metrics": "thegent_observability.metrics",
        "monitoring": "thegent_observability.monitoring",
        "logging_utils": "thegent_observability.logging_utils",
        # thegent-bench (formerly src/thegent/bench, evals, evaluation, phench)
        "bench": "thegent_bench.bench",
        "evals": "thegent_bench.evals",
        "evaluation": "thegent_bench.evaluation",
        "phench": "thegent_bench.phench",
        # thegent-platform (formerly src/thegent/desktop, gpu, native, tray)
        "desktop": "thegent_platform.desktop",
        "gpu": "thegent_platform.gpu",
        "native": "thegent_platform.native",
        "tray": "thegent_platform.tray",
    }
    if name in _workspace_map:
        import importlib
        return importlib.import_module(_workspace_map[name])
    raise AttributeError(f"module 'thegent' has no attribute {name!r}")


# ---------------------------------------------------------------------------
# sys.modules aliases — required so that `from thegent.X.Y import Z` works.
#
# PEP 562 __getattr__ only fires for attribute access on the module object
# itself.  Subpackage dotted imports (e.g. `from thegent.trace.recorder import
# TraceRecorder`) bypass __getattr__ and go straight to sys.modules, so we
# must register aliases there at import time.
# ---------------------------------------------------------------------------

def _register_subpackage_aliases() -> None:
    import importlib
    import sys

    # Map of  "thegent.<alias>"  →  "<real_package>.<submodule>"
    _subpackage_aliases: dict[str, str] = {
        # thegent-observability
        "thegent.observability": "thegent_observability",
        "thegent.trace": "thegent_observability.trace",
        "thegent.telemetry": "thegent_observability.telemetry",
        "thegent.metrics": "thegent_observability.metrics",
        "thegent.monitoring": "thegent_observability.monitoring",
        "thegent.logging_utils": "thegent_observability.logging_utils",
        # thegent-bench
        "thegent.bench": "thegent_bench.bench",
        "thegent.evals": "thegent_bench.evals",
        "thegent.evaluation": "thegent_bench.evaluation",
        "thegent.phench": "thegent_bench.phench",
        # thegent-platform
        "thegent.desktop": "thegent_platform.desktop",
        "thegent.gpu": "thegent_platform.gpu",
        "thegent.native": "thegent_platform.native",
        "thegent.tray": "thegent_platform.tray",
    }

    for alias, real in _subpackage_aliases.items():
        if alias not in sys.modules:
            try:
                mod = importlib.import_module(real)
                sys.modules[alias] = mod
                # Also register any already-imported children so that
                # `from thegent.trace.recorder import X` resolves the child.
                prefix = real + "."
                for key, child in list(sys.modules.items()):
                    if key.startswith(prefix):
                        suffix = key[len(prefix):]
                        child_alias = alias + "." + suffix
                        sys.modules.setdefault(child_alias, child)
            except ImportError:
                # Workspace package not installed in this environment — skip.
                pass


_register_subpackage_aliases()
