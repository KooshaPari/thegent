"""Immutable audit trail and query interface (WP-3004, FR-012).

Hardening (AUDIT-N+54 — SOTA pass-38)
--------------------------------------
Contract surface asserted by
``tests/test_unit_audit_n54_audit_hardening.py``
(``FR-GOV-AU-001..015``).

# @trace AUDIT-N+54
"""

from __future__ import annotations

from pathlib import Path

from thegent.execution import Auditor, RunRegistry


def _require_absolute(session_dir: Path) -> Path:
    session_dir = Path(session_dir)
    if not session_dir.is_absolute():
        raise ValueError(f"session_dir must be an absolute path (got {session_dir!s})")
    return session_dir


def verify_chain(session_dir: Path) -> dict[str, object]:
    """Verify hash chain integrity of the run registry.

    ``FR-GOV-AU-001`` .. ``FR-GOV-AU-003``.
    """
    session_dir = _require_absolute(session_dir)
    registry_path = session_dir / "run_registry.jsonl"
    auditor = Auditor(registry_path)
    return auditor.verify_registry()


def query_events(
    session_dir: Path,
    run_id: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
) -> list[dict[str, object]]:
    """Query audit events from the registry.

    ``FR-GOV-AU-004`` .. ``FR-GOV-AU-012``.
    """
    session_dir = _require_absolute(session_dir)
    if limit <= 0:
        raise ValueError(f"limit must be > 0 (got {limit})")

    registry = RunRegistry(session_dir)
    runs = registry.list_runs(limit=limit * 2)
    events: list[dict[str, object]] = []
    for r in runs:
        if run_id and r.get("run_id") != run_id:
            continue
        ev = r.get("event") or "start"
        if event_type and ev != event_type:
            continue
        events.append(r)
        if len(events) >= limit:
            break
    return events


__all__ = [
    "query_events",
    "verify_chain",
]
