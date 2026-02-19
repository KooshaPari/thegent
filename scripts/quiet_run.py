#!/usr/bin/env python3
"""
Quiet Run Helper

Suppresses common shell noise (rg errors, shell function errors) from command output.
Reduces verbosity and improves clarity.
"""

import subprocess
import sys


def quiet_run(cmd: list[str], filter_patterns: list[str] | None = None, **kwargs) -> subprocess.CompletedProcess:
    """Run command and filter out common noise patterns.

    Args:
        cmd: Command to run
        filter_patterns: Additional patterns to filter (beyond defaults)
        **kwargs: Additional subprocess.run() arguments

    Returns:
        CompletedProcess with filtered output
    """
    # Default noise patterns
    default_patterns = [
        "rg: error parsing flag",
        "_thegent_job_cleanup:",
        "bad math expression",
        "grep config error",
        "unknown encoding",
    ]

    all_patterns = (filter_patterns or []) + default_patterns

    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    # Filter stdout
    if result.stdout:
        lines = result.stdout.split("\n")
        filtered_lines = [line for line in lines if not any(pattern in line for pattern in all_patterns)]
        result.stdout = "\n".join(filtered_lines)

    # Filter stderr
    if result.stderr:
        lines = result.stderr.split("\n")
        filtered_lines = [line for line in lines if not any(pattern in line for pattern in all_patterns)]
        result.stderr = "\n".join(filtered_lines)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/quiet_run.py <command> [args...]")
        sys.exit(1)

    cmd = sys.argv[1:]
    result = quiet_run(cmd)

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    sys.exit(result.returncode)
