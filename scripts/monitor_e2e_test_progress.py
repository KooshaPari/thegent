#!/usr/bin/env python3
"""Monitor E2E test implementation progress.

Tracks which commands have tests and which are still missing.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
COVERAGE_REPORT = PROJECT_ROOT / "docs" / "governance" / "test_coverage_report.json"
TESTS_DIR = PROJECT_ROOT / "tests" / "e2e"


def count_e2e_test_files() -> int:
    """Count E2E test files."""
    if not TESTS_DIR.exists():
        return 0
    return len(list(TESTS_DIR.glob("test_*.py")))


def load_coverage_report() -> dict:
    """Load coverage report."""
    if not COVERAGE_REPORT.exists():
        return {}
    with open(COVERAGE_REPORT) as f:
        return json.load(f)


def main():
    """Print progress summary."""
    report = load_coverage_report()
    test_files = count_e2e_test_files()

    if not report:
        print("⚠️  Coverage report not found. Run: python scripts/analyze_test_coverage.py")
        return

    summary = report.get("summary", {})
    total = summary.get("total_commands", 0)
    with_tests = summary.get("commands_with_e2e_tests", 0)
    without_tests = summary.get("commands_without_e2e_tests", 0)
    coverage_pct = summary.get("coverage_percent", 0)

    print("📊 E2E Test Coverage Progress")
    print("=" * 60)
    print(f"Total CLI Commands: {total}")
    print(f"Commands with E2E Tests: {with_tests} ({coverage_pct:.2f}%)")
    print(f"Commands without E2E Tests: {without_tests}")
    print(f"E2E Test Files: {test_files}")
    print()
    print(f"Progress: {with_tests}/{total} ({coverage_pct:.2f}%)")
    print(f"Remaining: {without_tests} commands")
    print()

    if coverage_pct < 100:
        remaining_pct = 100 - coverage_pct
        print("🎯 Target: 100% coverage")
        print(f"📈 Progress needed: {remaining_pct:.2f}%")

    # Check for new test files
    if test_files > 0:
        print(f"\n✅ Found {test_files} E2E test file(s) in tests/e2e/")


if __name__ == "__main__":
    main()
