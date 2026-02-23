"""Symptom-to-fix matrix for autosync troubleshooting and diagnostics.

This module provides structured access to the symptom-to-fix mapping that guides
operators in diagnosing and resolving common autosync issues.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SymptomEntry:
    """A single symptom-to-fix mapping entry.

    Attributes:
        symptom: Description of the observed symptom.
        cause: Likely root cause.
        diagnostic_cmd: Command to run for diagnosis.
        fix_cmd: Command to run to resolve the issue.
        reference: Path or URL to reference documentation.
    """

    symptom: str
    cause: str
    diagnostic_cmd: str
    fix_cmd: str
    reference: str


def get_symptom_matrix() -> list[SymptomEntry]:
    """Get the complete symptom-to-fix matrix.

    Returns:
        List of SymptomEntry objects covering common autosync issues.
    """
    return [
        SymptomEntry(
            symptom="Drift detected in sync",
            cause="Schema mismatch or stale mapping",
            diagnostic_cmd="thegent autosync drift-check <connector>",
            fix_cmd="thegent autosync remap <connector>",
            reference="docs/guides/AUTOSYNC_CONFLICT_RESOLUTION.md",
        ),
        SymptomEntry(
            symptom="Conflict queue full, sync blocked",
            cause="Too many unresolved conflicts",
            diagnostic_cmd="thegent autosync conflicts-list <connector>",
            fix_cmd="thegent autosync resolve-conflicts <connector> --auto",
            reference="docs/guides/AUTOSYNC_CONFLICT_RESOLUTION.md",
        ),
        SymptomEntry(
            symptom="Auth token expired, 401 errors",
            cause="OAuth token expired or revoked",
            diagnostic_cmd="thegent autosync auth-status <connector>",
            fix_cmd="thegent autosync refresh-auth <connector>",
            reference="docs/guides/AUTOSYNC_AUTH_TROUBLESHOOTING.md",
        ),
        SymptomEntry(
            symptom="Rate limit hit, backoff active",
            cause="Connector rate limit exhausted",
            diagnostic_cmd="thegent autosync quota-status <connector>",
            fix_cmd="thegent autosync backoff --reset <connector>",
            reference="docs/guides/AUTOSYNC_RATE_LIMITING.md",
        ),
        SymptomEntry(
            symptom="Sync stuck, no progress",
            cause="Process deadlocked or hung",
            diagnostic_cmd="thegent autosync status <connector> --verbose",
            fix_cmd="thegent autosync restart <connector>",
            reference="docs/guides/AUTOSYNC_LIFECYCLE.md",
        ),
        SymptomEntry(
            symptom="Board ID collision, write rejected",
            cause="Duplicate board ID assignment",
            diagnostic_cmd="thegent autosync board-ids <connector> --check-dups",
            fix_cmd="thegent autosync reindex-boards <connector>",
            reference="docs/guides/AUTOSYNC_BOARD_MANAGEMENT.md",
        ),
        SymptomEntry(
            symptom="Startup validation failed",
            cause="Connector not ready or misconfigured",
            diagnostic_cmd="thegent autosync startup-validate <connector>",
            fix_cmd="thegent autosync configure <connector> --interactive",
            reference="docs/guides/AUTOSYNC_STARTUP.md",
        ),
        SymptomEntry(
            symptom="Rollback needed, revert state",
            cause="Production issue, need to recover",
            diagnostic_cmd="thegent autosync snapshots list <connector>",
            fix_cmd="thegent autosync rollback <connector> <snapshot-id>",
            reference="docs/guides/AUTOSYNC_ROLLBACK.md",
        ),
        SymptomEntry(
            symptom="Mapping stale, schema evolved",
            cause="Connector schema changed upstream",
            diagnostic_cmd="thegent autosync schema-diff <connector>",
            fix_cmd="thegent autosync schema-sync <connector>",
            reference="docs/guides/AUTOSYNC_SCHEMA_EVOLUTION.md",
        ),
        SymptomEntry(
            symptom="Writer lock held, writes blocked",
            cause="Another process holds write lock",
            diagnostic_cmd="thegent autosync lock-status <connector>",
            fix_cmd="thegent autosync lock-release <connector> --force",
            reference="docs/guides/AUTOSYNC_LOCKING.md",
        ),
    ]


def find_by_keyword(keyword: str) -> list[SymptomEntry]:
    """Find symptom entries by keyword (case-insensitive).

    Searches both symptom and cause fields.

    Args:
        keyword: Keyword to search for.

    Returns:
        List of SymptomEntry objects matching the keyword.
    """
    keyword_lower = keyword.lower()
    matrix = get_symptom_matrix()
    return [entry for entry in matrix if keyword_lower in entry.symptom.lower() or keyword_lower in entry.cause.lower()]
