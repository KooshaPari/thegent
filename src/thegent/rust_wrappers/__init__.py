"""Rust wrapper stubs for CLI entry points.

These are placeholder implementations until the Rust binaries are built.
For now, delegate to the main CLI with appropriate subcommands.
"""

import sys
import subprocess


def droid():
    """Droid agent runner - delegates to thegent CLI."""
    # Import and run thegent with droid subcommand
    sys.exit(subprocess.call(["thegent", "run", "--agent", "droid"] + sys.argv[1:]))


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
