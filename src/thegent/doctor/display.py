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
        return True

    passed = all(r.get("status") == "passed" for r in results)

    if verbose:
        for result in results:
            if "details" in result:
                _ = result["details"]

    return passed


def display_fix_report(fix_report: list[dict], dry_run: bool = False) -> None:
    """Display fix report.

    Args:
        fix_report: List of fix results
        dry_run: Whether this was a dry run
    """
    _ = dry_run
    for _fix in fix_report:
        pass
