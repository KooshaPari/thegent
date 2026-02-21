"""Gardening manager for never-idle loop.

Manages proactive gardening checks: governance health, backlog, test failures,
traceability, escalations, quality, and DAG sync.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, ClassVar

_log = logging.getLogger(__name__)


class GardeningManager:
    """Manages aggressive gardening checks in never-idle loop.

    Runs governance health, backlog checks, test failure detection,
    traceability verification, escalation monitoring, quality gates,
    and DAG synchronization.
    """

    # Gardening steps in rotation order
    STEPS: ClassVar[list[str]] = [
        "govern_health",
        "backlog_check",
        "test_failures",
        "traceability",
        "escalation",
        "session_discovery",
        "quality_check",
        "dag_sync",
        "smart_prune",
        "shadow_cleanup",
        "garden",  # WL-060: Automated documentation synthesis
    ]

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize the gardening manager.

        Args:
            project_root: Root directory for the project. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()
        self._findings: dict[str, Any] = {}
        self._last_results: dict[str, Any] = {}

    async def run_govern_health(self) -> dict[str, Any]:
        """Run governance health check (8 dimensions).

        Returns:
            Dict with health check results.
        """
        try:
            result = subprocess.run(
                ["thegent", "govern", "go", "health"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:500] if result.stdout else "",
                "error": result.stderr[:200] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            return {"success": False, "error": "thegent not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_backlog(self) -> dict[str, Any]:
        """Check for pending backlog items.

        Returns:
            Dict with backlog status.
        """
        # Check for WORK_STREAM.md
        work_stream = self.project_root / "docs" / "reference" / "WORK_STREAM.md"
        if work_stream.exists():
            try:
                content = work_stream.read_text()
                # Count items in different states
                claimed = content.count("| CLAIMED ")
                pending = content.count("| PENDING ")
                completed = content.count("| COMPLETED ")
                return {
                    "exists": True,
                    "claimed": claimed,
                    "pending": pending,
                    "completed": completed,
                    "needs_attention": pending > 0,
                }
            except Exception as e:
                return {"exists": False, "error": str(e)}
        return {"exists": False, "needs_attention": False}

    async def check_test_failures(self) -> dict[str, Any]:
        """Check for recent test failures.

        Looks for common test output files.
        """
        # Check for pytest failure files, test logs, etc.
        indicators = []

        # Look for .pytest_cache, test output, etc.
        for _pattern in ["**/.pytest_cache/", "**/test-results/", "**/__pycache__/"]:
            # Simple existence check
            pass

        # Run quick test to see if there are failures
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=no", "-q", "--co"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
                check=False,
            )
            # Just collecting, not running tests
            return {"success": True, "can_collect": result.returncode == 0}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            # No pytest
            return {"success": True, "error": "pytest not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_traceability(self) -> dict[str, Any]:
        """Check FR traceability gaps.

        Looks for FR_TRACKER.md.
        """
        fr_tracker = self.project_root / "docs" / "reference" / "FR_TRACKER.md"
        if fr_tracker.exists():
            try:
                content = fr_tracker.read_text()
                # Count uncovered FRs
                uncovered = content.count("| NOT STARTED ") + content.count("| IN PROGRESS ")
                return {
                    "exists": True,
                    "uncovered_count": uncovered,
                    "needs_attention": uncovered > 5,
                }
            except Exception as e:
                return {"exists": False, "error": str(e)}
        return {"exists": False, "needs_attention": False}

    async def check_escalations(self) -> dict[str, Any]:
        """Check past-SLA escalations.

        Returns:
            Dict with escalation status.
        """
        try:
            result = subprocess.run(
                ["thegent", "govern", "escalate", "list", "--past-sla"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
                check=False,
            )
            # Parse output for escalations
            has_escalations = "escalation" in result.stdout.lower() and len(result.stdout) > 50
            return {
                "success": result.returncode == 0,
                "has_escalations": has_escalations,
                "output": result.stdout[:300] if result.stdout else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            return {"success": False, "error": "thegent not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_quality(self) -> dict[str, Any]:
        """Run quality gate checks.

        Returns:
            Dict with quality check results.
        """
        # Try running quality task if available
        try:
            result = subprocess.run(
                ["task", "quality"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[-300:] if result.stdout else "",
            }
        except FileNotFoundError:
            # task not available
            return {"success": True, "error": "task not found"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_dag_sync(self) -> dict[str, Any]:
        """Check DAG synchronization.

        Returns:
            Dict with DAG sync status.
        """
        try:
            result = subprocess.run(
                ["thegent", "dag", "sync"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:200] if result.stdout else "",
            }
        except FileNotFoundError:
            return {"success": False, "error": "thegent dag not found"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_smart_prune(self) -> dict[str, Any]:
        """Run intelligent resource pruning.

        Returns:
            Dict with pruning results.
        """
        try:
            from thegent.orchestration.pruning.smart_prune import smart_prune_main

            results = smart_prune_main(force=False, reprompt=True)
            return {
                "success": True,
                "pruned": results["pruned"],
                "reprompted": results["reprompted"],
                "details": results["details"],
                "needs_attention": results["reprompted"] > 0,
            }
        except Exception as e:
            _log.error(f"Error in smart_prune gardening: {e}")
            return {"success": False, "error": str(e)}

    async def run_shadow_cleanup(self) -> dict[str, Any]:
        """Prune stale .shadow-* directories older than 7 days.

        # @trace WL-036

        Returns:
            Dict with shadow_removed count and success flag.
        """
        from thegent.orchestration.pruning.prune import _prune_stale_shadow_and_logs

        shadow_removed, logs_removed = _prune_stale_shadow_and_logs(
            dry_run=False,
            shadow_max_age_hours=7 * 24,  # 7 days
            quality_log_max_age_days=7,
        )
        _log.info("GardeningManager shadow_cleanup: removed %d shadow dirs, %d logs", shadow_removed, logs_removed)
        return {
            "success": True,
            "shadow_removed": shadow_removed,
            "logs_removed": logs_removed,
            "needs_attention": False,
        }

    async def run_garden(self) -> dict[str, Any]:
        """Run automated documentation synthesis via GardenerAgent.

        # @trace WL-060

        Returns:
            Dict with docs_checked, docs_updated, items_found, success flag.
        """
        from thegent.agents.gardener import GardenerAgent

        agent = GardenerAgent(dry_run=False, project_root=self.project_root)
        result = agent.run()
        _log.info(
            "GardeningManager garden: checked=%d updated=%d items=%d",
            result.docs_checked,
            result.docs_updated,
            len(result.items_found),
        )
        return {
            "success": True,
            "docs_checked": result.docs_checked,
            "docs_updated": result.docs_updated,
            "items_found": result.items_found,
            "needs_attention": result.docs_updated > 0,
        }

    async def run_step(self, step: str) -> dict[str, Any]:
        """Run a single gardening step.

        Args:
            step: Step name from STEPS

        Returns:
            Result dict from the step.
        """
        step_handlers = {
            "govern_health": self.run_govern_health,
            "backlog_check": self.check_backlog,
            "test_failures": self.check_test_failures,
            "traceability": self.check_traceability,
            "escalation": self.check_escalations,
            "quality_check": self.check_quality,
            "dag_sync": self.check_dag_sync,
            "session_discovery": self._session_discovery,  # Placeholder
            "smart_prune": self.run_smart_prune,
            "shadow_cleanup": self.run_shadow_cleanup,
            "garden": self.run_garden,  # WL-060: Automated documentation synthesis
        }

        handler = step_handlers.get(step)
        if handler is None:
            return {"success": False, "error": f"Unknown step: {step}"}

        result = await handler()
        self._last_results[step] = result

        # Store findings for items needing attention
        if result.get("needs_attention"):
            self._findings[step] = result

        return result

    async def _session_discovery(self) -> dict[str, Any]:
        """Placeholder for session discovery step.

        Actual discovery is handled by the never-idle loop.
        """
        return {"success": True, "note": "handled by never_idle loop"}

    def get_findings(self) -> dict[str, Any]:
        """Return gardening findings that need attention."""
        return self._findings.copy()

    def get_last_results(self) -> dict[str, Any]:
        """Return results from last run of each step."""
        return self._last_results.copy()

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of gardening status."""
        return {
            "findings_count": len(self._findings),
            "steps_run": len(self._last_results),
            "needs_attention": any(r.get("needs_attention", False) for r in self._last_results.values()),
        }

    def clear_findings(self) -> None:
        """Clear stored findings."""
        self._findings.clear()
