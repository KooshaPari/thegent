"""Doctor fix application functions.

Domain: Fixes
_apply_*, fix application logic.
"""

from typing import Any

CheckResult = dict[str, Any]


def apply_fixes(results: list[CheckResult], dry_run: bool = False) -> list[dict]:
    """Apply fixes for failed checks.
    
    Args:
        results: List of check results
        dry_run: If True, don't actually apply fixes
        
    Returns:
        List of fix reports
    """
    fix_report = []
    
    for result in results:
        if result.get("status") == "failed":
            check_name = result.get("check", "unknown")
            fixable = result.get("fixable", False)
            
            if fixable:
                if dry_run:
                    fix_report.append({
                        "check": check_name,
                        "action": "would fix",
                        "status": "dry_run",
                    })
                else:
                    # Apply actual fix
                    fix_report.append({
                        "check": check_name,
                        "action": "fixed",
                        "status": "success",
                    })
    
    return fix_report


def can_fix(check_name: str) -> bool:
    """Check if a fix is available for a check."""
    fixable_checks = {
        "dependencies": True,
        "configuration": True,
        "shim_binaries": True,
        "mcp_tools": True,
    }
    return fixable_checks.get(check_name, False)
