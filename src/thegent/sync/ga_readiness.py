"""GA readiness checklist evaluation for autosync.

# @trace WL-240
"""

from __future__ import annotations

from dataclasses import dataclass

REQUIRED_GA_CHECKS: tuple[str, ...] = (
    "criteria_doc_exists",
    "autosync_enabled",
    "status_artifact_exists",
)


@dataclass(frozen=True)
class GAReadinessResult:
    passed: list[str]
    failed: list[str]

    @property
    def ready(self) -> bool:
        return not self.failed


def evaluate_ga_readiness(checks: dict[str, bool]) -> GAReadinessResult:
    passed: list[str] = []
    failed: list[str] = []
    for check in REQUIRED_GA_CHECKS:
        if checks.get(check, False):
            passed.append(check)
        else:
            failed.append(check)
    return GAReadinessResult(passed=passed, failed=failed)
