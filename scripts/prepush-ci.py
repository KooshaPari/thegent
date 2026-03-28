#!/usr/bin/env python3
"""
Phenotype Pre-Push CI Gate

Local quality gate that runs before git push.
Replaces billed GitHub runner checks.

Usage:
    python prepush-ci.py [--all] [--fast]

Options:
    --all    Run all checks (lint, test, type check, security)
    --fast   Skip slow tests (unit only)
    --lint   Run linting only
    --test   Run tests only
    --type   Run type checking only
    --security   Run security checks only
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_command(cmd, cwd=None, description=""):
    """Run a shell command and return success status."""
    print(f"  Running: {description or ' '.join(cmd[:3])}...")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"  {GREEN}✓ PASS{RESET}")
            return True
        else:
            print(f"  {RED}✗ FAIL{RESET}")
            if result.stdout:
                print(result.stdout[:500])
            if result.stderr:
                print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print(f"  {RED}✗ TIMEOUT (>5min){RESET}")
        return False
    except Exception as e:
        print(f"  {RED}✗ ERROR: {e}{RESET}")
        return False


def check_lint():
    """Run linting checks."""
    print(f"\n{YELLOW}[1/4] Linting...{RESET}")
    checks = [
        (["ruff", "check", "."], "ruff check"),
        (["ruff", "format", "--check", "."], "ruff format"),
    ]
    return all(run_command(cmd, description=desc) for cmd, desc in checks)


def check_types():
    """Run type checking."""
    print(f"\n{YELLOW}[2/4] Type Checking...{RESET}")
    # Try pyright first, fall back to mypy
    pyright = shutil.which("pyright") or shutil.which("mypy")
    if pyright:
        return run_command([pyright, "."], description=pyright)
    print("  ⚠ SKIP (no type checker found)")
    return True


def check_tests():
    """Run tests."""
    print(f"\n{YELLOW}[3/4] Testing...{RESET}")
    pytest = shutil.which("pytest")
    if pytest:
        return run_command(
            [pytest, "-v", "--tb=short", "tests/"],
            description="pytest"
        )
    print("  ⚠ SKIP (pytest not found)")
    return True


def check_security():
    """Run security checks."""
    print(f"\n{YELLOW}[4/4] Security...{RESET}")
    checks = [
        (["ruff", "check", ".", "--select=Security"], "security lints"),
    ]
    # Try safety or pip-audit if available
    safety = shutil.which("safety") or shutil.which("pip-audit")
    if safety:
        checks.append(([safety, "check"], safety))
    return all(run_command(cmd, description=desc) for cmd, desc in checks)


def main():
    parser = argparse.ArgumentParser(description="Pre-push CI gate")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--lint", action="store_true", help="Lint only")
    parser.add_argument("--test", action="store_true", help="Test only")
    parser.add_argument("--type", action="store_true", help="Type check only")
    parser.add_argument("--security", action="store_true", help="Security only")
    args = parser.parse_args()

    # If no specific checks, run all
    run_all = args.all or not any([args.lint, args.test, args.type, args.security])

    print(f"{'='*60}")
    print("Phenotype Pre-Push CI Gate")
    print(f"Branch: {os.environ.get('GIT_BRANCH', 'unknown')}")
    print(f"{'='*60}")

    results = []

    if run_all or args.lint:
        results.append(("Lint", check_lint()))

    if run_all or args.type:
        results.append(("Types", check_types()))

    if run_all or args.test:
        results.append(("Tests", check_tests()))

    if run_all or args.security:
        results.append(("Security", check_security()))

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    all_passed = True
    for name, passed in results:
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    print(f"{'='*60}")

    if all_passed:
        print(f"{GREEN}All checks passed! Push approved.{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}Some checks failed. Fix before pushing.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    import shutil
    main()
