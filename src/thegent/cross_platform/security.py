"""Security hardening & compliance."""

import logging
import platform
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class CrossPlatformSecurity:
    """Cross-platform security hardening and compliance."""

    def __init__(self) -> None:
        """Initialize security."""
        self.system = platform.system()
        self.checks: list[dict[str, Any]] = []

    def run_security_check(self, check_name: str = "default") -> dict[str, Any]:
        """Run system security check.

        Args:
            check_name: Name of the check to run

        Returns:
            Security check results
        """
        logger.info(f"Running security check '{check_name}' for {self.system}")

        result = {
            "check": check_name,
            "system": self.system,
            "status": "passed",
            "vulnerabilities": [],
            "recommendations": [],
        }

        # Check file permissions for sensitive files
        sensitive_files = [".env", "config.yaml", "credentials.json"]
        for f in sensitive_files:
            if Path(f).exists():
                # Basic permission check
                self._check_file_permissions(f, result)

        # Check for suspicious processes
        for proc in psutil.process_iter(["name"]):
            self._check_suspicious_process(proc, result)

        self.checks.append(result)
        return result

    def _check_file_permissions(self, f: str, result: dict[str, Any]) -> None:
        """Check file permissions safely."""
        try:
            mode = Path(f).stat().st_mode
            if mode & 0o077:  # Group or world can read/write/exec
                result["status"] = "warn"
                result["vulnerabilities"].append(f"Sensitive file {f} has loose permissions")
                result["recommendations"].append(f"Restrict {f} permissions to owner only")
        except Exception as e:
            logger.error(f"Failed to check {f}: {e}")

    def _check_suspicious_process(self, proc: psutil.Process, result: dict[str, Any]) -> None:
        """Check for suspicious processes safely."""
        try:
            if proc.info["name"] in ["nc", "ncat", "socat"]:
                result["status"] = "warn"
                result["vulnerabilities"].append(f"Suspicious process found: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
            result["status"] = "warn"
            result["vulnerabilities"].append(f"Process inspection failed: {exc!s}")
            result["recommendations"].append("Review process visibility/permissions and rerun security checks")
            logger.warning("Security process inspection failed for pid=%s: %s", proc.pid, exc)

    def harden(self, target: str) -> bool:
        """Harden system or application.

        Args:
            target: Target for hardening

        Returns:
            True if successful
        """
        logger.info(f"Hardening {target} on {self.system}")

        if target == "files":
            # Harden file permissions
            sensitive_files = [".env", "config.yaml", "credentials.json"]
            success = True
            for f in sensitive_files:
                if Path(f).exists():
                    if not self._harden_file(f):
                        success = False
            return success

        return True

    def _harden_file(self, f: str) -> bool:
        """Harden file permissions safely."""
        try:
            if self.system != "Windows":
                Path(f).chmod(0o600)  # Owner read/write only
            # Windows specific hardening would go here
            return True
        except Exception as e:
            logger.error(f"Harden {f} failed: {e}")
            return False
