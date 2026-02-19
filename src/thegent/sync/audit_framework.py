"""System audit framework."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SystemAuditFramework:
    """Framework for system audits."""

    def __init__(self):
        """Initialize audit framework."""
        self.checks: list[dict[str, Any]] = []

    def register_check(self, name: str, check_func: callable) -> None:
        """Register an audit check.
        
        Args:
            name: Check name
            check_func: Check function
        """
        self.checks.append({
            "name": name,
            "func": check_func,
        })

    def run_audit(self) -> dict[str, Any]:
        """Run all audit checks.
        
        Returns:
            Audit results
        """
        results = {
            "checks": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }
        
        for check in self.checks:
            try:
                result = check["func"]()
                results["checks"].append({
                    "name": check["name"],
                    "status": result.get("status", "unknown"),
                    "message": result.get("message", ""),
                })
                if result.get("status") == "passed":
                    results["passed"] += 1
                elif result.get("status") == "failed":
                    results["failed"] += 1
                else:
                    results["warnings"] += 1
            except Exception as e:
                logger.error(f"Error running check {check['name']}: {e}")
                results["checks"].append({
                    "name": check["name"],
                    "status": "error",
                    "message": str(e),
                })
                results["failed"] += 1
        
        return results
