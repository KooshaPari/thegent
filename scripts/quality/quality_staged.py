#!/usr/bin/env python3
"""quality:staged - Run quality checks on staged files only."""
import subprocess
import sys
from pathlib import Path

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [Path(f) for f in result.stdout.strip().split("\n") if f and f.endswith(".py") and Path(f).exists()]

def run_ruff(files, fix=False):
    if not files: return True
    cmd = ["ruff", "check", *(["--fix"] if fix else []), *[str(f) for f in files]]
    return subprocess.run(cmd).returncode == 0

def run_format(files, check=True):
    if not files: return True
    cmd = ["ruff", "format", *(["--check"] if check else []), *[str(f) for f in files]]
    return subprocess.run(cmd).returncode == 0

def main():
    fix = "--fix" in sys.argv
    files = get_staged_files()
    if not files:
        print("No staged Python files to check.")
        return 0
    
    print(f"Checking {len(files)} staged file(s)...")
    
    ok = True
    print("1. Ruff lint...", end=" ")
    ok &= run_ruff(files, fix)
    print("✓" if ok else "✗")
    
    print("2. Ruff format...", end=" ")
    ok &= run_format(files)
    print("✓" if ok else "✗")
    
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
