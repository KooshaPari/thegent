"""Doctor display and reporting functions.

Domain: Display
_display_*, report generation.
"""

from typing import Any

CheckResult = dict[str, Any]


def display_results(results: list[CheckResult], verbose: bool = False) -> bool:
    """Display check results.
    
    Args:
        results: List of check results
        verbose: Verbose output
        
    Returns:
        True if all checks passed
    """
    if not results:
        print("No checks to display")
        return True

    passed = all(r.get("status") == "passed" for r in results)

    for result in results:
        status = result.get("status", "unknown")
        check = result.get("check", "unknown")

        if status == "passed":
            prefix = "✓"
        elif status == "failed":
            prefix = "✗"
        else:
            prefix = "?"

        print(f"{prefix} {check}: {status}")

        if verbose and "details" in result:
            print(f"  {result['details']}")

    return passed


def display_fix_report(fix_report: list[dict], dry_run: bool = False) -> None:
    """Display fix report.
    
    Args:
        fix_report: List of fix results
        dry_run: Whether this was a dry run
    """
    mode = "Would fix" if dry_run else "Fixed"

    for fix in fix_report:
        check = fix.get("check", "unknown")
        status = fix.get("status", "unknown")

        print(f"{mode}: {check} -> {status}")
