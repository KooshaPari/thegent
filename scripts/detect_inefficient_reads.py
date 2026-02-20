#!/usr/bin/env python3
"""Detect potentially inefficient file reading patterns in the codebase."""

import os
import re
from pathlib import Path

# Patterns to look for
PATTERNS = [
    (re.compile(r"\.read_text\(\)"), "Direct read_text() on Path object without limits"),
    (re.compile(r"\.read_bytes\(\)"), "Direct read_bytes() on Path object without limits"),
    (re.compile(r"open\(.*\)\.read\(\)"), "open().read() without limits"),
]

# Files to ignore
IGNORE_DIRS = {".venv", "node_modules", ".git", "__pycache__", "build", "dist"}


def scan_files(root_dir: str):
    issues_found = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()

                for i, line in enumerate(lines, 1):
                    for pattern, message in PATTERNS:
                        if pattern.search(line):
                            print(f"{file_path}:{i}: {message}")
                            print(f"  > {line.strip()}")
                            issues_found += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return issues_found


if __name__ == "__main__":
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Scanning {root} for inefficient read patterns...")
    count = scan_files(root)
    print(f"\nFound {count} potential issues.")
    print("\nRecommendation: Use read_file_optimized() or read_file_chunk() from thegent.utils.helpers")
