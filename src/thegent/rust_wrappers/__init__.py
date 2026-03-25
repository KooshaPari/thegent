"""Rust wrapper stubs for CLI entry points.

These are standalone stubs that don't import the main thegent package
to avoid version requirements. They delegate to shell commands.
"""

import os
import subprocess
import sys


def _run_thegent(subcommand: str):
    """Run thegent CLI with given subcommand."""
    # Try thegent CLI first, fall back to python
    result = subprocess.run(
        ["thegent"] + subcommand.split(),
        capture_output=False,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    sys.exit(result.returncode)


def droid():
    """Droid agent runner."""
    _run_thegent("run --agent droid")


def clode():
    """Codex agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "clode"] + sys.argv[1:]))


def roid():
    """ROID agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "roid"] + sys.argv[1:]))


def dex():
    """Dex agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "dex"] + sys.argv[1:]))


def anen():
    """Anen agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "anen"] + sys.argv[1:]))


def fanta():
    """Fanta agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "fanta"] + sys.argv[1:]))


def antigma():
    """Antigma agent runner."""
    sys.exit(subprocess.call(["thegent", "run", "--agent", "antigma"] + sys.argv[1:]))


if __name__ == "__main__":
    droid()
